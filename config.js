import dotenv from "dotenv";
import os from "node:os";
import path from "node:path";

dotenv.config({
  path: process.env.BARGAZ_ENV_FILE || path.join(os.homedir(), ".env")
});

export const UPS_STATUS_FILE =
  process.env.UPS_STATUS_FILE || "/home/devon/ups/ups_status.json";

export const SHUTDOWN_REQUEST_FILE =
  process.env.SHUTDOWN_REQUEST_FILE || "/home/devon/ups/shutdown_request.json";

export const SHUTDOWN_READY_FILE =
  process.env.SHUTDOWN_READY_FILE || "/home/devon/ups/shutdown_ready.json";