"""
Rutas para servir fotos de usuarios
"""
from flask import Blueprint, send_file, abort, current_app
from utils.fotos import get_foto_path, tiene_foto, get_default_avatar
import os

fotos_bp = Blueprint('fotos', __name__, url_prefix='/fotos')

@fotos_bp.route('/<int:usuario_id>')
def get_foto(usuario_id):
    """Servir foto de un usuario"""
    try:
        # Obtener ruta de la foto
        foto_path = get_foto_path(usuario_id)
        
        # Verificar si existe
        if not os.path.exists(foto_path) if foto_path else True:
            # Devolver avatar por defecto
            return send_file(get_default_avatar(), mimetype='image/svg+xml')
        
        # Determinar tipo MIME
        ext = os.path.splitext(foto_path)[1].lower()
        mime_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.bmp': 'image/bmp'
        }
        
        mimetype = mime_types.get(ext, 'image/jpeg')
        
        return send_file(foto_path, mimetype=mimetype)
        
    except Exception as e:
        current_app.logger.error(f"Error al servir foto {usuario_id}: {str(e)}")
        # Devolver avatar por defecto en caso de error
        return send_file(get_default_avatar(), mimetype='image/svg+xml')

@fotos_bp.route('/avatar')
def avatar_default():
    """Servir avatar por defecto"""
    return send_file(get_default_avatar(), mimetype='image/svg+xml')

@fotos_bp.route('/verificar/<int:usuario_id>')
def verificar(usuario_id):
    """Verificar si un usuario tiene foto"""
    from flask import jsonify
    
    return jsonify({
        'usuario_id': usuario_id,
        'tiene_foto': tiene_foto(usuario_id),
        'url': f'/fotos/{usuario_id}'
    })
