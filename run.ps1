# One-command launcher (works from any folder):
#   powershell -ExecutionPolicy Bypass -File <path-to>\DataPilot\run.ps1
param([switch]$NoRun)
$ErrorActionPreference = "Stop"
$proj = $PSScriptRoot
Set-Location $proj
$venv = Join-Path $env:USERPROFILE "venvs\datapilot"
$py = Join-Path $venv "Scripts\python.exe"
if (-not (Test-Path $py)) {
    Write-Host "Creating Python 3.12 environment at $venv ..."
    py -3.12 -m venv $venv
    if (-not (Test-Path $py)) { throw "Python 3.12 not found. Install it from python.org." }
}
& $py -c "import streamlit, autogen_agentchat, autogen_ext, pandas, matplotlib" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Installing requirements (first run only) ..."
    & $py -m pip install -q -r (Join-Path $proj "requirements.txt")
}
if (-not (Test-Path (Join-Path $proj ".env"))) { Copy-Item .env.example .env; Write-Host "Created .env (mock mode)." }
if (-not (Test-Path "sample_data\sales_2026.csv")) { & $py sample_data\make_sample.py }
$env:PYTHONPATH = Join-Path $proj "src"
& $py -m datapilot.branding   # tab title + icon = DataPilot (no Streamlit flash)
if ($NoRun) { Write-Host "OK (NoRun)"; exit 0 }
& $py -m streamlit run (Join-Path $proj "app.py")
