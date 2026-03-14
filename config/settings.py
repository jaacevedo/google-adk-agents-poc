import os
from dotenv import load_dotenv
from google.adk.sessions import InMemorySessionService

load_dotenv()

APP_NAME = "google-adk-agents-poc"
USER_ID = "usuario_123"
SESSION_SERVICE = InMemorySessionService()
PORT = int(os.getenv("PORT", 8001))
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")