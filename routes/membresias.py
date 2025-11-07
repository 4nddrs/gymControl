"""
Rutas para gestión de membresías
"""
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from models import Membresia, Usuario, Plan, db_manager
from utils.helpers import format_date, format_currency
from datetime import datetime

membresias_bp = Blueprint('membresias', __name__, url_prefix='/membresias')

@membresias_bp.route('/')
def index():
    """Lista de membresías"""
    filtro = request.args.get('filtro', 'todas')
    
    membresia_model = Membresia(db_manager.db)
    
    if filtro == 'vigentes':
        membresias = membresia_model.get_vigentes()
    elif filtro == 'vencidas':
        membresias = membresia_model.get_vencidas()
    elif filtro == 'proximas':
        dias = request.args.get('dias', 7, type=int)
        membresias = membresia_model.get_proximas_vencer(dias)
    else:
        membresias = list(db_manager.db.membresias.find({'activo': True}).sort('fecha_inicio', -1).limit(100))
    
    # Obtener información adicional
    for membresia in membresias:
        membresia['dias_restantes'] = (membresia['fecha_fin'] - datetime.now()).days if membresia.get('fecha_fin') else 0
    
    return render_template('membresias/index.html',
                         membresias=membresias,
                         filtro=filtro)

@membresias_bp.route('/nueva', methods=['GET', 'POST'])
def nueva():
    """Crear nueva membresía"""
    if request.method == 'POST':
        try:
            data = {
                'usuario_id': int(request.form['usuario_id']),
                'plan_id': int(request.form['plan_id']),
                'fecha_inicio': datetime.strptime(request.form['fecha_inicio'], '%Y-%m-%d'),
                'costo': float(request.form.get('costo', 0)),
                'descuento': float(request.form.get('descuento', 0)),
                'notas': request.form.get('notas', '')
            }
            
            membresia_model = Membresia(db_manager.db)
            membresia_id = membresia_model.create(
                usuario_id=data['usuario_id'],
                plan_id=data['plan_id'],
                fecha_inicio=data['fecha_inicio'],
                costo=data['costo'],
                descuento=data['descuento'],
                notas=data['notas']
            )
            
            flash('Membresía creada exitosamente', 'success')
            return redirect(url_for('membresias.index'))
            
        except Exception as e:
            flash(f'Error al crear membresía: {str(e)}', 'error')
            return render_template('membresias/nueva.html', 
                                 usuarios=Usuario(db_manager.db).find_all()['usuarios'],
                                 planes=Plan(db_manager.db).find_all())
    
    # GET: Mostrar formulario
    usuario_model = Usuario(db_manager.db)
    plan_model = Plan(db_manager.db)
    
    return render_template('membresias/nueva.html',
                         usuarios=usuario_model.find_all()['usuarios'],
                         planes=plan_model.find_all())

@membresias_bp.route('/<int:membresia_id>/renovar', methods=['POST'])
def renovar(membresia_id):
    """Renovar membresía"""
    try:
        fecha_inicio = request.form.get('fecha_inicio')
        if fecha_inicio:
            fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d')
        
        membresia_model = Membresia(db_manager.db)
        nueva_membresia_id = membresia_model.renovar(membresia_id, fecha_inicio)
        
        flash('Membresía renovada exitosamente', 'success')
        return redirect(url_for('membresias.index'))
        
    except Exception as e:
        flash(f'Error al renovar membresía: {str(e)}', 'error')
        return redirect(url_for('membresias.index'))

@membresias_bp.route('/<int:membresia_id>/cancelar', methods=['POST'])
def cancelar(membresia_id):
    """Cancelar membresía"""
    try:
        membresia_model = Membresia(db_manager.db)
        membresia_model.update(membresia_id, {'vigente': False, 'activo': False})
        
        flash('Membresía cancelada', 'success')
        
    except Exception as e:
        flash(f'Error al cancelar membresía: {str(e)}', 'error')
    
    return redirect(url_for('membresias.index'))

@membresias_bp.route('/reportes')
def reportes():
    """Reportes de membresías"""
    membresia_model = Membresia(db_manager.db)
    
    # Estadísticas
    stats = membresia_model.get_stats()
    
    # Ingresos por mes (últimos 6 meses)
    ingresos = []
    for i in range(5, -1, -1):
        fecha = datetime.now()
        mes = fecha.month - i
        anio = fecha.year
        
        if mes <= 0:
            mes += 12
            anio -= 1
        
        ingreso = membresia_model.get_ingresos_mes(anio, mes)
        ingresos.append({
            'mes': f"{mes}/{anio}",
            'total': ingreso
        })
    
    return render_template('membresias/reportes.html',
                         stats=stats,
                         ingresos=ingresos)

# API Endpoints
@membresias_bp.route('/api/usuario/<int:usuario_id>')
def api_por_usuario(usuario_id):
    """API: Obtener membresías de un usuario"""
    membresia_model = Membresia(db_manager.db)
    membresias = membresia_model.find_by_usuario(usuario_id)
    
    # Convertir ObjectId y datetime a string
    for m in membresias:
        m['_id'] = str(m['_id'])
        if m.get('fecha_inicio'):
            m['fecha_inicio'] = m['fecha_inicio'].isoformat()
        if m.get('fecha_fin'):
            m['fecha_fin'] = m['fecha_fin'].isoformat()
        if m.get('created_at'):
            m['created_at'] = m['created_at'].isoformat()
    
    return jsonify(membresias)

@membresias_bp.route('/api/vigente/<int:usuario_id>')
def api_vigente(usuario_id):
    """API: Verificar si usuario tiene membresía vigente"""
    membresia_model = Membresia(db_manager.db)
    membresia = membresia_model.find_by_usuario(usuario_id, vigente=True)
    
    if membresia:
        membresia = membresia[0]
        return jsonify({
            'tiene_membresia': True,
            'plan': membresia.get('plan_nombre'),
            'fecha_fin': membresia['fecha_fin'].isoformat(),
            'dias_restantes': (membresia['fecha_fin'] - datetime.now()).days
        })
    else:
        return jsonify({'tiene_membresia': False})
