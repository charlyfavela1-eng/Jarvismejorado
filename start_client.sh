#!/bin/bash
set -e
cd "$(dirname "$0")/client"

if [ ! -d "venv" ]; then
    echo "[setup] Creando entorno virtual del cliente..."
    python3 -m venv venv
    source venv/bin/activate
    echo "[setup] Instalando dependencias..."
    echo "[setup] Nota: faster-whisper descargará el modelo la primera vez (~150 MB)..."
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

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
python client.py
