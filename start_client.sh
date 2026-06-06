#!/bin/bash
set -e
cd "$(dirname "$0")/client"

if [ ! -d "venv" ]; then
    echo "[setup] Creando entorno virtual del cliente..."
    python3 -m venv venv
    echo "[setup] Instalando dependencias..."
    echo "[setup] Nota: faster-whisper descargará el modelo la primera vez (~150 MB)..."
    venv/bin/pip install --prefer-binary -r requirements.txt
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
echo "  Jarvis Cliente"
echo "  Asegúrate de que el servidor"
echo "  esté corriendo en otra terminal."
echo " ===================================="
echo ""
$PYTHON client.py
