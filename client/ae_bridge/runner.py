"""
Puente a After Effects.

Estrategia: generamos archivos .jsx temporales y los ejecutamos con
`AfterFX.exe -r <ruta_jsx>`. AE debe estar instalado en la ruta de AE_PATH.

Nota: AE debe tener "Allow Scripts to Write Files and Access Network"
habilitado (Edit > Preferences > Scripting & Expressions).
"""
import os
import platform
import subprocess
import tempfile
import logging
import time

log = logging.getLogger("ae_bridge.runner")

_PLATFORM = platform.system()
_DEFAULT_AE_PATH = (
    "/Applications/Adobe After Effects 2024/AfterFX.app/Contents/MacOS/AfterFX"
    if _PLATFORM == "Darwin"
    else r"C:\Program Files\Adobe\Adobe After Effects 2024\Support Files\AfterFX.exe"
)

AE_PATH = os.getenv("AE_PATH", _DEFAULT_AE_PATH)


def _run_jsx_code(jsx_code: str) -> str:
    """Escribe jsx_code a un archivo temporal y lo ejecuta en AE."""
    if not os.path.exists(AE_PATH):
        return f"ERROR: AE_PATH no existe: {AE_PATH}"

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".jsx", delete=False, encoding="utf-8"
    ) as f:
        f.write(jsx_code)
        jsx_path = f.name

    try:
        # -r ejecuta el script sin abrir nueva instancia si AE ya está abierto
        subprocess.Popen([AE_PATH, "-r", jsx_path])
        log.info(f"JSX lanzado: {jsx_path}")
        return f"OK: script ejecutado en AE"
    except Exception as e:
        return f"ERROR ejecutando JSX: {e}"


def launch_ae() -> str:
    if not os.path.exists(AE_PATH):
        return f"ERROR: AE no encontrado en {AE_PATH}"
    try:
        subprocess.Popen([AE_PATH])
        time.sleep(2)
        return "OK: After Effects lanzado"
    except Exception as e:
        return f"ERROR lanzando AE: {e}"


def new_composition(name: str, width: int, height: int, duration: float, frame_rate: float = 30) -> str:
    jsx = f"""
    app.beginUndoGroup("Jarvis: New Comp");
    var comp = app.project.items.addComp("{name}", {width}, {height}, 1, {duration}, {frame_rate});
    comp.openInViewer();
    app.endUndoGroup();
    """
    return _run_jsx_code(jsx)


def add_text_layer(text: str, font_size: int = 72, color: list = None) -> str:
    if color is None:
        color = [1, 1, 1]
    r, g, b = color[0], color[1], color[2]
    # Escapar comillas
    safe_text = text.replace('"', '\\"')
    jsx = f"""
    app.beginUndoGroup("Jarvis: Add Text");
    var comp = app.project.activeItem;
    if (comp && comp instanceof CompItem) {{
        var layer = comp.layers.addText("{safe_text}");
        var sourceText = layer.property("Source Text");
        var textDocument = sourceText.value;
        textDocument.fontSize = {font_size};
        textDocument.fillColor = [{r}, {g}, {b}];
        sourceText.setValue(textDocument);
    }} else {{
        alert("No hay composición activa");
    }}
    app.endUndoGroup();
    """
    return _run_jsx_code(jsx)


def render_active_comp(output_path: str) -> str:
    safe_path = output_path.replace("\\", "\\\\")
    jsx = f"""
    app.beginUndoGroup("Jarvis: Render");
    var comp = app.project.activeItem;
    if (comp && comp instanceof CompItem) {{
        var rq = app.project.renderQueue;
        var item = rq.items.add(comp);
        item.outputModule(1).file = new File("{safe_path}");
        rq.render();
    }} else {{
        alert("No hay composición activa para renderizar");
    }}
    app.endUndoGroup();
    """
    return _run_jsx_code(jsx)


def run_jsx(jsx_code: str) -> str:
    """Ejecuta código JSX arbitrario. Útil para casos no cubiertos por tools."""
    return _run_jsx_code(jsx_code)
