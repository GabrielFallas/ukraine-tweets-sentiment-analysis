@echo off
REM Setup script for Ukraine Tweets Sentiment Analysis Pipeline
REM Windows version

echo ============================================
echo Ukraine Tweets Sentiment Analysis Pipeline
echo Setup Script
echo ============================================
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker is not installed or not in PATH
    echo Please install Docker Desktop from https://www.docker.com/products/docker-desktop
    exit /b 1
)

echo [OK] Docker is installed
echo.

REM Check if docker-compose is available
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: docker-compose is not installed or not in PATH
    exit /b 1
)

echo [OK] docker-compose is installed
echo.

REM Create .env file if it doesn't exist
if not exist .env (
    echo Creating .env file from template...
    copy .env.example .env
    echo [OK] .env file created
    echo.
    echo IMPORTANT: Please edit .env file and add your keys:
    echo   1. Generate Fernet key: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
    echo   2. Generate Superset secret: openssl rand -base64 42
    echo.
) else (
    echo [OK] .env file already exists
    echo.
)

REM Create data directories
if not exist data\raw mkdir data\raw
if not exist data\processed mkdir data\processed
echo [OK] Data directories created
echo.

REM Create airflow directories
if not exist airflow\logs mkdir airflow\logs
if not exist airflow\plugins mkdir airflow\plugins
echo [OK] Airflow directories created
echo.

REM Create superset directories
if not exist superset\dashboards mkdir superset\dashboards
echo [OK] Superset directories created
echo.

echo ============================================
echo Setup Complete!
echo ============================================
echo.
echo Next Steps:
echo 1. Edit .env file with your generated keys
echo 2. Download the Ukraine tweets dataset from Kaggle:
echo    https://www.kaggle.com/datasets/bwandowando/ukraine-russian-crisis-twitter-dataset-1-2-m-rows
echo 3. Place the CSV file in: data\raw\ukraine_tweets.csv
echo 4. Run: docker-compose build
echo 5. Run: docker-compose up -d
echo 6. Wait 2-3 minutes for services to initialize
echo 7. Access Airflow at http://localhost:8080 (admin/admin)
echo.
echo For more information, see README.md
echo.

pause
