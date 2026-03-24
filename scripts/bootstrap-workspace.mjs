import fs from "node:fs";
import path from "node:path";
import { spawn } from "node:child_process";

const projectRoot = process.cwd();
const frontendNodeModules = path.join(projectRoot, "node_modules");
const backendVenv = path.join(projectRoot, "backend", ".venv");

function run(command) {
  return new Promise((resolve, reject) => {
    const child = spawn(command, {
      cwd: projectRoot,
      stdio: "inherit",
      shell: true,
    });

    child.on("error", reject);
    child.on("exit", (code) => {
      if (code === 0) {
        resolve();
        return;
      }
      reject(new Error(`Command failed: ${command} (exit ${code})`));
    });
  });
}

async function main() {
  if (!fs.existsSync(frontendNodeModules)) {
    console.log("Installing frontend dependencies (npm install)...");
    await run("npm install");
  } else {
    console.log("Frontend dependencies already installed.");
  }

  if (!fs.existsSync(backendVenv)) {
    console.log("Setting up backend environment (npm run setup:backend)...");
    await run("npm run setup:backend");
  } else {
    console.log("Backend virtual environment already exists.");
  }
}

main().catch((error) => {
  console.error(error.message);
  process.exit(1);
});

