import os
import httpx
# ═══════════════════════════════════════════════════════
# TOOLS — Funciones que los agentes pueden invocar solos
# El orquestador decide cuándo y cuál usar.
# ═══════════════════════════════════════════════════════
def _obtener_adapter_server_url() -> str:
    configured_url = os.getenv("ADAPTER_SERVER_URL")
    if configured_url:
        return configured_url.rstrip("/")

    # En Cloud Run el proxy vive en el mismo contenedor en el puerto PORT.
    if os.getenv("K_SERVICE"):
        port = os.getenv("PORT", "8080")
        return f"http://127.0.0.1:{port}"

    # Otras plataformas serverless con puerto explicito.
    if os.getenv("RENDER") or os.getenv("RAILWAY_ENVIRONMENT"):
        port = os.getenv("PORT", "8001")
        return f"http://127.0.0.1:{port}"

    port = os.getenv("PORT", "8001")
    return f"http://127.0.0.1:{port}"



async def llamar_gpt4(prompt: str, model: str = "gpt-4o-mini") -> str:
    """
    Adapter HTTP hacia GPT-4 externo.
    Llamada directa, fuera del ciclo ADK/Pydantic.
    """
    # Auto-detección: localhost en desarrollo, mismo contenedor en producción
    base_url = _obtener_adapter_server_url()

    #print(f"{base_url} - Llamando a GPT-4 con modelo {model} y prompt: {prompt[:50]}...")
    
    url = f"{base_url}/v1/chat/completions"
    payload = {"messages": [{"role": "user", "content": prompt}]}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, params={"model": model}, timeout=30.0)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            return f"[Error Adapter GPT-4]: {str(e)}"
