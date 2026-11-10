#!/usr/bin/env python3

import json
import os
import subprocess
import time
from datetime import datetime, timezone

from INA219 import INA219


CHECK_INTERVAL = 5
SHUTDOWN_PERCENT = 30.0

MIN_VOLTAGE = 6.0
MAX_VOLTAGE = 8.4

STATUS_FILE = os.environ.get(
    "UPS_STATUS_FILE",
    "/home/devon/ups/ups_status.json"
)

ina219 = INA219(addr=0x42)


def battery_percent(voltage):
    percent = (
        (voltage - MIN_VOLTAGE)
        / (MAX_VOLTAGE - MIN_VOLTAGE)
        * 100
    )
    return max(0.0, min(100.0, percent))


def write_status(
    power_source,
    on_battery,
    percent,
    voltage,
    current,
    power
):

    status = {
        "power_source": power_source,
        "on_battery": on_battery,
        "battery_percent": round(percent, 1),
        "voltage": round(voltage, 3),
        "current": round(current, 4),
        "power": round(power, 3),
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    temp_file = STATUS_FILE + ".tmp"

    with open(temp_file, "w") as f:
        json.dump(status, f, indent=2)

    os.replace(temp_file, STATUS_FILE)


while True:
    try:
        voltage = ina219.getBusVoltage_V()
        current = ina219.getCurrent_mA() / 1000.0
        power = ina219.getPower_W()

        percent = battery_percent(voltage)
        on_battery = current < 0
        power_source = "battery" if on_battery else "external"

        low_battery_shutdown_needed = (
            on_battery and percent <= SHUTDOWN_PERCENT
        )

        write_status(
            power_source,
            on_battery,
            percent,
            voltage,
            current,
            power
        )

        if low_battery_shutdown_needed:
            result = subprocess.run(
                [
                    "/usr/bin/systemctl",
                    "start",
                    "--no-block",
                    "bargaz-shutdown@low_battery.service"
                ],
                check=False
            )

            if result.returncode == 0:
                break

            print(
                f"UPS shutdown request failed with exit code "
                f"{result.returncode}; monitoring will continue.",
                flush=True
            )

    except Exception as e:
        print(f"UPS monitor error: {e}", flush=True)

    time.sleep(CHECK_INTERVAL)