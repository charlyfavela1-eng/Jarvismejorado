"""
Demo interactivo de Jarvis — sin API key.
El cerebro de IA está embebido aquí (reglas + NLP básico).
La ejecución está simulada con output realista.

Uso:
    python demo.py
"""
import re
import json
import asyncio
import logging
import sys
from typing import Optional

logging.basicConfig(level=logging.WARNING)

# ─── Colores terminal ────────────────────────────────────────────────────────
R = "\033[91m"; G = "\033[92m"; Y = "\033[93m"; B = "\033[94m"
C = "\033[96m"; W = "\033[97m"; DIM = "\033[2m"; RESET = "\033[0m"
BOLD = "\033[1m"


# ─── Cerebro mock (sin API) ──────────────────────────────────────────────────

APP_MAP = {
    "youtube":      ("chrome", "https://youtube.com"),
    "google":       ("chrome", "https://google.com"),
    "gmail":        ("chrome", "https://mail.google.com"),
    "spotify":      ("spotify", None),
    "chrome":       ("chrome", None),
    "firefox":      ("firefox", None),
    "notepad":      ("notepad", None),
    "bloc de notas":("notepad", None),
    "calculadora":  ("calc", None),
    "discord":      ("discord", None),
    "vs code":      ("code", None),
    "vscode":       ("code", None),
    "explorador":   ("explorer", None),
    "after effects":("afterfx", None),
    "premiere":     ("premiere", None),
    "photoshop":    ("photoshop", None),
    "word":         ("winword", None),
    "excel":        ("excel", None),
    "zoom":         ("zoom", None),
    "teams":        ("teams", None),
    "whatsapp":     ("whatsapp", None),
    "telegram":     ("telegram", None),
    "obs":          ("obs64", None),
    "paint":        ("mspaint", None),
}

def _find_app(text: str) -> Optional[tuple]:
    for key, val in APP_MAP.items():
        if key in text:
            return (key, val[0], val[1])
    return None


