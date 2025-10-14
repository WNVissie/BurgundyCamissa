@echo off
echo 🚀 Starting Employee Shift Roster App with Docker
echo ================================================

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Error: Docker is not running. Please start Docker and try again.
    pause
    exit /b 1
)

REM Check if Docker Compose is available
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Error: Docker Compose is not installed.
    pause
    exit /b 1
)

REM Create data directories if they don't exist
echo 📁 Creating data directories...
if not exist "data\database" mkdir data\database
if not exist "data\uploads" mkdir data\uploads

echo 🔨 Building and starting containers...

REM Build and start services
docker-compose up --build -d

if %errorlevel% equ 0 (
    echo ✅ Application started successfully!
    echo.
    echo 🌐 Frontend: http://localhost:3000
    echo 🔧 Backend API: http://localhost:5001
    echo.
    echo 📊 To view logs: docker-compose logs -f
    echo 🛑 To stop: docker-compose down
) else (
    echo ❌ Failed to start the application.
    echo 📋 Check logs: docker-compose logs
    pause
    exit /b 1
)

pause