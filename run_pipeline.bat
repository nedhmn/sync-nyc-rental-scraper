@echo off
:: --------------------------------------------------------------------------
:: Script: Docker Startup Script for NYC Rental Scraper
::
:: Description:
:: This script automates the process of building and running a Docker
:: container for the NYC Rental Scraper application. It performs the
:: following steps:
::   1. Ensures the script is run with administrator privileges.
::   2. Checks for required files (.env and compose.yml).
::   3. Starts Docker Desktop if it's not already running.
::   4. Waits for Docker to become responsive.
::   5. Builds the Docker image.
::   6. Runs the Docker container, mounting the 'data' directory.
::
:: Usage:
:: 1.  Ensure Docker Desktop is installed.
:: 2.  Run the script as an administrator.
:: --------------------------------------------------------------------------
setlocal EnableDelayedExpansion

:: Set configuration
set "DOCKER_EXE=%ProgramFiles%\Docker\Docker\Docker Desktop.exe"
set "MAX_ATTEMPTS=10"
set "WAIT_SECONDS=10"
set "INITIAL_WAIT_SECONDS=20"

echo ========================================
echo           Docker Script Startup
echo ========================================

:: Function to check and ensure admin rights
call :EnsureAdminRights || exit /b 1

:: Function to check required files
call :CheckRequiredFiles || exit /b 1

:: Function to start Docker and wait for it
call :EnsureDockerRunning || exit /b 1

:: Function to run Docker commands
call :RunDockerCommands || exit /b 1

echo ========================================
echo           Script Completed
echo ========================================
pause
exit /b 0

:EnsureAdminRights
echo Checking administrator rights...
net session >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Please run this script as Administrator!
    echo Check the Github repository for instructions.
    pause
    exit /b 1
)
echo [OK] Admin rights confirmed.
exit /b 0

:CheckRequiredFiles
echo Checking required files...
if not exist "%~dp0.env" (
    echo [ERROR] .env not found in current directory!
    echo Check the Github repository for instructions.
    pause
    exit /b 1
)

if not exist "%~dp0compose.yml" (
    echo [ERROR] compose.yml not found in current directory!
    echo Check the Github repository for instructions.
    pause
    exit /b 1
)
echo [OK] Found all required files!
exit /b 0

:EnsureDockerRunning
echo Checking Docker Desktop status...
tasklist /FI "IMAGENAME eq Docker Desktop.exe" 2>NUL | find /I /N "Docker Desktop.exe">NUL
if "%ERRORLEVEL%"=="1" (
    echo Starting Docker Desktop...
    start "" "%DOCKER_EXE%"
    echo Waiting initial %INITIAL_WAIT_SECONDS% seconds for Docker to start...
    ping 127.0.0.1 -n %INITIAL_WAIT_SECONDS% > nul
)

set attempts=0
:DOCKER_READY_CHECK
set /a attempts+=1
echo [Attempt %attempts% of %MAX_ATTEMPTS%] Checking Docker responsiveness...
docker ps >nul 2>&1
if errorlevel 1 (
    if !attempts! equ %MAX_ATTEMPTS% (
        echo [ERROR] Docker failed to respond after %MAX_ATTEMPTS% attempts.
        echo Contact Ned for support.
        pause
        exit /b 1
    )
    echo Waiting %WAIT_SECONDS% seconds...
    ping 127.0.0.1 -n !WAIT_SECONDS! > nul
    goto DOCKER_READY_CHECK
)
echo [OK] Docker is responsive and ready!
exit /b 0

:RunDockerCommands
echo ========================================
echo Starting Docker Operations
echo ========================================

echo Building the containers...
docker compose -f "%~dp0compose.yml" build
if errorlevel 1 (
    echo [ERROR] Docker Compose build failed!
    echo Contact Ned for support.
    pause
    exit /b 1
)

echo Starting the containers...
docker compose -f "%~dp0compose.yml" up
if errorlevel 1 (
    echo [ERROR] Docker Compose failed to start containers!
    echo Contact Ned for support.
    pause
    exit /b 1
)

echo [OK] Docker operations completed successfully!
exit /b 0
