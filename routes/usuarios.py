"""
Rutas para gestión de usuarios
"""
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, send_file
from models import Usuario, Departamento, db_manager
from utils.fotos import get_foto_path, get_foto_url, tiene_foto
from utils.helpers import format_date, calcular_edad
from datetime import datetime
from bson import ObjectId

usuarios_bp = Blueprint('usuarios', __name__, url_prefix='/usuarios')

@usuarios_bp.route('/')
def index():
    """Lista de usuarios"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    usuario_model = Usuario(db_manager.db)
    
    if search:
        usuarios_data = {
            'usuarios': usuario_model.search(search),
            'total': len(usuario_model.search(search)),
            'page': 1,
            'per_page': 50,
            'total_pages': 1
        }
    else:
        usuarios_data = usuario_model.find_all(page=page, per_page=20)
    
    # Agregar información de fotos
    for usuario in usuarios_data['usuarios']:
        usuario['foto_url'] = get_foto_url(usuario['_id'])
        usuario['tiene_foto'] = tiene_foto(usuario['_id'])
        if usuario.get('fecha_nacimiento'):
            usuario['edad'] = calcular_edad(usuario['fecha_nacimiento'])
    
    return render_template('usuarios/index.html', 
                         usuarios=usuarios_data['usuarios'],
                         pagination=usuarios_data,
                         search=search)

@usuarios_bp.route('/<int:usuario_id>')
def detalle(usuario_id):
    """Detalle de un usuario"""
    usuario_model = Usuario(db_manager.db)
    usuario = usuario_model.find_by_id(usuario_id)
    
    if not usuario:
        flash('Usuario no encontrado', 'error')
        return redirect(url_for('usuarios.index'))
    
    # Agregar información adicional
    usuario['foto_url'] = get_foto_url(usuario_id)
    usuario['tiene_foto'] = tiene_foto(usuario_id)
    
    if usuario.get('fecha_nacimiento'):
        usuario['edad'] = calcular_edad(usuario['fecha_nacimiento'])
    
    # Obtener membresías del usuario
    from models.membresia import Membresia
    membresia_model = Membresia(db_manager.db)
    membresias = membresia_model.find_by_usuario(usuario_id)
    
    # Obtener asistencias recientes
    from models.asistencia import Asistencia
    asistencia_model = Asistencia(db_manager.db)
    asistencias = asistencia_model.find_by_usuario(usuario_id, limit=10)
    
    # Obtener plantillas biométricas
    from models.plantilla_biometrica import PlantillaBiometrica
    plantilla_model = PlantillaBiometrica(db_manager.db)
    plantillas = plantilla_model.find_by_usuario(usuario_id)
    
    return render_template('usuarios/detalle.html',
                         usuario=usuario,
                         membresias=membresias,
                         asistencias=asistencias,
                         plantillas=plantillas)

@usuarios_bp.route('/nuevo', methods=['GET', 'POST'])
def nuevo():
    """Crear nuevo usuario"""
    if request.method == 'POST':
        try:
            data = request.form.to_dict()
            
            # Convertir fecha de nacimiento
            if data.get('fecha_nacimiento'):
                data['fecha_nacimiento'] = datetime.strptime(data['fecha_nacimiento'], '%Y-%m-%d')
            
            # Convertir fecha inicio membresía
            if data.get('fecha_inicio'):
                data['fecha_inicio'] = datetime.strptime(data['fecha_inicio'], '%Y-%m-%d')
            
            # Convertir fecha fin membresía
            if data.get('fecha_fin'):
                data['fecha_fin'] = datetime.strptime(data['fecha_fin'], '%Y-%m-%d')
            
            # Obtener nombre del departamento si se seleccionó uno
            if data.get('departamento_id'):
                departamento_model = Departamento(db_manager.db)
                departamento = departamento_model.find_by_id(data['departamento_id'])
                if departamento:
                    data['departamento_nombre'] = departamento['nombre']
            
            usuario_model = Usuario(db_manager.db)
            usuario_id = usuario_model.create(data)
            
            flash('Usuario creado exitosamente', 'success')
            return redirect(url_for('usuarios.detalle', usuario_id=usuario_id))
            
        except Exception as e:
            flash(f'Error al crear usuario: {str(e)}', 'error')
            departamento_model = Departamento(db_manager.db)
            return render_template('usuarios/nuevo.html', 
                                 data=data,
                                 departamentos=departamento_model.find_all())
    
    departamento_model = Departamento(db_manager.db)
    return render_template('usuarios/nuevo.html',
                         departamentos=departamento_model.find_all())

@usuarios_bp.route('/<int:usuario_id>/editar', methods=['GET', 'POST'])
def editar(usuario_id):
    """Editar usuario"""
    usuario_model = Usuario(db_manager.db)
    usuario = usuario_model.find_by_id(usuario_id)
    
    if not usuario:
        flash('Usuario no encontrado', 'error')
        return redirect(url_for('usuarios.index'))
    
    if request.method == 'POST':
        try:
            data = request.form.to_dict()
            
            # Convertir fecha de nacimiento
            if data.get('fecha_nacimiento'):
                data['fecha_nacimiento'] = datetime.strptime(data['fecha_nacimiento'], '%Y-%m-%d')
            
            # Convertir fecha inicio membresía
            if data.get('fecha_inicio'):
                data['fecha_inicio'] = datetime.strptime(data['fecha_inicio'], '%Y-%m-%d')
            
            # Convertir fecha fin membresía
            if data.get('fecha_fin'):
                data['fecha_fin'] = datetime.strptime(data['fecha_fin'], '%Y-%m-%d')
            
            # Obtener nombre del departamento si se seleccionó uno
            if data.get('departamento_id'):
                departamento_model = Departamento(db_manager.db)
                departamento = departamento_model.find_by_id(data['departamento_id'])
                if departamento:
                    data['departamento_nombre'] = departamento['nombre']
            
            usuario_model.update(usuario_id, data)
            
            flash('Usuario actualizado exitosamente', 'success')
            return redirect(url_for('usuarios.detalle', usuario_id=usuario_id))
            
        except Exception as e:
            flash(f'Error al actualizar usuario: {str(e)}', 'error')
    
    departamento_model = Departamento(db_manager.db)
    return render_template('usuarios/editar.html', 
                         usuario=usuario,
                         departamentos=departamento_model.find_all())

@usuarios_bp.route('/<int:usuario_id>/eliminar', methods=['POST'])
def eliminar(usuario_id):
    """Eliminar usuario (soft delete)"""
    usuario_model = Usuario(db_manager.db)
    
    if usuario_model.delete(usuario_id):
        flash('Usuario eliminado exitosamente', 'success')
    else:
        flash('Error al eliminar usuario', 'error')
    
    return redirect(url_for('usuarios.index'))

# API Endpoints
@usuarios_bp.route('/api/search')
def api_search():
    """API: Buscar usuarios"""
    query = request.args.get('q', '')
    usuario_model = Usuario(db_manager.db)
    usuarios = usuario_model.search(query)
    
    # Formato simple para autocomplete
    results = [{
        'id': u['_id'],
        'nombre': f"{u['nombre']} {u['apellido']}",
        'documento': u.get('numero_documento', ''),
        'departamento': u.get('departamento_nombre', '')
    } for u in usuarios]
    
    return jsonify(results)

@usuarios_bp.route('/api/<int:usuario_id>')
def api_detalle(usuario_id):
    """API: Obtener datos de un usuario"""
    usuario_model = Usuario(db_manager.db)
    usuario = usuario_model.find_by_id(usuario_id)
    
    if not usuario:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    
    # Convertir ObjectId y datetime a string
    usuario['_id'] = str(usuario['_id'])
    if usuario.get('fecha_nacimiento'):
        usuario['fecha_nacimiento'] = usuario['fecha_nacimiento'].isoformat()
    if usuario.get('created_at'):
        usuario['created_at'] = usuario['created_at'].isoformat()
    if usuario.get('updated_at'):
        usuario['updated_at'] = usuario['updated_at'].isoformat()
    
    return jsonify(usuario)
