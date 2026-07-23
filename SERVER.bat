@echo off
setlocal enabledelayedexpansion
title Capital Eye Hospital Records System

echo ============================================
echo  CAPITAL EYE HOSPITAL RECORDS SYSTEM
echo  LAN Production Server Startup
echo ============================================
echo.

cd /d "%~dp0"

if exist "venv\Scripts\activate.bat" (
    call "venv\Scripts\activate.bat"
    echo Virtual environment activated.
) else (
    echo ERROR: venv\Scripts\activate.bat not found.
    pause
    exit /b
)

echo.
echo Detecting server IP address...

set "SERVER_IP="

REM Pass 1: prefer real Wi-Fi/Ethernet adapters, skip known virtual adapters
REM (VirtualBox host-only 192.168.56.x, Windows Mobile Hotspot 192.168.137.x)
for /f "tokens=2 delims=:" %%A in ('ipconfig ^| findstr /i "IPv4"') do (
    set "ip=%%A"
    set "ip=!ip: =!"

    set "skip="
    echo !ip! | findstr /b "192.168.56." >nul && set "skip=1"
    echo !ip! | findstr /b "192.168.137." >nul && set "skip=1"

    if not defined skip (
        echo !ip! | findstr /b "192.168." >nul
        if not errorlevel 1 (
            set "SERVER_IP=!ip!"
            goto :IP_FOUND
        )

        echo !ip! | findstr /b "10." >nul
        if not errorlevel 1 (
            set "SERVER_IP=!ip!"
            goto :IP_FOUND
        )
    )
)

REM Pass 2: fallback - take any IPv4 address found, even virtual adapters
for /f "tokens=2 delims=:" %%A in ('ipconfig ^| findstr /i "IPv4"') do (
    if not defined SERVER_IP (
        set "ip=%%A"
        set "ip=!ip: =!"
        set "SERVER_IP=!ip!"
    )
)

:IP_FOUND

if not defined SERVER_IP (
    set /p SERVER_IP="Please enter server IP manually: "
)

echo Server IP: %SERVER_IP%
echo.

echo Updating .env ALLOWED_HOSTS and CSRF_TRUSTED_ORIGINS...

set "ENV_FILE=.env"
set "ALLOWED_LINE=ALLOWED_HOSTS=127.0.0.1,localhost,%SERVER_IP%"
set "CSRF_LINE=CSRF_TRUSTED_ORIGINS=http://127.0.0.1:8000,http://localhost:8000,http://%SERVER_IP%:8000"

if not exist "%ENV_FILE%" (
    echo SECRET_KEY=change-this-secret-key>%ENV_FILE%
    echo DEBUG=False>>%ENV_FILE%
    echo DATABASE_ENGINE=postgres>>%ENV_FILE%
    echo POSTGRES_DB=capital_eye_records_db>>%ENV_FILE%
    echo POSTGRES_USER=postgres>>%ENV_FILE%
    echo POSTGRES_PASSWORD=your_postgres_password>>%ENV_FILE%
    echo POSTGRES_HOST=localhost>>%ENV_FILE%
    echo POSTGRES_PORT=5432>>%ENV_FILE%
)

findstr /v /b /i "ALLOWED_HOSTS=" "%ENV_FILE%" > "%ENV_FILE%.tmp"
findstr /v /b /i "CSRF_TRUSTED_ORIGINS=" "%ENV_FILE%.tmp" > "%ENV_FILE%.tmp2"

echo %ALLOWED_LINE%>>"%ENV_FILE%.tmp2"
echo %CSRF_LINE%>>"%ENV_FILE%.tmp2"

move /y "%ENV_FILE%.tmp2" "%ENV_FILE%" >nul
del "%ENV_FILE%.tmp" >nul 2>nul

echo.
echo Applying migrations...
python manage.py migrate

echo.
echo Collecting static files...
python manage.py collectstatic --noinput

echo.
echo Creating backup reminder notification...
python manage.py create_backup_reminder

echo.
echo ============================================
echo  Server is starting.
echo.
echo  Other clinic devices should open:
echo  http://%SERVER_IP%:8000
echo.
echo  Press CTRL+C to stop the server.
echo ============================================
echo.

waitress-serve --host=0.0.0.0 --port=8000 config.wsgi:application

pause