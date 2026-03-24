import { spawn } from "node:child_process";
import fs from "node:fs";
import path from "node:path";

const projectRoot = process.cwd();
const backendDir = path.join(projectRoot, "backend");
const venvPython = process.platform === "win32"
  ? path.join(backendDir, ".venv", "Scripts", "python.exe")
  : path.join(backendDir, ".venv", "bin", "python");
const systemPython = process.env.PYTHON ?? (process.platform === "win32" ? "python" : "python3");

function run(command, args, options = {}) {
  return new Promise((resolve, reject) => {
    const child = spawn(command, args, { stdio: "inherit", ...options });
    child.on("error", reject);
    child.on("exit", (code) => {
      if (code === 0) {
        resolve();
        return;
      }
      reject(new Error(`Command failed: ${command} ${args.join(" ")} (exit ${code})`));
    });
  });
}

async function main() {
  if (!fs.existsSync(backendDir)) {
    throw new Error("backend directory not found");
  }

  if (!fs.existsSync(venvPython)) {
    await run(systemPython, ["-m", "venv", ".venv"], { cwd: backendDir });
  }

  await run(venvPython, ["-m", "pip", "install", "--upgrade", "pip"], { cwd: backendDir });
  await run(venvPython, ["-m", "pip", "install", "-r", "requirements.txt"], { cwd: backendDir });
}

main().catch((error) => {
  console.error(error.message);
  process.exit(1);
});

