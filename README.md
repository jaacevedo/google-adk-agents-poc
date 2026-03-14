# google-adk-agents-poc
Experimental multi-agent system built with Google ADK

**Patrón:** Orquestador + Sub-agentes + FunctionTools + Human-in-the-Loop (HITL)  
**Tecnologías:** Python 3.11+, Google ADK, FastAPI, OpenAI, AsyncIO  

---

## 📂 Estructura del Proyecto

google-adk-agents-poc/
│
├── agents/ # Agentes LlmAgent y Orquestador
│ ├── agente_resolutor.py
│ ├── agente_redactor.py
│ └── orquestador.py
│
├── tools/ # Funciones invocables por los agentes
│ ├── resolver_problema_tecnico.py
│ └── resolver_problema_facturacion.py
│
├── workflows/ # Flujo principal HITL
│ └── flujo_soporte.py
│
├── config/ # Configuraciones globales y servicios
│ └── settings.py
│
├── server.py # FastAPI proxy para GPT
├── main.py # CLI interactivo para pruebas locales
├── requirements.txt
├── .env # Variables de entorno (no subir a GitHub)
├── .gitignore
└── README.md


---

## ⚙️ Configuración

1. Crear archivo `.env` en la raíz del proyecto:

```env
PORT=8001
OPENAI_API_KEY=sk-xxxxxx

pip install -r requirements.txt