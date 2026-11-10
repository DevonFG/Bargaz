import Database from "better-sqlite3";
import fs from "node:fs";
import path from "node:path";
import {randomUUID} from "node:crypto";

const [backupType, databaseDir, logDir] = process.argv.slice(2);

if (!databaseDir || !logDir) {
    console.error(
        "Usage: node backup-databases.js hourly|daily|weekly DATABASE_DIR LOG_DIR"
    );
    process.exit(1);
}

const DATABASE_DIR = path.resolve(databaseDir);
const BACKUP_DIR = path.join(DATABASE_DIR, "backups");
const LOG_DIR = path.resolve(logDir);
const LOG_FILE = path.join(LOG_DIR, "database-backup.log");

const retention = {
    hourly: 6,
    daily: 7,
    weekly: 5,
};

function log(message) {
    const timestamp = new Date().toLocaleString();
    const line = `[${timestamp}] ${message}`;

    console.log(line);
    try {
        fs.appendFileSync(LOG_FILE, `${line}\n`);
    } catch (error) {
        console.error("Unable to write backup log:", error.message);
        process.exitCode = 1;
    }
}

function getTimestamp() {
    const now = new Date();

    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, "0");
    const day = String(now.getDate()).padStart(2, "0");

    let hour = now.getHours();
    const minute = String(now.getMinutes()).padStart(2, "0");
    const amPm = hour >= 12 ? "PM" : "AM";

    hour %= 12;
    hour = hour || 12;
    hour = String(hour).padStart(2, "0");

    return `${year}-${month}-${day}_${hour}-${minute}-${amPm}`;
}

async function backupDatabases() {
    fs.mkdirSync(BACKUP_DIR, { recursive: true });
    fs.mkdirSync(LOG_DIR, { recursive: true });

    if (!Object.hasOwn(retention, backupType)) {
        log(
            `ERROR: Invalid backup type "${backupType}". ` +
            "Use hourly, daily, or weekly."
        );
        process.exitCode = 1;
        return;
    }

    const databaseFiles = fs
        .readdirSync(DATABASE_DIR)
        .filter((file) => file.endsWith(".db"));

    if (databaseFiles.length === 0) {
        log(`INFO: No databases found. Skipping ${backupType} backup.`);
        return;
    }

    for (const databaseFile of databaseFiles) {
        const databasePath = path.join(DATABASE_DIR, databaseFile);
        const databaseName = path.basename(databaseFile, ".db");

        const backupName =
            `${backupType}_${getTimestamp()}_${randomUUID()}_${databaseName}.db`;
        const backupPath = path.join(BACKUP_DIR, backupName);
        const temporaryPath = `${backupPath}.partial`;

        let db;

        try {
            db = new Database(databasePath, {
                readonly: true,
                fileMustExist: true,
            });

            await db.backup(temporaryPath);

            const verification = new Database(temporaryPath, {
                readonly: true,
                fileMustExist: true,
            });

            try {
                const integrity = verification.pragma("integrity_check");
                const foreignKeys = verification.pragma("foreign_key_check");

                if (
                    integrity.length !== 1 ||
                    integrity[0].integrity_check !== "ok" ||
                    foreignKeys.length !== 0
                ) {
                    throw new Error("Backup failed SQLite integrity checks.");
                }
            } finally {
                verification.close();
            }

            fs.renameSync(temporaryPath, backupPath);

            log(
                `SUCCESS: Created ${backupType} backup ` +
                `"${backupName}".`
            );

            try {
                removeOldBackups(databaseName);
            } catch (error) {
                log(
                    `ERROR: Backup was saved, but retention failed: ` +
                    error.message
                );
                process.exitCode = 1;
            }
        } catch (error) {
            log(
                `ERROR: Failed to back up "${databaseFile}": ` +
                error.message
            );

            try {
                fs.rmSync(temporaryPath, { force: true });
            } catch {
                // Nothing else to do if cleanup also fails.
            }

            process.exitCode = 1;
        } finally {
            if (db) {
                db.close();
            }
        }
    }
}

function removeOldBackups(databaseName) {
    const prefix = `${backupType}_`;
    const suffix = `_${databaseName}.db`;

    const backups = fs
        .readdirSync(BACKUP_DIR)
        .filter(
            (file) =>
                file.startsWith(prefix) &&
                file.endsWith(suffix)
        )
        .map((file) => ({
            file,
            modified: fs.statSync(
                path.join(BACKUP_DIR, file)
            ).mtimeMs,
        }))
        .sort((a, b) => b.modified - a.modified);

    const oldBackups = backups.slice(retention[backupType]);

    for (const backup of oldBackups) {
        fs.rmSync(path.join(BACKUP_DIR, backup.file));

        log(`INFO: Removed old backup "${backup.file}".`);
    }
}

await backupDatabases();