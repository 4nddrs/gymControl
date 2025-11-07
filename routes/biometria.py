"""
Rutas para gestión de biometría
"""
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from models import PlantillaBiometrica, Usuario, db_manager
from datetime import datetime

biometria_bp = Blueprint('biometria', __name__, url_prefix='/biometria')

@biometria_bp.route('/')
def index():
    """Lista de plantillas biométricas"""
    tipo = request.args.get('tipo', '')
    
    plantilla_model = PlantillaBiometrica(db_manager.db)
    
    if tipo:
        plantillas = plantilla_model.find_by_tipo(tipo)
        titulo = f"Plantillas de {tipo}"
    else:
        plantillas = plantilla_model.get_con_template()
        titulo = "Todas las Plantillas Biométricas"
    
    return render_template('biometria/index.html',
                         plantillas=plantillas,
                         titulo=titulo,
                         tipo=tipo)

@biometria_bp.route('/usuario/<int:usuario_id>')
def por_usuario(usuario_id):
    """Plantillas biométricas de un usuario"""
    usuario_model = Usuario(db_manager.db)
    plantilla_model = PlantillaBiometrica(db_manager.db)
    
    usuario = usuario_model.find_by_id(usuario_id)
    if not usuario:
        flash('Usuario no encontrado', 'error')
        return redirect(url_for('biometria.index'))
    
    plantillas = plantilla_model.find_by_usuario(usuario_id)
    
    return render_template('biometria/usuario.html',
                         usuario=usuario,
                         plantillas=plantillas)

@biometria_bp.route('/estadisticas')
def estadisticas():
    """Estadísticas de biometría"""
    plantilla_model = PlantillaBiometrica(db_manager.db)
    
    # Obtener estadísticas
    stats = plantilla_model.get_stats()
    
    # Estadísticas por tipo
    stats_tipo = []
    for tipo in ['Huella Digital', 'Rostro', 'Iris', 'Voz']:
        plantillas = plantilla_model.find_by_tipo(tipo)
        con_template = [p for p in plantillas if p.get('template')]
        
        stats_tipo.append({
            'tipo': tipo,
            'total': len(plantillas),
            'con_template': len(con_template),
            'sin_template': len(plantillas) - len(con_template)
        })
    
    return render_template('biometria/estadisticas.html',
                         stats=stats,
                         stats_tipo=stats_tipo)

# API Endpoints
@biometria_bp.route('/api/usuario/<int:usuario_id>')
def api_por_usuario(usuario_id):
    """API: Obtener plantillas de un usuario"""
    plantilla_model = PlantillaBiometrica(db_manager.db)
    plantillas = plantilla_model.find_by_usuario(usuario_id)
    
    # Convertir ObjectId y datetime a string
    for p in plantillas:
        p['_id'] = str(p['_id'])
        if p.get('fecha_registro'):
            p['fecha_registro'] = p['fecha_registro'].isoformat()
        if p.get('created_at'):
            p['created_at'] = p['created_at'].isoformat()
    
    return jsonify(plantillas)

@biometria_bp.route('/api/verificar', methods=['POST'])
def api_verificar():
    """API: Verificar identidad biométrica"""
    try:
        data = request.get_json()
        
        usuario_id = data.get('usuario_id')
        tipo = data.get('tipo', 'Huella Digital')
        template_capturado = data.get('template')
        
        if not usuario_id or not template_capturado:
            return jsonify({
                'success': False,
                'error': 'usuario_id y template requeridos'
            }), 400
        
        plantilla_model = PlantillaBiometrica(db_manager.db)
        plantillas = plantilla_model.find_by_usuario(int(usuario_id))
        
        # Filtrar por tipo
        plantillas_tipo = [p for p in plantillas if p.get('tipo_plantilla') == tipo]
        
        if not plantillas_tipo:
            return jsonify({
                'success': False,
                'error': 'No se encontraron plantillas para este usuario'
            }), 404
        
        # En un sistema real, aquí se haría la comparación biométrica
        # Por ahora solo verificamos que exista
        verificado = True
        confianza = 0.95  # Simulado
        
        return jsonify({
            'success': True,
            'verificado': verificado,
            'confianza': confianza,
            'usuario_id': usuario_id
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@biometria_bp.route('/api/registrar', methods=['POST'])
def api_registrar():
    """API: Registrar nueva plantilla biométrica"""
    try:
        data = request.get_json()
        
        required_fields = ['usuario_id', 'tipo_plantilla', 'template']
        if not all(field in data for field in required_fields):
            return jsonify({
                'success': False,
                'error': 'Campos requeridos: usuario_id, tipo_plantilla, template'
            }), 400
        
        # Verificar que el usuario existe
        usuario_model = Usuario(db_manager.db)
        usuario = usuario_model.find_by_id(int(data['usuario_id']))
        
        if not usuario:
            return jsonify({
                'success': False,
                'error': 'Usuario no encontrado'
            }), 404
        
        # Insertar plantilla
        plantilla = {
            'usuario_id': int(data['usuario_id']),
            'tipo_plantilla': data['tipo_plantilla'],
            'template': data['template'],
            'calidad': data.get('calidad', 0.0),
            'dispositivo': data.get('dispositivo', 'API'),
            'fecha_registro': datetime.now(),
            'activo': True,
            'created_at': datetime.now()
        }
        
        result = db_manager.db.plantillas_biometricas.insert_one(plantilla)
        
        return jsonify({
            'success': True,
            'plantilla_id': str(result.inserted_id),
            'mensaje': 'Plantilla registrada exitosamente'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@biometria_bp.route('/api/stats')
def api_stats():
    """API: Obtener estadísticas de biometría"""
    plantilla_model = PlantillaBiometrica(db_manager.db)
    stats = plantilla_model.get_stats()
    
    return jsonify(stats)
