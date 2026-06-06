@echo off
title Jarvis — Cliente
cd /d "%~dp0client"

if not exist "venv\Scripts\activate.bat" (
    echo [setup] Creando entorno virtual del cliente...
    python -m venv venv
    call venv\Scripts\activate.bat
    echo [setup] Instalando dependencias...
    echo [setup] Nota: faster-whisper descargara el modelo la primera vez...
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
echo   Jarvis Cliente
echo   Asegurate de que el servidor
echo   este corriendo en otra terminal.
echo  ====================================
echo.
python client.py
pause
