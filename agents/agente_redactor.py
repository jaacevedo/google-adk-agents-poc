from google.adk.agents import LlmAgent

from model_wrapper.wrappers import AzureFoundryWrapper
# ═══════════════════════════════════════════════════════
# AGENTES
# ═══════════════════════════════════════════════════════
modelo_azure_central = AzureFoundryWrapper()
# --- Agente Redactor (sub-agente) ---
# Recibe la solución validada por el humano y la convierte
# en una respuesta empática para el cliente.
agente_redactor = LlmAgent(
    name="AgenteRedactor",
    model=modelo_azure_central,#"gemini-2.5-flash",
    instruction="""
Eres un redactor profesional de soporte al cliente.
Recibirás una solución técnica o de facturación ya validada por un auditor humano.

Tu tarea:
- Redactar una respuesta final empática, clara y profesional dirigida al cliente.
- Usar un tono cálido y comprensivo.
- No agregar información nueva, solo mejorar la forma y el tono.
- Estructurar la respuesta con: saludo, solución clara, cierre amable.
"""
)