import {
  readUpsStatus,
  readShutdownRequest,
  getNetworkStatus,
  hasInternetConnection
} from "./upsStatus.js";

export function startUpsMonitor({
  onStatus,
  onShutdown,
  intervalMs = 5000,
  networkShutdownMs = 120000
}) {
  let stopped = false;
  let timer;
  let currentCheck = Promise.resolve();
  let disconnectedAt = null;
  let shutdownRequested = false;
  let lastRequestId = null;

  async function check() {
    const status = readUpsStatus();
    const request = readShutdownRequest();
    const network = await getNetworkStatus();
    const connected = await hasInternetConnection();

    if (stopped) {
      return;
    }

    if (connected) {
      disconnectedAt = null;
    } else {
      disconnectedAt ??= Date.now();
    }

    const snapshot = {
      status,
      request,
      network: {...network, connected},
      timestamp: Date.now()
    };

    if (
      request?.shutdown_pending === true &&
      request.shutdown_request_id &&
      request.shutdown_request_id !== lastRequestId
    ) {
      lastRequestId = request.shutdown_request_id;
      shutdownRequested = true;
      await onShutdown({
        ...snapshot,
        requestId: lastRequestId,
        source: "ups"
      });
      return;
    }

    if (
      !shutdownRequested &&
      disconnectedAt !== null &&
      Date.now() - disconnectedAt >= networkShutdownMs
    ) {
      shutdownRequested = true;
      await onShutdown({
        ...snapshot,
        requestId: `network-${Date.now()}`,
        source: "network"
      });
      return;
    }

    if (!shutdownRequested) {
      await onStatus(snapshot);
    }
  }

  async function tick() {
    try {
      await check();
    } catch (error) {
      console.error("UPS/network monitoring failed:", error);
    } finally {
      if (!stopped) {
        timer = setTimeout(() => {
          currentCheck = tick();
        }, intervalMs);
      }
    }
  }

  currentCheck = tick();

  return {
    async stop() {
      stopped = true;
      clearTimeout(timer);
      await currentCheck;
    }
  };
}