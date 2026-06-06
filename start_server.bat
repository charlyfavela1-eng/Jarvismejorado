@echo off
title Jarvis — Servidor
cd /d "%~dp0server"

if not exist "venv\Scripts\activate.bat" (
    echo [setup] Creando entorno virtual del servidor...
    python -m venv venv
    call venv\Scripts\activate.bat
    echo [setup] Instalando dependencias...
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate.bat
)

if not exist "..\\.env" (
    echo.
    echo  ERROR: No encontre el archivo .env en la raiz del proyecto.
    echo  Copia .env.example a .env y pon tu ANTHROPIC_API_KEY.
    echo.
    pause
    exit /b 1
)

echo.
echo  ====================================
echo   Jarvis Server  —  localhost:8000
echo  ====================================
echo.
python server.py
pause
