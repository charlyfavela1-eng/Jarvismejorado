"""
Wrapper de la API de Claude.
Mantiene el historial de la conversación y gestiona tool use.
"""
import os
from anthropic import Anthropic
from tools import ALL_TOOLS

SYSTEM_PROMPT = """Eres Jarvis, un asistente de voz que controla una PC con Windows.

Reglas:
- Respondes en español, breve y directo (1-2 frases máximo). Tu salida se va a leer en voz alta.
- Cuando el usuario te pida hacer algo en la PC (abrir apps, controlar ventanas, editar video en After Effects), usas las tools disponibles.
- Si una tool falla, intentas una alternativa o avisas al usuario.
- No hagas preámbulos tipo "Claro, voy a..." — actúa y reporta en pasado: "Bloc de notas abierto."
- Si el usuario solo conversa, responde corto sin usar tools.
"""


class ClaudeClient:
    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError("Falta ANTHROPIC_API_KEY en el .env")

        self.client = Anthropic(api_key=api_key)
        self.model = os.getenv("CLAUDE_MODEL", "claude-haiku-4-5-20251001")
        self.history: list[dict] = []

    def reset(self):
        """Limpia el historial (por ejemplo, después de un periodo de silencio)."""
        self.history = []

    def chat(self, user_text: str) -> dict:
        """
        Manda el texto del usuario a Claude.
        Devuelve un dict con:
          - 'speech': lo que Jarvis debe decir en voz alta
          - 'actions': lista de tool_use bloques que el cliente debe ejecutar
        """
        self.history.append({"role": "user", "content": user_text})

        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            tools=ALL_TOOLS,
            messages=self.history,
        )

        # Guardar la respuesta del asistente en el historial
        self.history.append({"role": "assistant", "content": response.content})

        # Separar texto hablado y tool calls
        speech_parts = []
        actions = []
        for block in response.content:
            if block.type == "text":
                speech_parts.append(block.text)
            elif block.type == "tool_use":
                actions.append({
                    "id": block.id,
                    "name": block.name,
                    "input": block.input,
                })

        return {
            "speech": " ".join(speech_parts).strip(),
            "actions": actions,
            "stop_reason": response.stop_reason,
        }

    def submit_tool_results(self, results: list[dict]) -> dict:
        """
        Después de que el cliente ejecutó las tools, manda los resultados
        de vuelta a Claude para que continúe el razonamiento.

        results: [{"tool_use_id": "...", "content": "...", "is_error": bool}]
        """
        self.history.append({
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": r["tool_use_id"],
                    "content": r["content"],
                    "is_error": r.get("is_error", False),
                }
                for r in results
            ],
        })

        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            tools=ALL_TOOLS,
            messages=self.history,
        )

        self.history.append({"role": "assistant", "content": response.content})

        speech_parts = []
        actions = []
        for block in response.content:
            if block.type == "text":
                speech_parts.append(block.text)
            elif block.type == "tool_use":
                actions.append({
                    "id": block.id,
                    "name": block.name,
                    "input": block.input,
                })

        return {
            "speech": " ".join(speech_parts).strip(),
            "actions": actions,
            "stop_reason": response.stop_reason,
        }
