# Tools package - Funciones que los agentes pueden invocar
from .llamar_gpt4 import llamar_gpt4
from .resolver_problema_facturacion import resolver_problema_facturacion
from .resolver_problema_tecnico import resolver_problema_tecnico
from .resolver_problema_con_multimodel import resolver_problema_con_multimodel

__all__ = [
    "llamar_gpt4",
    "resolver_problema_facturacion", 
    "resolver_problema_tecnico",
    "resolver_problema_con_multimodel"
]