"""
Speech-to-text usando faster-whisper (corre local, sin red).
El modelo se descarga la primera vez.
"""
import os
import logging
import numpy as np
from faster_whisper import WhisperModel

log = logging.getLogger("audio.stt")

_model = None


def get_model() -> WhisperModel:
    """Lazy-load del modelo. La primera vez tarda en descargar."""
    global _model
    if _model is None:
        model_size = os.getenv("STT_MODEL", "base")
        log.info(f"Cargando modelo Whisper '{model_size}'... (primera vez tarda)")
        # int8 en CPU es rápido y suficientemente preciso
        _model = WhisperModel(model_size, device="cpu", compute_type="int8")
        log.info("Modelo cargado")
    return _model


def transcribe(audio: np.ndarray, language: str = "es") -> str:
    """Convierte audio (float32 mono 16kHz) a texto."""
    model = get_model()
    segments, info = model.transcribe(
        audio,
        language=language,
        beam_size=1,  # rápido; sube a 5 para más calidad
        vad_filter=True,
    )
    text = " ".join(seg.text for seg in segments).strip()
    log.info(f"📝 Transcrito: {text!r}")
    return text
