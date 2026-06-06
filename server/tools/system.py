"""
Tools de sistema: abrir apps, controlar ventanas, ejecutar atajos de teclado.
"""

SYSTEM_TOOLS = [
    {
        "name": "open_app",
        "description": (
            "Abre una aplicación de Windows por su nombre. "
            "Funciona para apps comunes (notepad, chrome, spotify) y para "
            "rutas completas a ejecutables."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "app_name": {
                    "type": "string",
                    "description": "Nombre o ruta del ejecutable (ej: 'notepad', 'chrome', 'C:\\path\\app.exe')",
                }
            },
            "required": ["app_name"],
        },
    },
    {
        "name": "close_window",
        "description": "Cierra la ventana activa o una ventana específica por título.",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Título parcial de la ventana. Si se omite, cierra la activa.",
                }
            },
        },
    },
    {
        "name": "focus_window",
        "description": "Pone una ventana al frente buscándola por título parcial.",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Título parcial de la ventana a enfocar.",
                }
            },
            "required": ["title"],
        },
    },
    {
        "name": "press_hotkey",
        "description": (
            "Ejecuta una combinación de teclas. Útil para atajos como ctrl+c, "
            "alt+tab, win+d, etc."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "keys": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Lista de teclas a presionar a la vez. Ej: ['ctrl','shift','t']",
                }
            },
            "required": ["keys"],
        },
    },
    {
        "name": "type_text",
        "description": "Escribe texto donde esté el cursor.",
        "input_schema": {
            "type": "object",
            "properties": {
                "text": {"type": "string"},
            },
            "required": ["text"],
        },
    },
    {
        "name": "list_open_windows",
        "description": "Devuelve la lista de ventanas abiertas con sus títulos.",
        "input_schema": {"type": "object", "properties": {}},
    },
]
