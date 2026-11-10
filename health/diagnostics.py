import os
import re
import shutil
import sqlite3
import subprocess
from datetime import datetime, timezone

detected_storage_errors = set()

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
            return False

        for name, pattern in ERROR_PATTERNS.items():
            if pattern.search(result.stdout):
                detected_storage_errors.add(name)

        return True

    except (OSError, subprocess.TimeoutExpired):
        return False


def get_diagnostics():
    checks = {
        "node": run_check(["node", "--version"]),
        "npm": run_check(["npm", "--version"]),
        "nano": run_check(["nano", "--version"]),
        "pm2_service": run_check([
            "systemctl", "is-active", "--quiet", "pm2-devon.service"
        ]),
        "sqlite": False,
        "kernel_logs": check_kernel()
    }

    try:
        with sqlite3.connect(":memory:") as database:
            checks["sqlite"] = (
                database.execute("PRAGMA integrity_check").fetchone()
                == ("ok",)
            )
    except sqlite3.Error:
        pass

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
        or bool(detected_storage_errors)
    )

    return {
        "status": "degraded" if degraded else "online",
        "checks": checks,
        "storage": storage,
        "storage_errors": sorted(detected_storage_errors),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }