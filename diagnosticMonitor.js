export function startDiagnosticMonitor({
  onAlert,
  url = "http://127.0.0.1:3001/endpoints/diagnostics",
  intervalMs = 60000
}) {
  let stopped = false;
  let timer;
  let currentCheck = Promise.resolve();
  let previousKey = null;

  async function check() {
    let issues;
    let diagnostics = null;

    try {
      const response = await fetch(url, {
        signal: AbortSignal.timeout(5000),
        cache: "no-store"
      });

      diagnostics = await response.json();

      if (
        ![200, 503].includes(response.status) ||
        !diagnostics.checks ||
        !diagnostics.storage ||
        !Array.isArray(diagnostics.storage_errors)
      ) {
        throw new Error("Invalid diagnostics response");
      }

      const updated = Date.parse(diagnostics.timestamp);
      const age = Date.now() - updated;

      if (!Number.isFinite(updated) || age > 180000 || age < -30000) {
        throw new Error("Diagnostics are stale");
      }

      issues = Object.entries(diagnostics.checks)
        .filter(([, passed]) => passed !== true)
        .map(([name]) => `check_failed:${name}`);

      for (const name of ["low_space", "low_inodes"]) {
        const value = diagnostics.storage[name];

        if (value !== false) {
          issues.push(value === true ? name : `check_unavailable:${name}`);
        }
      }

      issues.push(...diagnostics.storage_errors);
    } catch {
      issues = ["diagnostics_unavailable"];
    }

    if (stopped) {
      return;
    }

    issues.sort();
    const key = JSON.stringify(issues);

    if (key === previousKey) {
      return;
    }

    if (previousKey !== null || issues.length > 0) {
      await onAlert({
        recovered: issues.length === 0,
        issues,
        diagnostics
      });
    }

    previousKey = key;
  }

  async function tick() {
    try {
      await check();
    } catch (error) {
      console.error("Diagnostic alert delivery failed:", error);
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