# ═══════════════════════════════════════════════════════
# TOOLS — Funciones que los agentes pueden invocar solos
# El orquestador decide cuándo y cuál usar.
# ═══════════════════════════════════════════════════════
from .resolver_problema_con_multimodel import resolver_problema_con_multimodel


async def resolver_problema_facturacion(descripcion: str) -> str:
    """
    Consulta al experto externo gemini para resolver problemas de
    facturación, cobros, pagos o disputas financieras.

    Args:
        descripcion: Descripción detallada del problema de facturación.

    Returns:
        Solución del área de facturación paso a paso.
    """
    prompt = f"""
Eres un especialista en facturación, cobros y disputas financieras.
Analiza el siguiente problema y proporciona:
1. Causa probable del inconveniente
2. Pasos para resolverlo desde el área de facturación
3. Acción recomendada para el cliente

Problema: {descripcion}
"""
    return await resolver_problema_con_multimodel(prompt)