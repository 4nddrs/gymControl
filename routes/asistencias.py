"""
Rutas para gestión de asistencias
"""
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from models import Asistencia, Usuario, db_manager
from utils.helpers import format_date, format_datetime
from datetime import datetime, timedelta

asistencias_bp = Blueprint('asistencias', __name__, url_prefix='/asistencias')

@asistencias_bp.route('/')
def index():
    """Lista de asistencias"""
    fecha_str = request.args.get('fecha')
    
    asistencia_model = Asistencia(db_manager.db)
    
    if fecha_str:
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d')
        asistencias = asistencia_model.get_por_fecha(fecha)
        titulo = f"Asistencias del {format_date(fecha)}"
    else:
        asistencias = asistencia_model.get_hoy()
        titulo = "Asistencias de Hoy"
    
    return render_template('asistencias/index.html',
                         asistencias=asistencias,
                         titulo=titulo,
                         fecha=fecha_str or datetime.now().strftime('%Y-%m-%d'))

@asistencias_bp.route('/registrar', methods=['GET', 'POST'])
def registrar():
    """Registrar asistencia"""
    if request.method == 'POST':
        try:
            usuario_id = int(request.form['usuario_id'])
            metodo = request.form.get('metodo', 'Manual')
            notas = request.form.get('notas', '')
            
            asistencia_model = Asistencia(db_manager.db)
            asistencia_id = asistencia_model.registrar({
                'usuario_id': usuario_id,
                'tipo_acceso': metodo,
                'notas': notas
            })
            
            if asistencia_id:
                flash('Asistencia registrada exitosamente', 'success')
            else:
                flash('Error: Ya existe un registro de asistencia para este usuario hoy', 'warning')
            
            return redirect(url_for('asistencias.index'))
            
        except Exception as e:
            flash(f'Error al registrar asistencia: {str(e)}', 'error')
            return redirect(url_for('asistencias.registrar'))
    
    # GET: Mostrar formulario
    return render_template('asistencias/registrar.html')

@asistencias_bp.route('/estadisticas')
def estadisticas():
    """Estadísticas de asistencias"""
    asistencia_model = Asistencia(db_manager.db)
    
    # Estadísticas generales
    stats = asistencia_model.get_stats()
    
    # Top usuarios
    top_usuarios = asistencia_model.get_top_usuarios(limit=10)
    
    # Asistencias por departamento
    stats_depto = asistencia_model.get_por_departamento()
    
    # Asistencias por hora (hoy)
    stats_hora = asistencia_model.get_por_hora(datetime.now())
    
    # Asistencias última semana
    asistencias_semana = []
    for i in range(6, -1, -1):
        fecha = datetime.now() - timedelta(days=i)
        count = len(asistencia_model.get_por_fecha(fecha))
        asistencias_semana.append({
            'fecha': format_date(fecha),
            'count': count
        })
    
    return render_template('asistencias/estadisticas.html',
                         stats=stats,
                         top_usuarios=top_usuarios,
                         stats_depto=stats_depto,
                         stats_hora=stats_hora,
                         asistencias_semana=asistencias_semana)

@asistencias_bp.route('/historial/<int:usuario_id>')
def historial(usuario_id):
    """Historial de asistencias de un usuario"""
    asistencia_model = Asistencia(db_manager.db)
    usuario_model = Usuario(db_manager.db)
    
    usuario = usuario_model.find_by_id(usuario_id)
    if not usuario:
        flash('Usuario no encontrado', 'error')
        return redirect(url_for('asistencias.index'))
    
    asistencias = asistencia_model.find_by_usuario(usuario_id, limit=50)
    
    return render_template('asistencias/historial.html',
                         usuario=usuario,
                         asistencias=asistencias)

# API Endpoints
@asistencias_bp.route('/api/registrar', methods=['POST'])
def api_registrar():
    """API: Registrar asistencia (para sistemas biométricos)"""
    try:
        data = request.get_json()
        
        usuario_id = data.get('usuario_id')
        metodo = data.get('metodo', 'biometrico')
        
        if not usuario_id:
            return jsonify({'success': False, 'error': 'usuario_id requerido'}), 400
        
        asistencia_model = Asistencia(db_manager.db)
        asistencia_id = asistencia_model.registrar({
            'usuario_id': int(usuario_id),
            'tipo_acceso': metodo,
            'notas': ''
        })
        
        if asistencia_id:
            return jsonify({
                'success': True,
                'asistencia_id': asistencia_id,
                'mensaje': 'Asistencia registrada'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Ya existe un registro para hoy'
            }), 400
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@asistencias_bp.route('/api/verificar/<int:usuario_id>')
def api_verificar(usuario_id):
    """API: Verificar si el usuario ya registró asistencia hoy"""
    asistencia_model = Asistencia(db_manager.db)
    
    hoy_inicio = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    hoy_fin = datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999)
    
    asistencia = db_manager.db.asistencias.find_one({
        'usuario_id': usuario_id,
        'fecha_hora': {'$gte': hoy_inicio, '$lte': hoy_fin},
        'activo': True
    })
    
    if asistencia:
        return jsonify({
            'registrado': True,
            'hora': asistencia['fecha_hora'].strftime('%H:%M:%S')
        })
    else:
        return jsonify({'registrado': False})

@asistencias_bp.route('/api/hoy')
def api_hoy():
    """API: Obtener asistencias de hoy"""
    asistencia_model = Asistencia(db_manager.db)
    asistencias = asistencia_model.get_hoy()
    
    # Convertir datetime a string
    for a in asistencias:
        a['_id'] = str(a['_id'])
        if a.get('fecha_hora'):
            a['fecha_hora'] = a['fecha_hora'].isoformat()
    
    return jsonify({
        'total': len(asistencias),
        'asistencias': asistencias
    })
