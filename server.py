import os
import uvicorn
import openai
from fastapi import FastAPI, Request
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.post("/v1/chat/completions")
async def proxy_gpt(request: Request):
    data = await request.json()
    response = client.chat.completions.create(model="gpt-4o-mini", messages=data.get("messages", []))
    return {"choices": [{"message": {"role": "assistant", "content": response.choices[0].message.content}}]}

if __name__ == "__main__":
    from config.settings import PORT
    uvicorn.run(app, host="0.0.0.0", port=PORT)