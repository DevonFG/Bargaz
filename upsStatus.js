import fs from "fs";
import https from "https";
import {execFile} from "child_process";
import {promisify} from "util";
import {UPS_STATUS_FILE, SHUTDOWN_REQUEST_FILE} from "./config.js";

const execFileAsync = promisify(execFile);

const NETWORK_TIMEOUT_MS = 3000;
const WIFI_NAMES = {
  "Dragon Tears": "Home Wi-Fi",
  "OSU_IOT": "Primary Dorm Wi-Fi",
  "eduroam": "Backup Dorm Wi-Fi"
};

export function readUpsStatus() {
  try {
    return JSON.parse(fs.readFileSync(UPS_STATUS_FILE, "utf8"));
  } catch (error) {
    console.error("Unable to read UPS status:", error);
    return null;
  }
}

export function readShutdownRequest() {
  try {
    if (!fs.existsSync(SHUTDOWN_REQUEST_FILE)) {return null;}
    return JSON.parse(fs.readFileSync(SHUTDOWN_REQUEST_FILE, "utf8"));
  } catch (error) {
    console.error("Unable to read shutdown request:", error);
    return null;
  }
}

export async function getNetworkStatus() {
  const interfaces = fs.readdirSync("/sys/class/net").filter(name => name !== "lo");
  const active = [];

  for (const name of interfaces) {
    try {
      const state = fs.readFileSync(`/sys/class/net/${name}/operstate`, "utf8").trim();
      if (state !== "up") {continue;}

      const wireless = fs.existsSync(`/sys/class/net/${name}/wireless`);
      active.push({name, wireless});
    } catch {}
  }

  const ethernet = active.find(item => !item.wireless && !/^(tailscale|tun|tap|docker|veth|br-|wg)/.test(item.name));

  if (ethernet) {
    return {type: "ethernet", name: "Ethernet", bars: null, interface: ethernet.name};
  }

  const wifi = active.find(item => item.wireless);
  if (!wifi) {return {type: "disconnected", name: "Disconnected", bars: 0, interface: null};}

  const ssid = await runCommand("iwgetid", [wifi.name, "--raw"]);
  const signal = await runCommand("iw", ["dev", wifi.name, "link"]);
  const dbm = Number(signal?.match(/signal:\s*(-?\d+)/)?.[1]);

  let bars = null;

  if (Number.isFinite(dbm) && signal?.includes("signal:")) {
    if (dbm >= -55) {bars = 4;}
    else if (dbm >= -65) {bars = 3;}
    else if (dbm >= -75) {bars = 2;}
    else if (dbm >= -85) {bars = 1;}
    else {bars = 0;}
  }

  return {
    type: "wifi",
    name: WIFI_NAMES[ssid] || (ssid ? "Other Wi-Fi" : "Unknown Wi-Fi"),
    ssid: ssid || null,
    bars,
    interface: wifi.name
  };
}

export async function hasInternetConnection() {
  const results = await Promise.all([
    checkEndpoint("discord.com"),
    checkEndpoint("www.google.com"),
    checkEndpoint("www.cloudflare.com")
  ]);

  return results.some(Boolean);
}

async function runCommand(command, args = []) {
  try {
    const {stdout} = await execFileAsync(command, args, {timeout: 2000});
    return stdout.trim();
  } catch {
    return null;
  }
}

function checkEndpoint(host) {
  return new Promise(resolve => {
    const request = https.get({
      hostname: host,
      path: "/",
      signal: AbortSignal.timeout(NETWORK_TIMEOUT_MS)
    }, response => {
      response.resume();
      resolve(true);
    });

    request.on("error", () => resolve(false));
  });
}
