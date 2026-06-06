"""
Acciones de control de sistema cross-platform (macOS / Windows).
"""
import os
import platform
import subprocess
import logging

log = logging.getLogger("control.system")
PLATFORM = platform.system()  # "Darwin" | "Windows" | "Linux"

# ─── App aliases ───────────────────────────────────────────────────────────────

APP_ALIASES_MAC: dict[str, str] = {
    "terminal": "Terminal",
    "finder": "Finder",
    "safari": "Safari",
    "chrome": "Google Chrome",
    "google chrome": "Google Chrome",
    "firefox": "Firefox",
    "calculadora": "Calculator",
    "calculator": "Calculator",
    "notas": "Notes",
    "notes": "Notes",
    "correo": "Mail",
    "mail": "Mail",
    "vs code": "Visual Studio Code",
    "vscode": "Visual Studio Code",
    "visual studio code": "Visual Studio Code",
    "discord": "Discord",
    "slack": "Slack",
    "zoom": "zoom.us",
    "spotify": "Spotify",
    "vlc": "VLC",
    "obs": "OBS",
    "whatsapp": "WhatsApp",
    "telegram": "Telegram",
    "photoshop": "Adobe Photoshop 2024",
    "illustrator": "Adobe Illustrator 2024",
    "premiere": "Adobe Premiere Pro 2024",
    "after effects": "Adobe After Effects 2024",
    "xcode": "Xcode",
    "figma": "Figma",
    "music": "Music",
    "musica": "Music",
    "mensajes": "Messages",
    "messages": "Messages",
    "facetime": "FaceTime",
}

APP_ALIASES_WIN: dict[str, str] = {
    "notepad": "notepad.exe",
    "bloc de notas": "notepad.exe",
    "calculadora": "calc.exe",
    "calculator": "calc.exe",
    "explorador": "explorer.exe",
    "explorer": "explorer.exe",
    "explorador de archivos": "explorer.exe",
    "paint": "mspaint.exe",
    "cmd": "cmd.exe",
    "terminal": "cmd.exe",
    "powershell": "powershell.exe",
    "task manager": "taskmgr.exe",
    "administrador de tareas": "taskmgr.exe",
    "panel de control": "control.exe",
    "control panel": "control.exe",
    "configuración": "ms-settings:",
    "settings": "ms-settings:",
    "regedit": "regedit.exe",
    "chrome": "chrome.exe",
    "google chrome": "chrome.exe",
    "firefox": "firefox.exe",
    "edge": "msedge.exe",
    "microsoft edge": "msedge.exe",
    "word": "winword.exe",
    "excel": "excel.exe",
    "powerpoint": "powerpnt.exe",
    "outlook": "outlook.exe",
    "photoshop": "photoshop.exe",
    "illustrator": "illustrator.exe",
    "premiere": "adobe premiere pro.exe",
    "after effects": "afterfx.exe",
    "vs code": "code.exe",
    "vscode": "code.exe",
    "visual studio code": "code.exe",
    "discord": "discord.exe",
    "slack": "slack.exe",
    "zoom": "zoom.exe",
    "teams": "teams.exe",
    "microsoft teams": "teams.exe",
    "spotify": "spotify.exe",
    "vlc": "vlc.exe",
    "obs": "obs64.exe",
    "whatsapp": "whatsapp.exe",
    "telegram": "telegram.exe",
}


def open_app(app_name: str) -> str:
    key = app_name.lower().strip()
    try:
        if PLATFORM == "Darwin":
            alias = APP_ALIASES_MAC.get(key, app_name)
            subprocess.Popen(["open", "-a", alias])
        elif PLATFORM == "Windows":
            command = APP_ALIASES_WIN.get(key, app_name)
            if ":" in command and os.path.sep not in command:
                subprocess.Popen(f"start {command}", shell=True)
            else:
                subprocess.Popen(["start", "", command], shell=True)
        else:
            subprocess.Popen(["xdg-open", app_name])
        return f"OK: {app_name} abierto"
    except Exception as e:
        return f"ERROR abriendo {app_name}: {e}"


def _osascript(script: str) -> str:
    result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
    return result.stdout.strip()


def close_window(title: str | None = None) -> str:
    if PLATFORM == "Darwin":
        try:
            if title:
                script = f'tell application "{title}" to close front window'
            else:
                # Cmd+W cierra la ventana activa en cualquier app
                script = (
                    'tell application "System Events" to keystroke "w" '
                    'using command down'
                )
            _osascript(script)
            return "OK: ventana cerrada"
        except Exception as e:
            return f"ERROR cerrando ventana: {e}"
    else:
        try:
            import pygetwindow as gw
            if title:
                wins = gw.getWindowsWithTitle(title)
                if not wins:
                    return f"No encontré ventana con título '{title}'"
                wins[0].close()
                return f"OK: '{wins[0].title}' cerrada"
            active = gw.getActiveWindow()
            if not active:
                return "No hay ventana activa"
            active.close()
            return "OK: ventana activa cerrada"
        except Exception as e:
            return f"ERROR cerrando ventana: {e}"


def focus_window(title: str) -> str:
    if PLATFORM == "Darwin":
        try:
            _osascript(f'tell application "{title}" to activate')
            return f"OK: '{title}' al frente"
        except Exception as e:
            return f"ERROR enfocando ventana: {e}"
    else:
        try:
            import pygetwindow as gw
            wins = gw.getWindowsWithTitle(title)
            if not wins:
                return f"No encontré ventana con título '{title}'"
            w = wins[0]
            if w.isMinimized:
                w.restore()
            w.activate()
            return f"OK: '{w.title}' al frente"
        except Exception as e:
            return f"ERROR enfocando ventana: {e}"


def press_hotkey(keys: list[str]) -> str:
    try:
        import pyautogui
        pyautogui.hotkey(*keys)
        return f"OK: {'+'.join(keys)} presionado"
    except Exception as e:
        return f"ERROR con hotkey: {e}"


def type_text(text: str) -> str:
    try:
        import pyperclip
        import pyautogui
        import time
        prev = pyperclip.paste()
        pyperclip.copy(text)
        if PLATFORM == "Darwin":
            pyautogui.hotkey("command", "v")
        else:
            pyautogui.hotkey("ctrl", "v")
        time.sleep(0.15)
        pyperclip.copy(prev)
        return f"OK: escrito ({len(text)} chars)"
    except ImportError:
        try:
            import pyautogui
            pyautogui.typewrite(text, interval=0.02)
            return f"OK: escrito ({len(text)} chars) [solo ASCII]"
        except Exception as e:
            return f"ERROR escribiendo: {e}"
    except Exception as e:
        return f"ERROR escribiendo: {e}"


def list_open_windows() -> str:
    if PLATFORM == "Darwin":
        try:
            script = (
                'tell application "System Events" to get name of every '
                'application process whose visible is true'
            )
            result = _osascript(script)
            if not result:
                return "Sin aplicaciones visibles"
            apps = [a.strip() for a in result.split(",") if a.strip()]
            return "Aplicaciones abiertas:\n- " + "\n- ".join(apps[:25])
        except Exception as e:
            return f"ERROR listando ventanas: {e}"
    else:
        try:
            import pygetwindow as gw
            titles = [t for t in gw.getAllTitles() if t.strip()]
            if not titles:
                return "Sin ventanas abiertas"
            return "Ventanas abiertas:\n- " + "\n- ".join(titles[:25])
        except Exception as e:
            return f"ERROR listando ventanas: {e}"
