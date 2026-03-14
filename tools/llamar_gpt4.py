import os
import httpx
# ═══════════════════════════════════════════════════════
# TOOLS — Funciones que los agentes pueden invocar solos
# El orquestador decide cuándo y cuál usar.
# ═══════════════════════════════════════════════════════
async def llamar_gpt4(prompt: str) -> str:
    """
    Adapter HTTP hacia GPT-4 externo.
    Llamada directa, fuera del ciclo ADK/Pydantic.
    """
    # Auto-detección: localhost en desarrollo, mismo contenedor en producción
    if os.getenv("RENDER") or os.getenv("RAILWAY_ENVIRONMENT") or os.getenv("PORT"):
        # Estamos en producción - usar localhost interno del contenedor
        base_url = "http://localhost:8001"
    else:
        # Desarrollo local
        base_url = os.getenv("ADAPTER_SERVER_URL", "http://127.0.0.1:8001")
    
    url = f"{base_url}/v1/chat/completions"
    payload = {"messages": [{"role": "user", "content": prompt}]}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, timeout=30.0)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            return f"[Error Adapter GPT-4]: {str(e)}"
