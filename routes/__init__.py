"""
Paquete de rutas
"""
from .usuarios import usuarios_bp
from .membresias import membresias_bp
from .asistencias import asistencias_bp
from .biometria import biometria_bp
from .fotos import fotos_bp

__all__ = [
    'usuarios_bp',
    'membresias_bp',
    'asistencias_bp',
    'biometria_bp',
    'fotos_bp'
]
