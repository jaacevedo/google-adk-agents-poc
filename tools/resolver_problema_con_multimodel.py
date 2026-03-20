import asyncio

from tools import llamar_gpt4

async def resolver_problema_con_multimodel(messages: str) -> str:
    """Llama a varios modelos en paralelo y devuelve la primera respuesta válida"""
    resultados = await asyncio.gather(
        llamar_gpt4(messages, "gpt-4o-mini"),
        ##llamar_gpt4(messages, "gpt-4o"),
        return_exceptions=True
    )
    # Filtrar errores
    textos = [r for r in resultados if not isinstance(r, Exception)]
    if not textos:
        return "No se pudo obtener respuesta de los modelos."
    return textos[0]  # prioriza GPT-4 sobre Gemini/Claude

    #return await llamar_gpt4(messages, "gpt-4o-mini")


