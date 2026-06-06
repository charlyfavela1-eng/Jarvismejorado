"""
Servidor Jarvis.

Expone un WebSocket en /ws. El cliente:
  1. Conecta.
  2. Manda mensajes tipo {"type": "user_message", "text": "..."}
  3. Recibe {"type": "speech", "text": "..."} (lo que Jarvis dice)
             {"type": "execute", "actions": [...]}  (tools a ejecutar)
             {"type": "turn_end"}  (señal de fin de turno, no más tools)
  4. Devuelve {"type": "tool_results", "results": [...]} si recibió execute.
"""
import os
import json
import asyncio
import logging
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import uvicorn

load_dotenv(dotenv_path="../.env")

from claude_client import ClaudeClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("jarvis-server")

app = FastAPI(title="Jarvis Server")

RESET_AFTER_SECONDS = int(os.getenv("RESET_AFTER_MINUTES", "5")) * 60


@app.get("/health")
async def health():
    return {"ok": True, "model": os.getenv("CLAUDE_MODEL", "claude-haiku-4-5-20251001")}


@app.websocket("/ws")
async def ws_endpoint(ws: WebSocket):
    await ws.accept()
    log.info("Cliente conectado")
    claude = ClaudeClient()
    loop = asyncio.get_running_loop()
    last_activity = loop.time()

    async def inactivity_watcher():
        nonlocal last_activity
        while True:
            await asyncio.sleep(30)
            elapsed = loop.time() - last_activity
            if elapsed > RESET_AFTER_SECONDS:
                claude.reset()
                last_activity = loop.time()
                log.info(f"Historial reiniciado por inactividad ({elapsed:.0f}s)")
                try:
                    await ws.send_json({
                        "type": "info",
                        "text": "Historial reiniciado por inactividad.",
                    })
                except Exception:
                    break

    watcher = asyncio.create_task(inactivity_watcher())

    try:
        while True:
            raw = await ws.receive_text()
            last_activity = loop.time()
            msg = json.loads(raw)
            log.info(f"<< {msg.get('type')}: {str(msg)[:200]}")

            if msg["type"] == "user_message":
                user_text = msg["text"]
                if not user_text.strip():
                    continue
                result = claude.chat(user_text)
                await _handle_claude_response(ws, claude, result)

            elif msg["type"] == "tool_results":
                result = claude.submit_tool_results(msg["results"])
                await _handle_claude_response(ws, claude, result)

            elif msg["type"] == "reset":
                claude.reset()
                await ws.send_json({"type": "info", "text": "Historial reiniciado."})

            elif msg["type"] == "ping":
                await ws.send_json({"type": "pong"})

            else:
                log.warning(f"Tipo de mensaje desconocido: {msg.get('type')}")

    except WebSocketDisconnect:
        log.info("Cliente desconectado")
    except Exception as e:
        log.exception(f"Error en WebSocket: {e}")
        try:
            await ws.send_json({"type": "error", "text": str(e)})
        except Exception:
            pass
    finally:
        watcher.cancel()


async def _handle_claude_response(ws: WebSocket, claude: ClaudeClient, result: dict):
    """
    Traduce la respuesta de Claude a mensajes para el cliente.
    Siempre termina con turn_end cuando no quedan tools pendientes.
    """
    if result["speech"]:
        await ws.send_json({"type": "speech", "text": result["speech"]})
        log.info(f">> speech: {result['speech'][:100]}")

    if result["actions"]:
        await ws.send_json({"type": "execute", "actions": result["actions"]})
        log.info(f">> execute: {len(result['actions'])} acción(es)")
    else:
        # No hay más tools que ejecutar → fin de turno
        await ws.send_json({"type": "turn_end"})


if __name__ == "__main__":
    host = os.getenv("SERVER_HOST", "127.0.0.1")
    port = int(os.getenv("SERVER_PORT", "8000"))
    log.info(f"Iniciando Jarvis Server en {host}:{port}")
    uvicorn.run("server:app", host=host, port=port, reload=False)
