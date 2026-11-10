#!/bin/bash
set -euo pipefail

if [[ "$EUID" -ne 0 ]]; then
    echo "Run this installer with sudo on the Raspberry Pi."
    exit 1
fi

for command in python3 node flock systemctl journalctl visudo; do
    if ! command -v "$command" >/dev/null 2>&1; then
        echo "Missing required command: $command"
        exit 1
    fi
done

if ! python3 -c 'import smbus' >/dev/null 2>&1; then
    echo "Install python3-smbus before running this installer."
    exit 1
fi

if [[ ! -e /dev/i2c-1 ]]; then
    echo "Enable I2C and reboot before running this installer."
    exit 1
fi

if ! id devon >/dev/null 2>&1; then
    echo "The service templates require the devon account."
    exit 1
fi

if ! getent group systemd-journal >/dev/null; then
    echo "The systemd-journal group is missing."
    exit 1
fi

SOURCE_DIR="$(cd -- "$(dirname -- "$0")" && pwd)"

if [[ ! -f "$SOURCE_DIR/ups/INA219.py" ]]; then
    echo "Place the verified INA219.py driver in ups/ before installing."
    exit 1
fi

install -d -m 755 \
    /opt/bargaz-system \
    /opt/bargaz-system/ups \
    /opt/bargaz-system/health

install -o root -g root -m 644 \
    "$SOURCE_DIR/ups/INA219.py" \
    "$SOURCE_DIR/ups/ups_monitor.py" \
    "$SOURCE_DIR/ups/ups_monitor.py" \
    /opt/bargaz-system/ups/

install -o root -g root -m 755 \
    "$SOURCE_DIR/ups/ups-shutdown" \
    /opt/bargaz-system/ups/ups-shutdown

install -o root -g root -m 644 \
    "$SOURCE_DIR/health/health_server.py" \
    "$SOURCE_DIR/health/diagnostics.py" \
    /opt/bargaz-system/health/

for unit in \
    health-server.service \
    ups-monitor.service \
    bargaz-shutdown@.service \
    bargazbot-db-backup@.service \
    bargazbot-db-backup-hourly.timer \
    bargazbot-db-backup-daily.timer \
    bargazbot-db-backup-weekly.timer
do
    install -o root -g root -m 644 \
        "$SOURCE_DIR/systemd/$unit" \
        "/etc/systemd/system/$unit"
done

cat > /usr/local/sbin/ups-shutdown <<'SH'
#!/bin/bash
set -euo pipefail

reason="${1:-manual}"

case "$reason" in
    manual|low_battery|network) ;;
    *)
        echo "Invalid shutdown reason: $reason"
        exit 1
        ;;
esac

exec systemctl start --no-block "bargaz-shutdown@${reason}.service"
SH

chown root:root /usr/local/sbin/ups-shutdown
chmod 755 /usr/local/sbin/ups-shutdown

sudo_rule="$(mktemp)"
trap 'rm -f "$sudo_rule"' EXIT

echo 'devon ALL=(root) NOPASSWD: /usr/local/sbin/ups-shutdown network' \
    > "$sudo_rule"

visudo -cf "$sudo_rule"

install -o root -g root -m 440 \
    "$sudo_rule" /etc/sudoers.d/bargaz-network-shutdown

systemctl daemon-reload

echo "Bargaz system files installed."
echo "Services and timers are ready for the Pi setup verification."