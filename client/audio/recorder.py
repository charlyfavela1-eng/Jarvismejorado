"""
Captura audio del micrófono con detección de silencio (VAD simple).
Graba hasta que detecta un silencio sostenido.
"""
import numpy as np
import sounddevice as sd
import logging

log = logging.getLogger("audio.recorder")

SAMPLE_RATE = 16000
CHANNELS = 1
DTYPE = "float32"

# Umbral de "silencio" (RMS). Ajustar según tu mic.
SILENCE_THRESHOLD = 0.01
# Cuántos segundos de silencio sostenido cierran la grabación
SILENCE_DURATION = 1.2
# Máximo absoluto por seguridad
MAX_DURATION = 20.0


def record_until_silence() -> np.ndarray:
    """
    Graba audio del mic hasta que detecta SILENCE_DURATION segundos de silencio
    o hasta MAX_DURATION. Devuelve el audio como ndarray float32 mono.
    """
    log.info("🎤 Listening...")
    chunks = []
    silence_samples = 0
    silence_limit = int(SILENCE_DURATION * SAMPLE_RATE)
    max_samples = int(MAX_DURATION * SAMPLE_RATE)
    total_samples = 0
    started_speaking = False

    block_size = 1024  # ~64ms a 16kHz

    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype=DTYPE,
        blocksize=block_size,
    ) as stream:
        while True:
            block, _ = stream.read(block_size)
            block = block.flatten()
            chunks.append(block)
            total_samples += len(block)

            rms = np.sqrt(np.mean(block**2))

            if rms > SILENCE_THRESHOLD:
                started_speaking = True
                silence_samples = 0
            elif started_speaking:
                silence_samples += len(block)
                if silence_samples >= silence_limit:
                    log.info("🔇 Silencio detectado, cerrando grabación")
                    break

            if total_samples >= max_samples:
                log.info("⏱️  Tiempo máximo alcanzado")
                break

    audio = np.concatenate(chunks)
    log.info(f"📦 Audio capturado: {len(audio)/SAMPLE_RATE:.2f}s")
    return audio


def record_fixed(seconds: float = 5.0) -> np.ndarray:
    """Graba un bloque fijo, útil para pruebas."""
    log.info(f"🎤 Grabando {seconds}s...")
    audio = sd.rec(
        int(seconds * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype=DTYPE,
    )
    sd.wait()
    return audio.flatten()
