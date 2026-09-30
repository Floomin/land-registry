# Recreate project environment (Windows PowerShell). Run from the project root.
$ErrorActionPreference = "Stop"

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "uv not found - installing..."
    powershell -ExecutionPolicy ByPass -Command "irm https://astral.sh/uv/install.ps1 | iex"
    $env:Path = "$env:USERPROFILE\.local\bin;$env:Path"
}

if (Test-Path ".venv") {
    Remove-Item -Recurse -Force ".venv"
}

uv sync

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host ".env created - fill in the DB settings."
}

uv run ruff check .
Write-Host "Done. Run: uv run streamlit run app.py"