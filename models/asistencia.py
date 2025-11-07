"""
Modelo de Asistencia
"""
from datetime import datetime, timedelta
from bson import ObjectId

class Asistencia:
    """Modelo para gestionar asistencias"""
    
    def __init__(self, db):
        self.collection = db.asistencias
        self.usuarios_collection = db.usuarios
    
    def find_all(self, page=1, per_page=20, filtros=None):
        """Obtener todas las asistencias con paginación"""
        skip = (page - 1) * per_page
        query = filtros if filtros else {}
        
        asistencias = list(self.collection.find(query).skip(skip).limit(per_page).sort('fecha', -1))
        total = self.collection.count_documents(query)
        
        return {
            'asistencias': asistencias,
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': (total + per_page - 1) // per_page
        }
    
    def find_by_usuario(self, usuario_id, limit=30):
        """Obtener asistencias de un usuario"""
        return list(self.collection.find({'usuario_id': int(usuario_id)}).sort('fecha', -1).limit(limit))
    
    def get_hoy(self):
        """Obtener asistencias de hoy"""
        hoy = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        return list(self.collection.find({'fecha': {'$gte': hoy}}).sort('fecha', -1))
    
    def get_por_fecha(self, fecha):
        """Obtener asistencias de una fecha específica"""
        inicio = fecha.replace(hour=0, minute=0, second=0, microsecond=0)
        fin = inicio + timedelta(days=1)
        
        return list(self.collection.find({
            'fecha': {
                '$gte': inicio,
                '$lt': fin
            }
        }).sort('fecha', -1))
    
    def registrar(self, data):
        """Registrar asistencia"""
        # Permitir pasar data como dict o como parámetros individuales
        if isinstance(data, dict):
            usuario_id = data.get('usuario_id')
            tipo_acceso = data.get('tipo_acceso', 'Manual')
            notas = data.get('notas', '')
        else:
            # Si se pasa usuario_id directamente (retrocompatibilidad)
            usuario_id = data
            tipo_acceso = 'Manual'
            notas = ''
        
        usuario = self.usuarios_collection.find_one({'_id': int(usuario_id)})
        if not usuario:
            raise ValueError("Usuario no encontrado")
        
        asistencia = {
            'usuario_id': int(usuario_id),
            'usuario_nombre': f"{usuario['nombre']} {usuario['apellido']}",
            'fecha': datetime.now(),
            'departamento_id': usuario.get('departamento_id'),
            'departamento_nombre': usuario.get('departamento_nombre'),
            'tipo_acceso': tipo_acceso,
            'metodo_registro': tipo_acceso,  # Alias para compatibilidad
            'notas': notas,
            'created_at': datetime.now()
        }
        
        result = self.collection.insert_one(asistencia)
        return result.inserted_id
    
    def delete(self, asistencia_id):
        """Eliminar asistencia"""
        result = self.collection.delete_one({'_id': ObjectId(asistencia_id)})
        return result.deleted_count > 0
    
    def get_stats(self):
        """Obtener estadísticas de asistencias"""
        hoy = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        semana_atras = hoy - timedelta(days=7)
        mes_atras = hoy - timedelta(days=30)
        
        return {
            'hoy': self.collection.count_documents({'fecha': {'$gte': hoy}}),
            'semana': self.collection.count_documents({'fecha': {'$gte': semana_atras}}),
            'mes': self.collection.count_documents({'fecha': {'$gte': mes_atras}}),
            'total': self.collection.count_documents({})
        }
    
    def get_top_usuarios(self, limite=10):
        """Obtener usuarios con más asistencias"""
        pipeline = [
            {'$group': {
                '_id': '$usuario_id',
                'nombre': {'$first': '$usuario_nombre'},
                'total': {'$sum': 1}
            }},
            {'$sort': {'total': -1}},
            {'$limit': limite}
        ]
        
        return list(self.collection.aggregate(pipeline))
    
    def get_por_departamento(self):
        """Obtener asistencias agrupadas por departamento"""
        pipeline = [
            {'$group': {
                '_id': '$departamento_nombre',
                'total': {'$sum': 1}
            }},
            {'$sort': {'total': -1}}
        ]
        
        return list(self.collection.aggregate(pipeline))
    
    def get_por_hora(self, fecha=None):
        """Obtener asistencias agrupadas por hora"""
        if not fecha:
            fecha = datetime.now()
        
        inicio = fecha.replace(hour=0, minute=0, second=0, microsecond=0)
        fin = inicio + timedelta(days=1)
        
        pipeline = [
            {'$match': {
                'fecha': {'$gte': inicio, '$lt': fin}
            }},
            {'$group': {
                '_id': {'$hour': '$fecha'},
                'total': {'$sum': 1}
            }},
            {'$sort': {'_id': 1}}
        ]
        
        return list(self.collection.aggregate(pipeline))
