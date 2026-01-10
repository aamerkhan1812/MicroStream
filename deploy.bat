@echo off
REM Automated deployment script for MicroStream system
REM Run this after Docker Desktop is installed and running

echo ============================================================
echo MicroStream - Automated Deployment Script
echo ============================================================
echo.

REM Check if Docker is running
echo [1/5] Checking Docker status...
docker --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker is not installed or not running!
    echo.
    echo Please:
    echo 1. Install Docker Desktop
    echo 2. Start Docker Desktop
    echo 3. Wait for it to fully start
    echo 4. Run this script again
    echo.
    pause
    exit /b 1
)
echo OK: Docker is installed
docker compose version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker Compose is not available!
    pause
    exit /b 1
)
echo OK: Docker Compose is available
echo.

REM Check if models exist
echo [2/5] Checking ML models...
if not exist "services\ml_engine\models\isolation_forest.pkl" (
    echo ERROR: Isolation Forest model not found!
    echo Please run: python notebooks\train_models.py
    pause
    exit /b 1
)
if not exist "services\ml_engine\models\hmm_regime.pkl" (
    echo ERROR: HMM model not found!
    echo Please run: python notebooks\train_models.py
    pause
    exit /b 1
)
echo OK: Both ML models found
echo.

REM Stop any existing containers
echo [3/5] Cleaning up existing containers...
docker compose down >nul 2>&1
echo OK: Cleanup complete
echo.

REM Build and start services
echo [4/5] Building and starting services...
echo This may take 5-10 minutes on first run...
echo.
docker compose up --build -d

if errorlevel 1 (
    echo.
    echo ERROR: Failed to start services!
    echo Check the error messages above.
    pause
    exit /b 1
)
echo.
echo OK: Services started successfully
echo.

REM Wait for services to be ready
echo [5/5] Waiting for services to initialize...
timeout /t 10 /nobreak >nul
echo.

REM Show status
echo ============================================================
echo Service Status:
echo ============================================================
docker compose ps
echo.

echo ============================================================
echo Deployment Complete!
echo ============================================================
echo.
echo Dashboard URL: http://localhost:8501
echo.
echo Useful commands:
echo   View logs:        docker compose logs -f
echo   Stop services:    docker compose down
echo   Restart:          docker compose restart
echo.
echo Opening dashboard in 5 seconds...
timeout /t 5 /nobreak >nul
start http://localhost:8501

echo.
echo Press any key to view live logs (Ctrl+C to exit)...
pause >nul
docker compose logs -f
