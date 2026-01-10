# MicroStream - Automated Deployment Script (PowerShell)
# Run this after Docker Desktop is installed and running

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "MicroStream - Automated Deployment Script" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is running
Write-Host "[1/5] Checking Docker status..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version 2>&1
    Write-Host "OK: Docker is installed: $dockerVersion" -ForegroundColor Green
    
    $composeVersion = docker compose version 2>&1
    Write-Host "OK: Docker Compose is available: $composeVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Docker is not installed or not running!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please:" -ForegroundColor Yellow
    Write-Host "1. Install Docker Desktop" -ForegroundColor Yellow
    Write-Host "2. Start Docker Desktop" -ForegroundColor Yellow
    Write-Host "3. Wait for it to fully start" -ForegroundColor Yellow
    Write-Host "4. Run this script again" -ForegroundColor Yellow
    exit 1
}
Write-Host ""

# Check if models exist
Write-Host "[2/5] Checking ML models..." -ForegroundColor Yellow
if (-not (Test-Path "services\ml_engine\models\isolation_forest.pkl")) {
    Write-Host "ERROR: Isolation Forest model not found!" -ForegroundColor Red
    Write-Host "Please run: python notebooks\train_models.py" -ForegroundColor Yellow
    exit 1
}
if (-not (Test-Path "services\ml_engine\models\hmm_regime.pkl")) {
    Write-Host "ERROR: HMM model not found!" -ForegroundColor Red
    Write-Host "Please run: python notebooks\train_models.py" -ForegroundColor Yellow
    exit 1
}
Write-Host "OK: Both ML models found" -ForegroundColor Green
Write-Host ""

# Stop any existing containers
Write-Host "[3/5] Cleaning up existing containers..." -ForegroundColor Yellow
docker compose down 2>&1 | Out-Null
Write-Host "OK: Cleanup complete" -ForegroundColor Green
Write-Host ""

# Build and start services
Write-Host "[4/5] Building and starting services..." -ForegroundColor Yellow
Write-Host "This may take 5-10 minutes on first run..." -ForegroundColor Cyan
Write-Host ""

$result = docker compose up --build -d 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to start services!" -ForegroundColor Red
    Write-Host $result
    exit 1
}
Write-Host "OK: Services started successfully" -ForegroundColor Green
Write-Host ""

# Wait for services to be ready
Write-Host "[5/5] Waiting for services to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 10
Write-Host ""

# Show status
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Service Status:" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
docker compose ps
Write-Host ""

Write-Host "============================================================" -ForegroundColor Green
Write-Host "Deployment Complete!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Dashboard URL: " -NoNewline
Write-Host "http://localhost:8501" -ForegroundColor Cyan
Write-Host ""
Write-Host "Useful commands:" -ForegroundColor Yellow
Write-Host "  View logs:        docker compose logs -f" -ForegroundColor White
Write-Host "  Stop services:    docker compose down" -ForegroundColor White
Write-Host "  Restart:          docker compose restart" -ForegroundColor White
Write-Host ""
Write-Host "Opening dashboard in 5 seconds..." -ForegroundColor Cyan
Start-Sleep -Seconds 5
Start-Process "http://localhost:8501"

Write-Host ""
Write-Host "Press Enter to view live logs (Ctrl+C to exit)..." -ForegroundColor Yellow
Read-Host
docker compose logs -f
