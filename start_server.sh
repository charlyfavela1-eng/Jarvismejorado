#!/bin/bash
set -e
cd "$(dirname "$0")/server"

if [ ! -d "venv" ]; then
    echo "[setup] Creando entorno virtual del servidor..."
    python3 -m venv venv
    echo "[setup] Instalando dependencias..."
    venv/bin/pip install -r requirements.txt
fi

PYTHON=venv/bin/python

if [ ! -f "../.env" ]; then
    echo ""
    echo " ERROR: No encontré el archivo .env en la raíz del proyecto."
    echo " Copia .env.example a .env y pon tu ANTHROPIC_API_KEY."
    echo ""
    exit 1
fi

echo ""
echo " ===================================="
echo "  Jarvis Server  —  localhost:8000"
echo " ===================================="
echo ""
$PYTHON server.py
