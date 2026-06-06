"""
Definiciones de las tools que Claude puede llamar.
Estas definiciones se mandan al API; la ejecución real ocurre en el CLIENTE
(porque solo el cliente tiene acceso al Windows del usuario).
"""
from .system import SYSTEM_TOOLS
from .after_effects import AE_TOOLS

ALL_TOOLS = SYSTEM_TOOLS + AE_TOOLS
