"""
Text-to-speech.
- Windows/Mac: pyttsx3 con las voces del sistema.
- Linux sin motor de voz: fallback a imprimir el texto (útil para desarrollo).
"""
import logging

log = logging.getLogger("audio.tts")

_engine = None
_mode: str | None = None  # "pyttsx3" | "print"


def _init():
    global _engine, _mode
    if _mode is not None:
        return

    try:
        import pyttsx3
        engine = pyttsx3.init()
        engine.setProperty("rate", 180)
        for voice in engine.getProperty("voices"):
            name = voice.name.lower()
            if "spanish" in name or "español" in name or "sabina" in name or "diego" in name:
                engine.setProperty("voice", voice.id)
                log.info(f"Voz TTS: {voice.name}")
                break
        _engine = engine
        _mode = "pyttsx3"
        log.info("TTS inicializado con pyttsx3")
    except Exception as e:
        log.warning(f"pyttsx3 no disponible ({e}) — TTS en modo texto")
        _mode = "print"


def speak(text: str):
    global _mode
    if not text:
        return
    log.info(f"Jarvis: {text[:80]}")
    _init()

    if _mode == "pyttsx3":
        try:
            _engine.say(text)
            _engine.runAndWait()
            return
        except Exception as e:
            log.warning(f"pyttsx3 error: {e} — usando modo texto")
            _mode = "print"

    # Fallback: mostrar en consola
    print(f"\n🤖 Jarvis: {text}\n")
