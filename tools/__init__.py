# Tools package - Funciones que los agentes pueden invocar
from .llamar_model import generar_respuesta
from .resolver_problema_facturacion import resolver_problema_facturacion
from .resolver_problema_tecnico import resolver_problema_tecnico
from .resolver_problema_con_multimodel import resolver_problema_con_multimodel

__all__ = [
    "generar_respuesta",
    "resolver_problema_facturacion", 
    "resolver_problema_tecnico",
    "resolver_problema_con_multimodel"
]