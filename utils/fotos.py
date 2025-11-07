"""
Utilidades para manejo de fotos
"""
import os
from pathlib import Path

# Ruta a la carpeta de fotos (dentro de gymControl)
PHOTOS_DIR = Path(__file__).parent.parent / "fotos"

def get_foto_path(usuario_id):
    """Obtener la ruta de la foto de un usuario"""
    extensiones = ['.jpg', '.JPG', '.jpeg', '.JPEG', '.png', '.PNG']
    
    for ext in extensiones:
        foto_path = PHOTOS_DIR / f"{usuario_id}{ext}"
        if foto_path.exists():
            return str(foto_path)
    
    return None

def tiene_foto(usuario_id):
    """Verificar si un usuario tiene foto"""
    return get_foto_path(usuario_id) is not None

def get_foto_url(usuario_id):
    """Obtener URL relativa para mostrar la foto"""
    # Siempre devolver la URL, el endpoint manejará si existe o no
    return f"/fotos/{usuario_id}"

def get_default_avatar():
    """Obtener avatar por defecto"""
    # Ruta absoluta al archivo de avatar por defecto
    default_path = Path(__file__).parent.parent / "static" / "img" / "default-avatar.svg"
    return str(default_path)
