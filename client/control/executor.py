"""
Recibe las 'actions' que mandó el servidor y las ejecuta llamando
al módulo correcto. Devuelve los resultados para mandar de vuelta.
"""
import logging
from control import system
from ae_bridge import runner as ae

log = logging.getLogger("control.executor")


def execute_action(action: dict) -> dict:
    """
    action = {'id': '...', 'name': '...', 'input': {...}}
    return = {'tool_use_id': '...', 'content': '...', 'is_error': bool}
    """
    name = action["name"]
    inp = action.get("input", {})
    log.info(f"⚙️  Ejecutando {name}({inp})")

    try:
        if name == "open_app":
            result = system.open_app(**inp)
        elif name == "close_window":
            result = system.close_window(**inp)
        elif name == "focus_window":
            result = system.focus_window(**inp)
        elif name == "press_hotkey":
            result = system.press_hotkey(**inp)
        elif name == "type_text":
            result = system.type_text(**inp)
        elif name == "list_open_windows":
            result = system.list_open_windows()

        # After Effects
        elif name == "ae_launch":
            result = ae.launch_ae()
        elif name == "ae_new_composition":
            result = ae.new_composition(**inp)
        elif name == "ae_add_text_layer":
            result = ae.add_text_layer(**inp)
        elif name == "ae_render_active_comp":
            result = ae.render_active_comp(**inp)
        elif name == "ae_run_jsx":
            result = ae.run_jsx(**inp)

        else:
            return {
                "tool_use_id": action["id"],
                "content": f"Tool desconocida: {name}",
                "is_error": True,
            }

        is_err = isinstance(result, str) and result.startswith("ERROR")
        return {
            "tool_use_id": action["id"],
            "content": result,
            "is_error": is_err,
        }

    except Exception as e:
        log.exception(f"Excepción en {name}")
        return {
            "tool_use_id": action["id"],
            "content": f"ERROR excepción: {e}",
            "is_error": True,
        }


def execute_all(actions: list[dict]) -> list[dict]:
    return [execute_action(a) for a in actions]
