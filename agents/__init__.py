# Agents package - Agentes especializados
from .agente_redactor import agente_redactor
from .agente_resolutor import agente_resolutor  
from .orquestador import orquestador

root_agent = orquestador

__all__ = [
    "agente_redactor",
    "agente_resolutor", 
    "orquestador",
    "root_agent",
]