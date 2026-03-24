$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
  throw "Python not found in PATH"
}

if (-not (Test-Path ".venv")) {
  python -m venv .venv
}

$python = Join-Path $PSScriptRoot ".venv\\Scripts\\python.exe"

& $python -m pip install --upgrade pip
& $python -m pip install -r requirements.txt

Write-Host "Backend setup completed."
Write-Host "Run backend with: `npm run dev:backend`"

