#!/usr/bin/env python3

from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime, timezone
from diagnostics import get_diagnostics
import json
import os
import threading
import time

HOST = os.environ.get("HEALTH_HOST", "127.0.0.1")
PORT = int(os.environ.get("HEALTH_PORT", "3001"))

UPS_STATUS_FILE = os.environ.get(
    "UPS_STATUS_FILE",
    "/home/devon/ups/ups_status.json"
)

SHUTDOWN_REQUEST_FILE = os.environ.get(
    "SHUTDOWN_REQUEST_FILE",
    "/home/devon/ups/shutdown_request.json"
)

def get_health():
    result = {
        "status": "online",
        "power_source": "unknown",
        "battery_percent": None,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    if not os.path.exists(UPS_STATUS_FILE):
        result["status"] = "degraded"
    else:
        try:
            with open(UPS_STATUS_FILE, "r") as f:
                ups = json.load(f)

            updated = datetime.fromisoformat(ups["timestamp"])
            age = (
                datetime.now(timezone.utc) - updated
            ).total_seconds()

            if age > 30 or age < -30:
                result["status"] = "degraded"

            result["power_source"] = ups.get(
                "power_source", "unknown"
            )
            result["battery_percent"] = ups.get(
                "battery_percent"
            )
            result["shutdown_pending"] = ups.get(
                "shutdown_pending", False
            )
            result["shutdown_reason"] = ups.get(
                "shutdown_reason"
            )

            # Use the UPS monitor's timestamp when available.
            if ups.get("timestamp") is not None:
                result["timestamp"] = ups["timestamp"]

        except (OSError, ValueError, AttributeError, KeyError, TypeError):
            result["status"] = "degraded"
        try:
            with open(SHUTDOWN_REQUEST_FILE, encoding="utf-8") as f:
                request = json.load(f)

            if request.get("shutdown_pending") is True:
                result["shutdown_pending"] = True
                result["shutdown_reason"] = request.get("shutdown_reason")
                result["status"] = "shutting_down"

        except FileNotFoundError:
            pass
        except (OSError, ValueError, AttributeError):
            result["status"] = "degraded"
    return result

diagnostics_result = {
    "status": "starting",
    "timestamp": None
}
diagnostics_lock = threading.Lock()

def update_diagnostics():
    global diagnostics_result

    while True:
        try:
            result = get_diagnostics()
        except Exception:
            result = {
                "status": "unavailable",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

        with diagnostics_lock:
            diagnostics_result = result

        time.sleep(60)

def get_response(path):
    if path in ("/health", "/endpoints/health"):
        return get_health()

    if path in ("/diagnostics", "/endpoints/diagnostics"):
        with diagnostics_lock:
            return dict(diagnostics_result)

    return None

class HealthHandler(BaseHTTPRequestHandler):
    def respond(self, include_body):
        result = get_response(self.path.split("?", 1)[0])

        if result is None:
            self.send_response(404)
            self.end_headers()
            return

        body = json.dumps(result, indent=2).encode("utf-8")
        healthy = result.get("status") == "online"

        self.send_response(200 if healthy else 503)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()

        if include_body:
            self.wfile.write(body)

    def do_HEAD(self):
        self.respond(False)

    def do_GET(self):
        self.respond(True)

    def log_message(self, format, *args):
        return

if __name__ == "__main__":
    threading.Thread(target=update_diagnostics, daemon=True).start()

    server = HTTPServer((HOST, PORT), HealthHandler)
    print(f"Bargaz health server listening on {HOST}:{PORT}", flush=True)
    server.serve_forever()
