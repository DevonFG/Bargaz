# Changelog

### Format: YY.FEATURE.PATCH-NOTE.V
- YY = The year the feature was introduced
- FEATURE = The feature number from that year
    - When a new feature is released in a new year, FEATURE starts at 1
- PATCH = Bug fixes since the last feature added (Year doesn't turn over till new feature is added)
- NOTE = Optional development status "dev", "beta", or "error" to indicate an in-progress version
    - "dev" is refering to a version that has not been deployed
    - "beta" is refering to a version that is deployed while undergoing testing
    - "error" is refering to a version that exists due to system errors that require edits, it can be deployed or not
- V = Optional revision number that corresponds with the current development status (NOTE), starting at 1

A feature is when something is added/removed that changes what the user can do.
Any other changes, regardless of size, is considered a patch. (Very few exceptions)

Note: A change from dev or beta to a release is not impacted by an untestable feature like needing to wait for a
specific platform to have new content. In cases like that, the untested feature can be logged and the version released.
Additional Note: Error versions can have beta, dev, and release version
before and afterwards due to the multi-use of the version type.

## v26.1.1 - Nov 12
- Edited LED Indicator code after restarting and testing

## v26.1.0 - Nov 12
- Updated diagnostics.py
  - actually reads bargazbot.db instead of an empty :memory: database
  - Kernel storage errors are pre-run instead of module-level set that never cleared (one old warning no longer pins the system as degraded forever)
  - Database now reported in detail
  - Filesystem read-only detection added from /proc/mounts
  - New Install-sync check (compares diagnostics.py and health_server.py between the repo and /out)
  - Backup reporting added
  - Network reporting added
  - new checks for backup_hourly/daily/weekly
- Updated health_server.py
  - Shutdown-request file is read even when ups_status.json is missing
  - added /endpoints/versions, /endpoints/backups, /endpoints/network, /health, and /diagnostics
  - Exceptions in the diagnostics loop now print a traceback instead of unavailable
- Updated shutdownCoordinator.js
  - Network shtudown now runs the app's shutdown handlers first, then requests the host shutdown. A failed sent message while offline is now bounded by a 30s timeout and will not block poweroff
  - Removed multiple unused exports
- ups-shutdown was updated so that if the app already wrote a readiness file in the last 60s, the host skips its 45s wait and powres off immidiately
- Updated install-system.sh
  - New --if-changed mode hashes everything it installs and exits when nothing changed
  - Installs and enables bargaz-install.timer which runs every 2mins and restarts healther-server and ups-monitor when something changes
- Updated systemd/
  - bargazbot-db-backup@service WorkingDirectory corrected to /home/devon/Bargaz/BargazBot (daily/weekly backups didn't exist when checking, this fixes that)
  - new bargaz-install.service and bargaz-install.timer
- Unknown SSIDs are no longer printed in status output from upsStatus.js
- Added new LED light indicator for ups shutdown process
Note: I cannot test the network shutdown changes until the wifi actually disconnects.

## v26.0.1 - Nov 10
- Confirmed all features working!

## v26.0.1-error.1 - Nov 10
- Moved backup-databases.js from BargazBot to Bargaz
  - Made database and log directories configurable
  - Added SQLite integrity anf foreign-key checks before publishing backups
  - Added unique filenames and temporary backup files
- Moved logging.jsfrom BargazBot to Bargaz and made its database and Discord dependencies configurable
- Moved shutdownCoordinator.js from BargazBot to Bargaz
  - Made the readiness-file path configurable
  - Prevented failed cleanup from being reported as shutdown-ready
  - Routed network shutdown requests through the host shutdown process
- Moved UPS status and network-checking functions from upsNotifier.js into upsStatus.js
- Added upsMonitor.js for shared polling and shutdown-request detection
- Moved health_server.py into Bargaz
  - Made its settings configurable
  - Corrected shutdown-state reads
  - Added state-status detection, diagnostic routes, and matching GET/HEAD health responses
- Moved ups_monitor.py into Bargaz
  - Made its status-file path configurable
  - Fixed the low-battery shutdown argument
  - Routed shutdown requests through systemd and retained monitoring when requests fail
- Moved ups-shutdown into Bargaz
  - Added configurable paths, request locking, and network shutdown support
  - Allowed Linux shutdown to procees after a 45-second application-preperation timeout
- Included Waveshare's MIT-licensed INA219.py driver with its license
- Moved the existing health, UPS, Cloudflare, and database backup server/timer templates into Bargaz
  - Updated installation paths and shared environment loading
  - Added backup locking and kernel-journal access
- Added a systemd shutdown service
- Added storage, inode, component, and kernel storage-error diagnostics
- Added diagnostic alert callbacks with duplicate suppression, delivery retries, and recovery notices
- Added an installer with dependency checks, root-owned system scripts, and limited network-shutdown permission
- Added shared configuration, .env.example, setup instructions, and .gitignore rules for private and generated files
Pending testing: backup test results, bargazBot/BargazLive integration, live Pi testing, and the safe-to-unplug visual indicator
