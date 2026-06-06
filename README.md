# 🤖 Jarvis Local (Windows + Claude)

Asistente de voz que escucha tu micrófono, le habla a Claude, y controla tu PC Windows (abrir ventanas, ejecutar acciones, controlar After Effects).

**Arquitectura local-local**: cliente y servidor corren ambos en tu Windows. Después se puede mover el servidor a Render cambiando una sola URL.

```
🎤 Tu voz
    ↓
[cliente.py] ──captura audio──> Whisper (STT) ──texto──> WebSocket
                                                              ↓
                                                    [server.py en localhost:8000]
                                                              ↓
                                                         Claude API
                                                              ↓
                                                    decide qué tool usar
                                                              ↓
[cliente.py] <──orden JSON───── WebSocket <──────────────────┘
    ↓
PyAutoGUI / pywinauto / ExtendScript → AE
    ↓
🔊 TTS responde
```

## Estructura

```
jarvis-local/
├── server/                  ← El "cerebro" (Claude + tools)
│   ├── server.py            ← FastAPI + WebSocket
│   ├── claude_client.py     ← Wrapper de la API de Claude
│   ├── tools/               ← Definiciones de tools que Claude puede invocar
│   │   ├── __init__.py
│   │   ├── system.py        ← abrir apps, ventanas
│   │   └── after_effects.py ← control de AE vía ExtendScript
│   └── requirements.txt
│
├── client/                  ← Las "manos y oídos" (corre en tu Windows)
│   ├── client.py            ← Loop principal: escucha → manda → ejecuta
│   ├── audio/
│   │   ├── recorder.py      ← captura micrófono
│   │   ├── stt.py           ← speech-to-text (Whisper local)
│   │   └── tts.py           ← text-to-speech (pyttsx3 o ElevenLabs)
│   ├── control/
│   │   ├── system.py        ← PyAutoGUI + pywinauto
│   │   └── executor.py      ← traduce órdenes JSON a acciones
│   ├── ae_bridge/
│   │   ├── runner.py        ← ejecuta ExtendScript .jsx en AE
│   │   └── scripts/         ← .jsx pre-hechos
│   └── requirements.txt
│
├── .env.example             ← plantilla de variables
└── docs/
    └── SETUP.md             ← guía paso a paso
```

## Setup rápido

### 1. Prerequisitos
- Windows 10/11
- Python 3.11+ ([descargar](https://www.python.org/downloads/))
- After Effects (con scripting habilitado, ver SETUP.md)
- API key de Anthropic ([console.anthropic.com](https://console.anthropic.com))

### 2. Instalar

```powershell
git clone <tu-repo>
cd jarvis-local

# Servidor
cd server
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
deactivate
cd ..

# Cliente
cd client
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
deactivate
cd ..

# Configurar API key
copy .env.example .env
# Edita .env y pon tu ANTHROPIC_API_KEY
```

### 3. Correr (necesitas DOS terminales)

**Terminal 1 — Servidor:**
```powershell
cd server
.\venv\Scripts\activate
python server.py
```

**Terminal 2 — Cliente:**
```powershell
cd client
.\venv\Scripts\activate
python client.py
```

Cuando el cliente diga "Listening...", háblale: *"Jarvis, abre el bloc de notas"*.

## Roadmap del proyecto

- [x] Estructura base
- [ ] **Milestone 1**: Servidor responde a texto plano sin tools (probar Claude funciona)
- [ ] **Milestone 2**: Cliente captura audio → texto y lo manda al servidor
- [ ] **Milestone 3**: Tool básica: abrir aplicaciones Windows
- [ ] **Milestone 4**: TTS para que Jarvis responda hablado
- [ ] **Milestone 5**: Control de ventanas (mover, redimensionar, cerrar)
- [ ] **Milestone 6**: Puente a After Effects (ExtendScript)
- [ ] **Milestone 7**: Wake word ("Jarvis...") en lugar de push-to-talk
- [ ] **Milestone 8**: Mover servidor a Render

Lee `docs/SETUP.md` para la guía detallada paso a paso.
