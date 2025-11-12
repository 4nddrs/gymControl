"""
Rutas para gestión de membresías (ahora basadas en Usuario)
"""
from flask import Blueprint, render_template, request
from models import Usuario, db_manager
from datetime import datetime, timedelta

membresias_bp = Blueprint('membresias', __name__, url_prefix='/membresias')

@membresias_bp.route('/')
def index():
    """Lista de usuarios con filtros de membresía"""
    filtro = request.args.get('filtro', 'todas')
    dias_aviso = request.args.get('dias', 7, type=int)
    
    # Normalizar fecha actual a medianoche (solo comparar día, mes, año)
    fecha_actual = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Obtener todos los usuarios activos
    usuarios = list(db_manager.db.usuarios.find({'activo': True}).sort('nombre', 1))
    
    # Procesar cada usuario para determinar su estado de membresía
    usuarios_procesados = []
    
    for usuario in usuarios:
        # Obtener fechas del usuario
        fecha_inicio = usuario.get('fecha_inicio')
        fecha_fin = usuario.get('fecha_fin')
        
        # Inicializar estado por defecto
        usuario['estado_membresia'] = 'sin_membresia'
        usuario['tiene_membresia'] = False
        usuario['dias_restantes'] = None
        
        # Solo procesar si tiene fecha_fin definida
        if fecha_fin is not None:
            # Normalizar fecha_fin a medianoche para comparación justa
            if isinstance(fecha_fin, datetime):
                fecha_fin_normalizada = fecha_fin.replace(hour=0, minute=0, second=0, microsecond=0)
            else:
                fecha_fin_normalizada = fecha_fin
            
            # Calcular días restantes
            dias_restantes = (fecha_fin_normalizada - fecha_actual).days
            usuario['dias_restantes'] = dias_restantes
            
            # Determinar estado según fecha_fin
            if fecha_fin_normalizada >= fecha_actual:
                # Membresía vigente (incluye el día de hoy)
                usuario['tiene_membresia'] = True
                
                if dias_restantes <= dias_aviso:
                    usuario['estado_membresia'] = 'proxima_vencer'
                else:
                    usuario['estado_membresia'] = 'vigente'
            else:
                # Membresía vencida
                usuario['estado_membresia'] = 'vencida'
                usuario['tiene_membresia'] = False
        
        # Agregar a la lista procesada
        usuarios_procesados.append(usuario)
    
    # Filtrar según el filtro seleccionado
    usuarios_filtrados = []
    for usuario in usuarios_procesados:
        if filtro == 'todas':
            usuarios_filtrados.append(usuario)
        elif filtro == 'vigentes' and usuario['estado_membresia'] in ['vigente', 'proxima_vencer']:
            usuarios_filtrados.append(usuario)
        elif filtro == 'vencidas' and usuario['estado_membresia'] == 'vencida':
            usuarios_filtrados.append(usuario)
        elif filtro == 'sin_membresia' and usuario['estado_membresia'] == 'sin_membresia':
            usuarios_filtrados.append(usuario)
        elif filtro == 'proximas' and usuario['estado_membresia'] == 'proxima_vencer':
            usuarios_filtrados.append(usuario)
    
    # Ordenar según el filtro
    if filtro == 'proximas':
        # Ordenar por días restantes (los que vencen primero)
        usuarios_filtrados.sort(key=lambda x: x.get('dias_restantes', 999) if x.get('dias_restantes') is not None else 999)
    elif filtro == 'vencidas':
        # Ordenar por fecha de vencimiento (más recientes primero)
        usuarios_filtrados.sort(key=lambda x: x.get('fecha_fin') or datetime.min, reverse=True)
    
    # Calcular estadísticas con TODOS los usuarios procesados
    stats = {
        'vigentes': len([u for u in usuarios_procesados if u.get('estado_membresia') in ['vigente', 'proxima_vencer']]),
        'proximas': len([u for u in usuarios_procesados if u.get('estado_membresia') == 'proxima_vencer']),
        'vencidas': len([u for u in usuarios_procesados if u.get('estado_membresia') == 'vencida']),
        'sin_membresia': len([u for u in usuarios_procesados if u.get('estado_membresia') == 'sin_membresia'])
    }
    
    return render_template('membresias/index.html',
                         usuarios=usuarios_filtrados,
                         stats=stats,
                         filtro=filtro,
                         dias_aviso=dias_aviso)
