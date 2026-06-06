"""
Smoke test: prueba el servidor sin micrófono ni cliente completo.
Útil para verificar que Claude + tools funcionan antes de meterle audio.

Uso (con el servidor corriendo):
    python test_smoke.py "abre el bloc de notas"
    python test_smoke.py "lista las ventanas abiertas"
    python test_smoke.py "hola jarvis"
"""
import asyncio
import json
import sys
import websockets


async def main():
    if len(sys.argv) < 2:
        print("Uso: python test_smoke.py 'tu mensaje aquí'")
        sys.exit(1)

    message = " ".join(sys.argv[1:])
    url = "ws://127.0.0.1:8000/ws"

    print(f"→ Conectando a {url}...")
    async with websockets.connect(url) as ws:
        print(f"→ Enviando: {message!r}")
        await ws.send(json.dumps({"type": "user_message", "text": message}))

        try:
            while True:
                raw = await asyncio.wait_for(ws.recv(), timeout=15)
                msg = json.loads(raw)
                mtype = msg.get("type")

                if mtype == "speech":
                    print(f"🤖 Jarvis dice: {msg['text']}")

                elif mtype == "execute":
                    print(f"⚙️  Acciones pedidas ({len(msg['actions'])}):")
                    fake_results = []
                    for a in msg["actions"]:
                        print(f"   → {a['name']}({json.dumps(a['input'])})")
                        fake_results.append({
                            "tool_use_id": a["id"],
                            "content": f"[SIMULADO] {a['name']} ejecutado OK",
                            "is_error": False,
                        })
                    await ws.send(json.dumps({
                        "type": "tool_results",
                        "results": fake_results,
                    }))

                elif mtype == "turn_end":
                    print("✅ Turno completado")
                    break  # Conversación terminó

                elif mtype == "error":
                    print(f"❌ Error: {msg.get('text')}")
                    break

                else:
                    print(f"   [{mtype}] {msg}")

        except asyncio.TimeoutError:
            print("(timeout esperando respuesta)")


if __name__ == "__main__":
    asyncio.run(main())
