import fs from "node:fs";
import path from "node:path";
import { spawn } from "node:child_process";

const projectRoot = process.cwd();
const backendDir = path.join(projectRoot, "backend");
const venvPython = process.platform === "win32"
  ? path.join(backendDir, ".venv", "Scripts", "python.exe")
  : path.join(backendDir, ".venv", "bin", "python");
const systemPython = process.env.PYTHON ?? (process.platform === "win32" ? "python" : "python3");
const pythonExec = fs.existsSync(venvPython) ? venvPython : systemPython;
const backendPort = process.env.BACKEND_PORT ?? "8000";

const child = spawn(
  pythonExec,
  [
    "-m",
    "uvicorn",
    "main:app",
    "--reload",
    "--host",
    "127.0.0.1",
    "--port",
    backendPort,
    "--app-dir",
    "backend",
  ],
  { stdio: "inherit", cwd: projectRoot }
);

child.on("error", () => {
  console.error("Failed to start backend. Run `npm run setup:backend` first.");
  process.exit(1);
});

child.on("exit", (code) => {
  process.exit(code ?? 0);
});

