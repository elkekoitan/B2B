Param(
  [string]$ComposeFile = "docker-compose.coolify.yml",
  [string]$EnvFile = ".env"
)

function Write-Info($msg) { Write-Host "[INFO] $msg" -ForegroundColor Cyan }
function Write-Err($msg) { Write-Host "[ERROR] $msg" -ForegroundColor Red }

# Check Docker Desktop
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
  Write-Err "Docker is not installed. Install Docker Desktop and retry."
  exit 1
}

# Ensure .env exists; if not, copy .env.mock
if (-not (Test-Path $EnvFile)) {
  if (Test-Path ".env.mock") {
    Copy-Item ".env.mock" $EnvFile -Force
    Write-Info "Created $EnvFile from .env.mock (mock mode)"
  } else {
    Write-Err "Missing $EnvFile and .env.mock. Aborting."
    exit 1
  }
}

Write-Info "Starting services with $ComposeFile using $EnvFile ..."
docker compose -f $ComposeFile --env-file $EnvFile build --no-cache
if ($LASTEXITCODE -ne 0) { Write-Err "Build failed"; exit 1 }

docker compose -f $ComposeFile --env-file $EnvFile up -d
if ($LASTEXITCODE -ne 0) { Write-Err "Compose up failed"; exit 1 }

Write-Info "Done. Open UI: http://localhost:13000 | API: http://localhost:18000"

