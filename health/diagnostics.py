import hashlib
import json
import os
import re
import socket
import sqlite3
import subprocess
from datetime import datetime, timezone

DATABASE_FILE = os.environ.get(
    "BARGAZBOT_DB",
    "/home/devon/Bargaz/BargazBot/databases/bargazbot.db"
)
BACKUP_DIR = os.environ.get(
    "BARGAZBOT_BACKUP_DIR",
    os.path.join(os.path.dirname(DATABASE_FILE), "backups")
)
BACKUP_MAX_AGE = {
    "hourly": 2 * 3600,
    "daily": 26 * 3600,
    "weekly": 8 * 86400
}
ERROR_PATTERNS = {
    "filesystem_error": re.compile(
        r"EXT4-fs (?:error|warning)|"
        r"structure needs cleaning|"
        r"filesystem.*(?:corrupt|aborted)|"
        r"aborting journal",
        re.IGNORECASE
    ),
    "storage_io_error": re.compile(
        r"I/O error|"
        r"buffer I/O|"
        r"mmc[0-9].*(?:error|timeout|timed out)|"
        r"blk_update_request.*error",
        re.IGNORECASE
    ),
    "read_only_filesystem": re.compile(
        r"remounting filesystem read-only|"
        r"remounting filesystem read only",
        re.IGNORECASE
    )
}
REPO_DIR   = os.environ.get("BARGAZ_REPO_DIR", "/home/devon/Bargaz")
COMPONENTS = {
    "bargaz": REPO_DIR,
    "bargazbot": os.path.join(REPO_DIR, "BargazBot"),
    "bargazlive": os.path.join(REPO_DIR, "BargazLive")
}
INSTALLED_HEALTH_DIR = "/opt/bargaz-system/health"
HEALTH_FILES         = ["diagnostics.py", "health_server.py"]

def run_check(command):
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=10,
            check=False
        )
        return result.returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return False


def check_kernel():
    detected = set()
    try:
        result = subprocess.run(
            [
                "journalctl", "-k", "-b",
                "-n", "5000",
                "--no-pager",
                "--quiet",
                "--output=cat"
            ],
            capture_output=True,
            text=True,
            timeout=10,
            check=False
        )

        if result.returncode != 0 or not result.stdout.strip():
            return False, detected

        for name, pattern in ERROR_PATTERNS.items():
            if pattern.search(result.stdout):
                detected.add(name)

        return True, detected

    except (OSError, subprocess.TimeoutExpired):
        return False, detected

def check_backups():
    result = {
        "directory": BACKUP_DIR,
        "present": os.path.isdir(BACKUP_DIR),
        "types": {}
    }

    if not result["present"]:
        return result

    try:
        names = os.listdir(BACKUP_DIR)
    except OSError:
        return result

    now = datetime.now(timezone.utc).timestamp()

    for backup_type, max_age in BACKUP_MAX_AGE.items():
        newest = None

        for name in names:
            if not name.startswith(f"{backup_type}_"):
                continue

            if not name.endswith(".db"):
                continue

            path = os.path.join(BACKUP_DIR, name)

            try:
                modified = os.path.getmtime(path)
                size = os.path.getsize(path)
            except OSError:
                continue

            if newest is None or modified > newest["modified"]:
                newest = {
                    "name": name,
                    "modified": modified,
                    "size_bytes": size
                }

        if newest is None:
            result["types"][backup_type] = {
                "name": None,
                "age_seconds": None,
                "size_bytes": None,
                "stale": True
            }
            continue

        age = max(0, int(now - newest["modified"]))

        result["types"][backup_type] = {
            "name": newest["name"],
            "age_seconds": age,
            "size_bytes": newest["size_bytes"],
            "stale": age > max_age
        }

    return result


def backup_is_fresh(backups, backup_type):
    entry = backups["types"].get(backup_type)

    return bool(entry) and entry["stale"] is False


def has_internet():
    try:
        with socket.create_connection(("1.1.1.1", 53), timeout=3):
            return True
    except OSError:
        return False