def brain(user_text: str) -> dict:
    """
    Cerebro mock: analiza el texto y decide qué herramienta llamar.
    Devuelve el mismo formato que ClaudeClient.chat().
    """
    t = user_text.lower().strip()

    # ── ABRIR APP / URL ──────────────────────────────────────────────────────
    open_match = re.search(
        r'(abre|abrir|lanza|lanzar|inicia|iniciar|pon|abre|ejecuta)\s+(.+)',
        t
    )
    if open_match:
        target = open_match.group(2).strip().rstrip(".")
        app_info = _find_app(target)

        if app_info:
            _, app_cmd, url = app_info
            actions = [{"id": "a1", "name": "open_app",
                        "input": {"app_name": app_cmd}}]
            if url:
                actions += [
                    {"id": "a2", "name": "press_hotkey",
                     "input": {"keys": ["ctrl", "l"]}},
                    {"id": "a3", "name": "type_text",
                     "input": {"text": url}},
                    {"id": "a4", "name": "press_hotkey",
                     "input": {"keys": ["enter"]}},
                ]
            return {
                "speech": f"{app_info[0].title()} abierto.",
                "actions": actions,
                "stop_reason": "tool_use",
            }
        else:
            return {
                "speech": f"Abriendo {target}.",
                "actions": [{"id": "a1", "name": "open_app",
                              "input": {"app_name": target}}],
                "stop_reason": "tool_use",
            }

    # ── CERRAR ───────────────────────────────────────────────────────────────
    close_match = re.search(r'(cierra|cerrar)\s*(.*)', t)
    if close_match:
        title = close_match.group(2).strip() or None
        inp = {"title": title} if title else {}
        speech = f"'{title}' cerrado." if title else "Ventana activa cerrada."
        return {
            "speech": speech,
            "actions": [{"id": "a1", "name": "close_window", "input": inp}],
            "stop_reason": "tool_use",
        }

    # ── LISTAR VENTANAS ──────────────────────────────────────────────────────
    if any(w in t for w in ["lista", "qué ventanas", "que ventanas",
                             "ventanas abiertas", "qué hay abierto"]):
        return {
            "speech": "Te muestro las ventanas abiertas.",
            "actions": [{"id": "a1", "name": "list_open_windows", "input": {}}],
            "stop_reason": "tool_use",
        }

    # ── ESCRIBIR TEXTO ───────────────────────────────────────────────────────
    write_match = re.search(r'(escribe|escribir|tipea|tipear|pon el texto|type)\s+(.+)', t)
    if write_match:
        texto = write_match.group(2).strip().rstrip(".")
        return {
            "speech": f"Escrito: {texto}",
            "actions": [{"id": "a1", "name": "type_text",
                         "input": {"text": texto}}],
            "stop_reason": "tool_use",
        }

    # ── HOTKEYS ──────────────────────────────────────────────────────────────
    hotkey_patterns = {
        r'ctrl\+?c|copiar':           ["ctrl", "c"],
        r'ctrl\+?v|pegar':            ["ctrl", "v"],
        r'ctrl\+?z|deshacer':         ["ctrl", "z"],
        r'ctrl\+?s|guardar':          ["ctrl", "s"],
        r'ctrl\+?a|seleccionar todo': ["ctrl", "a"],
        r'alt\+?tab':                 ["alt", "tab"],
        r'alt\+?f4|cerrar ventana':   ["alt", "f4"],
        r'win\+?d|escritorio':        ["win", "d"],
        r'win\+?l|bloquear':          ["win", "l"],
        r'imprimir|screenshot|captura':["win", "shift", "s"],
        r'maximizar':                  ["win", "up"],
        r'minimizar':                  ["win", "down"],
        r'pantalla completa':          ["f11"],
    }
    for pattern, keys in hotkey_patterns.items():
        if re.search(pattern, t):
            combo = "+".join(keys)
            return {
                "speech": f"{combo} presionado.",
                "actions": [{"id": "a1", "name": "press_hotkey",
                              "input": {"keys": keys}}],
                "stop_reason": "tool_use",
            }

    # ── AFTER EFFECTS ────────────────────────────────────────────────────────
    if "after effects" in t or "composición" in t or "composition" in t:
        # Nueva composición
        # Extraer nombre primero (va después de "llamada")
        name_match = re.search(r'llamad[ao]\s+["\']?([A-Za-z0-9_\- áéíóúüñÁÉÍÓÚÜÑ]+)', t)
        w = re.search(r'(\d{3,4})\s*(?:x|por)\s*(\d{3,4})', t)
        dur = re.search(r'(\d+)\s*(?:seg|segundo|s\b)', t)
        name = name_match.group(1).strip() if name_match else "Mi Comp"
        width = int(w.group(1)) if w else 1920
        height = int(w.group(2)) if w else 1080
        duration = float(dur.group(1)) if dur else 10.0
        return {
            "speech": f"Composición '{name}' creada en After Effects.",
            "actions": [{"id": "a1", "name": "ae_new_composition",
                         "input": {"name": name, "width": width,
                                   "height": height, "duration": duration}}],
            "stop_reason": "tool_use",
        }

    # ── CONVERSACIONAL ───────────────────────────────────────────────────────
    greetings = ["hola", "hey", "buenos", "buenas"]
    if any(t.startswith(g) for g in greetings):
        return {
            "speech": "Hola. Dime qué necesitas.",
            "actions": [],
            "stop_reason": "end_turn",
        }

    if any(w in t for w in ["qué puedes", "que puedes", "qué sabes", "ayuda", "help"]):
        return {
            "speech": (
                "Puedo abrir apps, controlar ventanas, escribir texto, "
                "ejecutar atajos de teclado y controlar After Effects. "
                "Di por ejemplo: abre YouTube, o escribe Hola Mundo."
            ),
            "actions": [],
            "stop_reason": "end_turn",
        }

    if any(w in t for w in ["gracias", "thanks"]):
        return {"speech": "De nada.", "actions": [], "stop_reason": "end_turn"}

    # Fallback
    return {
        "speech": (
            "Entendido. No reconocí un comando específico. "
            "Prueba: 'abre YouTube', 'lista ventanas', 'escribe Hola'."
        ),
        "actions": [],
        "stop_reason": "end_turn",
    }


def brain_after_tools(results: list) -> dict:
    """Respuesta final después de ejecutar las herramientas."""
    errors = [r for r in results if r.get("is_error")]
    if errors:
        return {
            "speech": "Algunas acciones fallaron. Revisa la consola.",
            "actions": [],
            "stop_reason": "end_turn",
        }
    return {"speech": "", "actions": [], "stop_reason": "end_turn"}


# ─── Ejecutor simulado (Linux-compatible) ────────────────────────────────────

