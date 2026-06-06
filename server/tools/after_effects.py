"""
Tools de After Effects.

La estrategia: cada tool genera/elige un .jsx (ExtendScript) y el cliente
lo ejecuta vía `AfterFX.exe -r script.jsx` o vía COM en Windows.

Empezamos con tools básicas. A medida que crezca, se pueden agregar más.
"""

AE_TOOLS = [
    {
        "name": "ae_launch",
        "description": "Abre Adobe After Effects si no está abierto.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "ae_new_composition",
        "description": "Crea una nueva composición en After Effects con los parámetros dados.",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Nombre de la composición"},
                "width": {"type": "integer", "description": "Ancho en píxeles (ej: 1920)"},
                "height": {"type": "integer", "description": "Alto en píxeles (ej: 1080)"},
                "duration": {"type": "number", "description": "Duración en segundos"},
                "frame_rate": {"type": "number", "description": "FPS (ej: 30)", "default": 30},
            },
            "required": ["name", "width", "height", "duration"],
        },
    },
    {
        "name": "ae_add_text_layer",
        "description": "Agrega una capa de texto a la composición activa.",
        "input_schema": {
            "type": "object",
            "properties": {
                "text": {"type": "string"},
                "font_size": {"type": "integer", "default": 72},
                "color": {
                    "type": "array",
                    "items": {"type": "number"},
                    "description": "RGB normalizado [0-1], ej: [1, 1, 1] para blanco",
                    "default": [1, 1, 1],
                },
            },
            "required": ["text"],
        },
    },
    {
        "name": "ae_render_active_comp",
        "description": "Renderiza la composición activa al archivo de salida especificado.",
        "input_schema": {
            "type": "object",
            "properties": {
                "output_path": {
                    "type": "string",
                    "description": "Ruta absoluta del archivo de salida (.mov o .mp4)",
                }
            },
            "required": ["output_path"],
        },
    },
    {
        "name": "ae_run_jsx",
        "description": (
            "Escotilla de escape: ejecuta código ExtendScript (.jsx) crudo en AE. "
            "Úsalo cuando necesites algo que las tools específicas no cubren."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "jsx_code": {"type": "string", "description": "Código ExtendScript a ejecutar"},
            },
            "required": ["jsx_code"],
        },
    },
]