def wifi_signal(interface):
    try:
        result = subprocess.run(
            ["iw", "dev", interface, "link"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False
        )
    except (OSError, subprocess.TimeoutExpired):
        return None

    match = re.search(r"signal:\s*(-?\d+)", result.stdout)

    return int(match.group(1)) if match else None


def check_network():
    interfaces = []

    try:
        names = sorted(os.listdir("/sys/class/net"))
    except OSError:
        names = []

    for name in names:
        if name == "lo":
            continue

        try:
            with open(f"/sys/class/net/{name}/operstate") as handle:
                state = handle.read().strip()
        except OSError:
            continue

        interfaces.append({
            "name": name,
            "state": state,
            "wireless": os.path.isdir(
                f"/sys/class/net/{name}/wireless"
            )
        })

    virtual = re.compile(r"^(tailscale|tun|tap|docker|veth|br-|wg)")

    ethernet = next((
        item for item in interfaces
        if not item["wireless"]
        and item["state"] == "up"
        and not virtual.match(item["name"])
    ), None)

    wifi = next((
        item for item in interfaces
        if item["wireless"] and item["state"] == "up"
    ), None)

    if ethernet:
        connection = "ethernet"
    elif wifi:
        connection = "wifi"
    else:
        connection = "disconnected"

    return {
        "connection": connection,
        "connected": has_internet(),
        "signal_dbm": wifi_signal(wifi["name"]) if wifi else None,
        "interfaces": interfaces,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

def check_database():
    result = {
        "path": DATABASE_FILE,
        "present": os.path.isfile(DATABASE_FILE),
        "readable": False,
        "writable_directory": False,
        "quick_check": False
    }

    if not result["present"]:
        return result

    result["readable"] = os.access(DATABASE_FILE, os.R_OK)
    result["writable_directory"] = os.access(
        os.path.dirname(DATABASE_FILE),
        os.W_OK
    )

    try:
        with sqlite3.connect(f"file:{DATABASE_FILE}?mode=ro", uri=True) as database:
            result["quick_check"] = (
                database.execute("PRAGMA quick_check").fetchone() == ("ok",)
            )
    except sqlite3.Error:
        result["quick_check"] = False

    return result


def filesystem_is_read_only():
    try:
        with open("/proc/mounts", encoding="utf-8") as handle:
            for line in handle:
                fields = line.split()

                if len(fields) < 4 or fields[1] != "/":
                    continue

                return "ro" in fields[3].split(",")
    except OSError:
        pass

    return None


def run_git(component_dir, arguments):
    try:
        result = subprocess.run(
            ["git", "-C", component_dir] + arguments,
            capture_output=True,
            text=True,
            timeout=10,
            check=False
        )
        if result.returncode != 0:
            return None
        return result.stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        return None


def read_version(component_dir):
    try:
        with open(
            os.path.join(component_dir, "package.json"),
            encoding="utf-8"
        ) as handle:
            return json.load(handle).get("version")
    except (OSError, ValueError):
        return None


def file_checksum(path):
    digest = hashlib.sha256()

    try:
        with open(path, "rb") as handle:
            for chunk in iter(lambda: handle.read(65536), b""):
                digest.update(chunk)
    except OSError:
        return None

    return digest.hexdigest()


def check_installed_copy():
    mismatched = []

    for name in HEALTH_FILES:
        source = file_checksum(os.path.join(REPO_DIR, "health", name))
        installed = file_checksum(
            os.path.join(INSTALLED_HEALTH_DIR, name)
        )

        if source is None or installed is None or source != installed:
            mismatched.append(name)

    return {
        "in_sync": not mismatched,
        "mismatched_files": mismatched
    }


def get_versions():
    components = {}

    for name, component_dir in COMPONENTS.items():
        commit = run_git(component_dir, ["rev-parse", "--short", "HEAD"])
        status = run_git(component_dir, ["status", "--porcelain"])

        components[name] = {
            "version": read_version(component_dir),
            "commit": commit or None,
            "uncommitted_changes": None if status is None else bool(status)
        }

    return {
        "components": components,
        "installed_health_files": check_installed_copy(),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

def get_diagnostics():
    kernel_logs_ok, storage_errors = check_kernel()
    database = check_database()
    backups = check_backups()
    network = check_network()
    checks = {
        "node": run_check(["node", "--version"]),
        "npm": run_check(["npm", "--version"]),
        "nano": run_check(["nano", "--version"]),
        "pm2_service": run_check([
            "systemctl", "is-active", "--quiet", "pm2-devon.service"
        ]),
        "sqlite": database["quick_check"],
        "kernel_logs": kernel_logs_ok,
        "database_present": database["present"],
        "database_writable": database["writable_directory"],
        "filesystem_writable": filesystem_is_read_only() is not True,
        "backup_hourly": backup_is_fresh(backups, "hourly"),
        "backup_daily": backup_is_fresh(backups, "daily"),
        "backup_weekly": backup_is_fresh(backups, "weekly")
    }

    storage = {
        "available_bytes": None,
        "available_inodes": None,
        "low_space": None,
        "low_inodes": None
    }

    try:
        disk = os.statvfs("/")
        available = disk.f_bavail * disk.f_frsize
        total = disk.f_blocks * disk.f_frsize

        storage.update({
            "available_bytes": available,
            "available_inodes": disk.f_favail,
            "low_space": (
                available < 1024 ** 3
                or (total > 0 and available / total < 0.1)
            ),
            "low_inodes": (
                disk.f_files > 0
                and disk.f_favail / disk.f_files < 0.1
            )
        })
    except OSError:
        pass

    degraded = (
        not all(checks.values())
        or storage["low_space"] is not False
        or storage["low_inodes"] is not False
        or bool(storage_errors)
    )

    return {
        "status": "degraded" if degraded else "online",
        "checks": checks,
        "storage": storage,
        "storage_errors": sorted(storage_errors),
        "database": database,
        "versions": get_versions(),
        "backups": backups,
        "network": network,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
