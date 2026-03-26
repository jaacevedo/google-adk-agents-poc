from google.adk.agents import LlmAgent
from agents.agente_resolutor import agente_resolutor
from agents.agente_redactor import agente_redactor
from model_wrapper.wrappers import AzureFoundryWrapper
# ═══════════════════════════════════════════════════════
# AGENTES
# ═══════════════════════════════════════════════════════

modelo_azure_central = AzureFoundryWrapper()

# --- Orquestador principal ---
# El cerebro del flujo. Coordina a los sub-agentes,
# les habla y les pasa contexto directamente.
orquestador = LlmAgent(
    name="Orquestador",
    model=modelo_azure_central,#"gemini-2.5-flash",
    sub_agents=[agente_resolutor, agente_redactor],
    instruction="""
Eres el coordinador del sistema de soporte de Glosas IG Services.

REGLAS ESTRICTAS:
- NUNCA resumas, acortes ni parafrasees las respuestas de los sub-agentes.
- Siempre devuelve el texto COMPLETO tal como lo entrego el sub-agente.
- No agregues frases como "Le informaremos..." ni comentarios propios al final.

Tu flujo de trabajo es:
1. Recibe el ticket del cliente.
2. Transfiere el ticket completo al AgenteResolutor.
3. Devuelve la respuesta COMPLETA del AgenteResolutor, sin modificarla ni agregar nada.

Cuando recibas una solucion validada para redactar:
1. Transfiere la solucion completa al AgenteRedactor.
2. Devuelve la respuesta COMPLETA del AgenteRedactor, sin modificarla ni agregar nada.
"""
)