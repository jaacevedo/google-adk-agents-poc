
# ═══════════════════════════════════════════════════════
# TOOLS — Funciones que los agentes pueden invocar solos
# El orquestador decide cuándo y cuál usar.
# ═══════════════════════════════════════════════════════
from .resolver_problema_con_multimodel import resolver_problema_con_multimodel


async def resolver_problema_tecnico(descripcion: str) -> str:
    """
    Consulta al experto externo gemini para resolver problemas técnicos
    de infraestructura, APIs, errores de sistema o conectividad.

    Args:
        descripcion: Descripción detallada del problema técnico.

    Returns:
        Solución técnica paso a paso.
    """
    prompt = f"""
Eres un ingeniero de soporte técnico senior especializado en infraestructura cloud y APIs.
Analiza el siguiente problema técnico y proporciona:
1. Diagnóstico probable
2. Pasos concretos para resolverlo
3. Recomendaciones para evitar recurrencia

Problema: {descripcion}
"""

    return await resolver_problema_con_multimodel(prompt)