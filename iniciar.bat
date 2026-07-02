@echo off
chcp 65001 >nul
title GTFSSpain - Visor de Transporte Publico
echo.
echo ========================================
echo   GTFSSpain - Visor de Transporte Publico
echo   Datos de nap.transportes.gob.es
echo ========================================
echo.

REM Comprobar si Python esta instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no encontrado.
    echo       Instala Python 3.8+ desde https://www.python.org/downloads/
    echo       Asegurate de marcar "Add Python to PATH"
    pause
    exit /b 1
)

echo [OK] Python encontrado
echo.

REM Comprobar si el visor existe
if not exist "visor\index.html" (
    echo [ERROR] No se encontro visor\index.html
    pause
    exit /b 1
)

REM Comprobar si hay datos
set /a zip_count=0
for /r "data" %%f in (*.zip) do set /a zip_count+=1

echo [INFO] Datos GTFS: !zip_count! ZIPs encontrados
echo.

REM Obtener IP local
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do (
    for /f "tokens=1" %%i in ("%%a") do (
        set LOCAL_IP=%%i
    )
)

echo ========================================
echo   Servidor local iniciado
echo ========================================
echo.
echo   Visor: http://localhost:8080/visor/index.html
if defined LOCAL_IP (
    echo   Red local: http://%LOCAL_IP%:8080/visor/index.html
)
echo.
echo   Para detener: Ctrl+C
echo ========================================
echo.

REM Iniciar servidor
cd visor
python server.py
