# Bargaz

Bargaz is a project focused on providing shared infrastructure, monitoring, and system management for the Bargaz software ecosystem.

The project provides reusable tools for BargazBot and BargazLive, with support for future deployment across multiple devices.

## Project Scope

### Shared Infrastructure

Bargaz includes shared tools and configuration for:

- SQLite database backups with integrity checks and hourly, daily, and weekly retention.
- Logging with application-provided database and Discord connections.
- UPS battery, power-source, and network monitoring.
- Application shutdown preparation and host shutdown requests.
- Systemd services, backup timers, and Raspberry Pi installation.

### Health and Diagnostics

Bargaz provides health and diagnostics endpoints for monitoring system availability, battery status, storage, inodes, installed components, and detected kernel storage errors.

The health server listens on `127.0.0.1:3001` by default.

| Endpoint | Purpose |
|---|---|
| `/health` | Compatibility with the existing health monitor |
| `/endpoints/health` | Power, battery, and shutdown status |
| `/endpoints/diagnostics` | Component checks, storage availability, and detected storage errors |

The intended public endpoint location is **[bargaz.app/endpoints/](https://bargaz.app/endpoints/)**. Cloudflare must route these requests to the health service. Website traffic remains with BargazLive.

Diagnostics refresh every minute. Kernel checks inspect up to 5,000 retained messages from the current boot. Database backups receive separate SQLite integrity checks.

Diagnostic alert callbacks support duplicate suppression, delivery retries, and recovery notices. BargazBot supplies Discord delivery.

## Installation

The current Raspberry Pi deployment uses a parent Bargaz repository with separate BargazBot and BargazLive checkouts inside it.

```text
/home/devon/Bargaz
/home/devon/Bargaz/BargazBot
/home/devon/Bargaz/BargazLive
```

1. Install Node.js, Python 3, `python3-smbus`, and PM2. Enable I²C and reboot.
2. Run `npm ci` in each repository.
3. Use `.env.example` to configure shared settings in `/home/devon/.env`.
4. From Bargaz, run `sudo bash install-system.sh`.
5. Configure both applications and restore their private configuration and data.
6. Verify the services before enabling them and the backup timers.

The installer places system scripts under `/opt/bargaz-system`. Run it again after updating those scripts.

### Shutdown

Request a manual shutdown on the Raspberry Pi using:

```bash
sudo ups-shutdown
```

The host allows up to 45 seconds for application preparation before requesting Linux shutdown. Both applications require graceful termination handling and appropriate PM2 shutdown timeouts.

The physical safe-to-unplug indicator still requires verification.

### Private Configuration

Environment files, credentials, private keys, databases, logs, and generated UPS state remain outside Git.

## Related Projects and Links

- **[BargazBot](https://github.com/DevonFG/BargazBot)** — A Discord bot providing content creator notifications and community management tools.
- **[BargazLive](https://github.com/DevonFG/BargazLive)** — Website hosting and tools for livestreamers and content creators.
- **[Bargaz Website](https://bargaz.app)** — Information about Bargaz and its projects.
- **[The Wolf Den Discord Server](https://discord.gg/PvYFVshGrZ)** - Project feedback, bug reports, support, and Bargaz status.

## License

A license for Bargaz, BargazBot, and BargazLive has not yet been selected. Once selected, it will be posted at https://bargaz.app/license

The included `ups/INA219.py` driver comes from **[Waveshare’s UPS-Power-Module repository](https://github.com/waveshare/UPS-Power-Module)** and is distributed under the MIT License. Its copyright and license notice are included in `ups/LICENSE`.