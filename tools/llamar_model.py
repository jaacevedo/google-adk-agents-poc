import os

from google import genai

gemini_client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

def generar_respuesta(analisis: str):

    response = gemini_client.models.generate_content(
        model="gemini-2.5-flash",
        contents=analisis
    )

    return response.candidates[0].content.parts[0].text