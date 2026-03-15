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

    # En plataformas serverless el proxy suele vivir en el mismo contenedor.
    if os.getenv("RENDER") or os.getenv("RAILWAY_ENVIRONMENT"):
        return "http://localhost:8001"

    return "http://127.0.0.1:8001"



async def llamar_gpt4(prompt: str, model: str = "gpt-4o-mini") -> str:
    """
    Adapter HTTP hacia GPT-4 externo.
    Llamada directa, fuera del ciclo ADK/Pydantic.
    """
    # Auto-detección: localhost en desarrollo, mismo contenedor en producción
    base_url = _obtener_adapter_server_url()

    
    url = f"{base_url}/v1/chat/completions"
    payload = {"messages": [{"role": "user", "content": prompt}]}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, params={"model": model}, timeout=30.0)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            return f"[Error Adapter GPT-4]: {str(e)}"
