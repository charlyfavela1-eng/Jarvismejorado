"""
Cliente Jarvis.

Loop:
1. Espera que el turno anterior haya terminado (turn_end del servidor).
2. Pide input: Enter vacío = grabar voz, texto = modo debug.
3. Manda texto al servidor por WebSocket.
4. Recibe speech (lo dice), execute (ejecuta y manda resultados) o turn_end.
5. Vuelve a 1.
"""
import os
import json
import asyncio
import logging
from dotenv import load_dotenv
import websockets

load_dotenv(dotenv_path="../.env")

from audio import recorder, stt, tts
from control import executor

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger("jarvis-client")

SERVER_URL = os.getenv("SERVER_URL", "ws://127.0.0.1:8000/ws")
WAKE_WORD = os.getenv("WAKE_WORD", "jarvis").lower()
TURN_TIMEOUT = 60  # segundos máximos esperando respuesta del servidor


async def main():
    log.info(f"Conectando a {SERVER_URL}...")
    try:
        async with websockets.connect(SERVER_URL) as ws:
            log.info("Conectado al servidor Jarvis")
            tts.speak("Listo")

            # Event que señala si el turno anterior ya terminó.
            # Inicia en set (= libre para enviar el primer mensaje).
            turn_done = asyncio.Event()
            turn_done.set()

            async def handle_server_message(msg: dict):
                mtype = msg.get("type")

                if mtype == "speech":
                    tts.speak(msg["text"])

                elif mtype == "execute":
                    actions = msg["actions"]
                    results = executor.execute_all(actions)
                    await ws.send(json.dumps({
                        "type": "tool_results",
                        "results": results,
                    }))

                elif mtype == "turn_end":
                    turn_done.set()

                elif mtype == "error":
                    log.error(f"Error del servidor: {msg.get('text')}")
                    tts.speak("Hubo un error en el servidor.")
                    turn_done.set()  # desbloquear aunque haya error

                elif mtype == "info":
                    log.info(f"[servidor] {msg.get('text')}")

                elif mtype == "pong":
                    log.debug("pong")

                else:
                    log.warning(f"Mensaje desconocido: {msg}")

            # Tarea de fondo: recibe mensajes del servidor
            async def receiver():
                async for raw in ws:
                    msg = json.loads(raw)
                    await handle_server_message(msg)

            recv_task = asyncio.create_task(receiver())
            loop = asyncio.get_running_loop()

            try:
                while True:
                    # Esperar a que el turno anterior termine
                    try:
                        await asyncio.wait_for(turn_done.wait(), timeout=TURN_TIMEOUT)
                    except asyncio.TimeoutError:
                        log.warning("Timeout esperando respuesta del servidor.")
                        turn_done.set()

                    print("\n" + "=" * 50)
                    print("  Enter → grabar voz  |  texto + Enter → modo texto")
                    print("  'salir' → cerrar     |  'reset' → borrar historial")
                    print("=" * 50)

                    user_input = await loop.run_in_executor(None, input, ">>> ")
                    user_input = user_input.strip()

                    if user_input.lower() == "salir":
                        break

                    if user_input.lower() == "reset":
                        await ws.send(json.dumps({"type": "reset"}))
                        continue

                    if user_input:
                        # Modo texto (debug sin micrófono)
                        text = user_input
                    else:
                        # Modo voz
                        audio = recorder.record_until_silence()
                        text = stt.transcribe(audio)
                        if not text:
                            print("(No se escuchó nada, intenta de nuevo)")
                            continue
                        print(f"Tú: {text}")

                        # Filtro de wake word (opcional; descomentar para activar)
                        # if WAKE_WORD and WAKE_WORD not in text.lower():
                        #     print(f"(wake word '{WAKE_WORD}' no detectado)")
                        #     continue

                    # Marcar turno como ocupado antes de enviar
                    turn_done.clear()
                    await ws.send(json.dumps({"type": "user_message", "text": text}))

            finally:
                recv_task.cancel()

    except (websockets.exceptions.ConnectionClosed, ConnectionRefusedError) as e:
        log.error(f"No pude conectar al servidor: {e}")
        log.error("Asegúrate de que el servidor esté corriendo: python server/server.py")
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nAdiós")
