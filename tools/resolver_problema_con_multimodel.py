import asyncio

from tools import llamar_model

async def resolver_problema_con_multimodel(messages: str) -> str:
    """Llama a varios modelos en paralelo y devuelve la primera respuesta válida"""
    resultados = await asyncio.gather(
        asyncio.to_thread(llamar_model.generar_respuesta, messages),
        return_exceptions=True
    )
    # Filtrar errores
    textos = [r for r in resultados if not isinstance(r, Exception)]
    if not textos:
        return "No se pudo obtener respuesta de los modelos."
    return textos[0]  


