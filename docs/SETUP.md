# Setup paso a paso

## Antes de empezar

### Lo que necesitas instalado en Windows
1. **Python 3.11 o 3.12** — descarga desde [python.org](https://www.python.org/downloads/). Al instalar, marca "Add Python to PATH".
2. **Git** — [git-scm.com](https://git-scm.com/download/win)
3. **Visual C++ Build Tools** (para faster-whisper) — [aka.ms/buildtools](https://aka.ms/buildtools), selecciona "Desktop development with C++".
4. **After Effects** — opcional al principio. Solo necesario cuando llegues al Milestone 6.

### API key de Anthropic
- Ve a [console.anthropic.com](https://console.anthropic.com)
- Crea una API key
- Cárgale al menos $5 USD de crédito
- Guarda la key, la usarás en `.env`

---

## Milestone 1 — Que el servidor responda a texto

Sin micrófono, sin tools, solo verificar que Claude responde.

```powershell
cd jarvis-local\server
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

Copia `.env.example` a `.env` en la raíz del proyecto y pon tu API key.

```powershell
python server.py
```

Deberías ver:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
```

Abre otra terminal y prueba:
```powershell
curl http://127.0.0.1:8000/health
```

Debe responder `{"ok": true, "model": "..."}`.

**Test WebSocket rápido** (en Python):
```python
import asyncio, websockets, json
async def test():
    async with websockets.connect("ws://127.0.0.1:8000/ws") as ws:
        await ws.send(json.dumps({"type": "user_message", "text": "Hola, ¿quién eres?"}))
        for _ in range(3):
            print(await ws.recv())
asyncio.run(test())
```

Si te responde, el cerebro funciona. ✅

---

## Milestone 2 — Cliente con audio

```powershell
cd ..\client
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

⚠️ **Posibles problemas:**

- **PyAudio falla:** instala con `pip install pipwin && pipwin install pyaudio`. Nota: `sounddevice` que usamos NO depende de PyAudio, debería funcionar directo.
- **faster-whisper tarda mucho en instalar:** es normal, baja modelos.
- **sounddevice no encuentra mic:** ejecuta `python -c "import sounddevice; print(sounddevice.query_devices())"` para listar dispositivos.

Con el servidor corriendo en la otra terminal:

```powershell
python client.py
```

La primera vez tarda ~30s en cargar Whisper. Después, presiona Enter (sin escribir nada) para grabar tu voz, o escribe texto para hacer debug sin mic.

Di: **"Hola Jarvis, ¿cómo estás?"**

Debe transcribir tu voz, mandarla al servidor, recibir respuesta y leerla en voz alta.

---

## Milestone 3 — Abrir aplicaciones

Con todo conectado, di:

> "Jarvis, abre el bloc de notas"

Claude debe llamar `open_app(app_name="notepad")`, el cliente lo ejecuta, y se abre Notepad. ✅

Prueba también:
- "Lista las ventanas abiertas"
- "Abre la calculadora"
- "Cierra la ventana del bloc de notas"

---

## Milestone 6 — After Effects

### Habilitar scripting en AE

1. Abre After Effects
2. Edit > Preferences > Scripting & Expressions
3. ✅ Marca **"Allow Scripts to Write Files and Access Network"**
4. Reinicia AE

### Ajustar AE_PATH

En `.env`, ajusta `AE_PATH` a tu versión real. Para verificar:

```powershell
dir "C:\Program Files\Adobe\Adobe After Effects*"
```

### Probar

> "Jarvis, abre After Effects y crea una composición de 1920 por 1080, 10 segundos, llamada Prueba"

Después:

> "Agrega un texto que diga Inbursa Nogales en color blanco"

---

## Wake word (Milestone 7, opcional)

Para que en vez de "Enter para grabar" sea "di Jarvis y empieza a hablar":

```powershell
pip install pvporcupine
```

Crea cuenta gratis en [picovoice.ai](https://picovoice.ai), descarga el wake word "jarvis", y modifica `client.py` para usar Porcupine antes de grabar.

---

## Troubleshooting general

**Cliente no conecta al servidor**
- Confirma que el servidor está corriendo (`http://127.0.0.1:8000/health`)
- Revisa `SERVER_URL` en `.env`
- Firewall: Windows puede preguntarte permiso la primera vez

**Whisper transcribe basura**
- Cambia `STT_MODEL` a `small` o `medium` (más lento pero preciso)
- Habla más cerca del mic
- Ajusta `SILENCE_THRESHOLD` en `audio/recorder.py`

**TTS suena robótico**
- Es pyttsx3, normal. Upgrade a ElevenLabs (cuesta ~$5/mes por uso normal): cambia `audio/tts.py` para usar su API.

**AE no responde a scripts**
- ¿Habilitaste el permiso de scripting?
- ¿AE está abierto antes de ejecutar la tool? Las tools de AE asumen que AE ya está corriendo (o usan `ae_launch` primero).
- Revisa `%TEMP%` por los .jsx generados; ábrelos en AE manualmente para ver errores.

**Costos disparados**
- Default es Haiku 4.5 (~$1/M tokens input). Para conversaciones normales no debería pasar de centavos al día.
- Si usas Sonnet/Opus, vigila el dashboard de Anthropic.
- Reseteo del historial: cada conversación nueva, manda `{"type": "reset"}` por WS (se puede automatizar con timeout de inactividad).
