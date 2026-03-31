import { spawn } from "node:child_process";

function run(scriptName) {
  return spawn(`npm run ${scriptName}`, {
    stdio: "inherit",
    shell: true,
  });
}

const backend = run("dev:backend");
const frontend = run("dev:frontend");
const children = [backend, frontend];

let shuttingDown = false;

function shutdown(exitCode = 0) {
  if (shuttingDown) return;
  shuttingDown = true;

  for (const child of children) {
    if (!child.killed) {
      child.kill("SIGINT");
    }
  }

  process.exit(exitCode);
}

backend.on("exit", (code) => {
  if (!shuttingDown && code && code !== 0) {
    shutdown(code);
  }
});

frontend.on("exit", (code) => {
  if (!shuttingDown && code && code !== 0) {
    shutdown(code);
  }
});

process.on("SIGINT", () => shutdown(0));
process.on("SIGTERM", () => shutdown(0));