def simulate_action(action: dict) -> dict:
    name = action["name"]
    inp  = action.get("input", {})

    print(f"  {DIM}⚙  {name}({json.dumps(inp, ensure_ascii=False)}){RESET}")

    if name == "open_app":
        app = inp.get("app_name", "")
        # En Linux intentamos xdg-open si es un exe conocido
        import subprocess, os
        linux_map = {
            "chrome": "google-chrome",
            "firefox": "firefox",
            "code": "code",
            "calc": "gnome-calculator",
            "notepad": "gedit",
            "explorer": "nautilus",
        }
        linux_cmd = linux_map.get(app.lower().replace(".exe", ""))
        if linux_cmd:
            try:
                subprocess.Popen([linux_cmd], stdout=subprocess.DEVNULL,
                                  stderr=subprocess.DEVNULL)
                return {"tool_use_id": action["id"],
                        "content": f"OK: {app} abierto", "is_error": False}
            except FileNotFoundError:
                pass
        return {"tool_use_id": action["id"],
                "content": f"[SIMULADO en Linux] {app} se abriría en Windows",
                "is_error": False}

    if name == "type_text":
        text = inp.get("text", "")
        print(f"  {DIM}   → texto: {text!r}{RESET}")
        return {"tool_use_id": action["id"],
                "content": f"OK: escrito '{text}'", "is_error": False}

    if name == "press_hotkey":
        keys = inp.get("keys", [])
        print(f"  {DIM}   → teclas: {'+'.join(keys)}{RESET}")
        return {"tool_use_id": action["id"],
                "content": f"OK: {'+'.join(keys)}", "is_error": False}

    if name == "list_open_windows":
        import subprocess
        try:
            out = subprocess.check_output(["wmctrl", "-l"], text=True,
                                           stderr=subprocess.DEVNULL)
            titles = [l.split(None, 3)[-1] for l in out.strip().splitlines() if l]
            content = "Ventanas:\n- " + "\n- ".join(titles[:15]) if titles else "Sin ventanas"
        except Exception:
            content = "Ventanas abiertas:\n- Visual Studio Code\n- Terminal\n- Chrome  [simulado]"
        return {"tool_use_id": action["id"], "content": content, "is_error": False}

    if name == "close_window":
        title = inp.get("title", "activa")
        return {"tool_use_id": action["id"],
                "content": f"OK: '{title}' cerrada", "is_error": False}

    if name == "focus_window":
        return {"tool_use_id": action["id"],
                "content": f"OK: '{inp.get('title')}' al frente",
                "is_error": False}

    if name.startswith("ae_"):
        return {"tool_use_id": action["id"],
                "content": f"[After Effects] {name} ejecutado OK",
                "is_error": False}

    return {"tool_use_id": action["id"],
            "content": f"OK: {name}", "is_error": False}


# ─── Loop principal ───────────────────────────────────────────────────────────

def run():
    print(f"\n{BOLD}{C}╔══════════════════════════════════════════╗{RESET}")
    print(f"{BOLD}{C}║        JARVIS  —  Modo Demo              ║{RESET}")
    print(f"{BOLD}{C}║   (sin API key, cerebro local embebido)  ║{RESET}")
    print(f"{BOLD}{C}╚══════════════════════════════════════════╝{RESET}")
    print(f"\n{DIM}Escribe un comando. 'salir' para terminar.{RESET}\n")

    examples = [
        "abre YouTube",
        "abre el bloc de notas",
        "lista las ventanas abiertas",
        "escribe Hola Mundo",
        "ctrl+s",
        "qué puedes hacer",
    ]
    print(f"{DIM}Ejemplos:{RESET}")
    for ex in examples:
        print(f"  {DIM}→ {ex}{RESET}")
    print()

    history = []

    while True:
        try:
            user = input(f"{BOLD}{Y}Tú:{RESET} ").strip()
        except (EOFError, KeyboardInterrupt):
            print(f"\n{DIM}Adiós.{RESET}")
            break

        if not user:
            continue
        if user.lower() in ("salir", "exit", "quit"):
            print(f"{DIM}Adiós.{RESET}")
            break
        if user.lower() == "reset":
            history.clear()
            print(f"{DIM}Historial borrado.{RESET}\n")
            continue

        history.append({"role": "user", "text": user})

        # ── Turno del cerebro ─────────────────────────────────────────────
        result = brain(user)

        # Voz
        if result["speech"]:
            print(f"{BOLD}{C}Jarvis:{RESET} {result['speech']}")

        # Herramientas
        if result["actions"]:
            tool_results = []
            for action in result["actions"]:
                res = simulate_action(action)
                tool_results.append(res)
                if not res["is_error"]:
                    print(f"  {G}✓{RESET} {res['content']}")
                else:
                    print(f"  {R}✗{RESET} {res['content']}")

            # Segunda vuelta del cerebro tras ejecutar herramientas
            followup = brain_after_tools(tool_results)
            if followup["speech"]:
                print(f"{BOLD}{C}Jarvis:{RESET} {followup['speech']}")

        history.append({"role": "jarvis", "speech": result["speech"]})
        print()


if __name__ == "__main__":
    run()
