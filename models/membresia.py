"""
Modelo de Membresía
"""
from datetime import datetime, timedelta
from bson import ObjectId

class Membresia:
    """Modelo para gestionar membresías"""
    
    def __init__(self, db):
        self.collection = db.membresias
        self.planes_collection = db.planes
        self.usuarios_collection = db.usuarios
    
    def find_all(self, page=1, per_page=20, filtros=None):
        """Obtener todas las membresías con paginación"""
        skip = (page - 1) * per_page
        query = filtros if filtros else {}
        
        membresias = list(self.collection.find(query).skip(skip).limit(per_page).sort('fecha_inicio', -1))
        total = self.collection.count_documents(query)
        
        return {
            'membresias': membresias,
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': (total + per_page - 1) // per_page
        }
    
    def find_by_id(self, membresia_id):
        """Obtener membresía por ID"""
        return self.collection.find_one({'_id': ObjectId(membresia_id)})
    
    def find_by_usuario(self, usuario_id):
        """Obtener membresías de un usuario"""
        return list(self.collection.find({'usuario_id': int(usuario_id)}).sort('fecha_inicio', -1))
    
    def get_vigentes(self):
        """Obtener membresías vigentes"""
        return list(self.collection.find({'vigente': True}))
    
    def get_vencidas(self):
        """Obtener membresías vencidas"""
        return list(self.collection.find({'vigente': False}))
    
    def get_proximas_vencer(self, dias=7):
        """Obtener membresías próximas a vencer"""
        fecha_limite = datetime.now() + timedelta(days=dias)
        return list(self.collection.find({
            'vigente': True,
            'fecha_fin': {
                '$gte': datetime.now(),
                '$lte': fecha_limite
            }
        }))
    
    def create(self, data):
        """Crear nueva membresía"""
        # Obtener datos del usuario
        usuario = self.usuarios_collection.find_one({'_id': int(data['usuario_id'])})
        if not usuario:
            raise ValueError("Usuario no encontrado")
        
        # Obtener datos del plan
        plan = self.planes_collection.find_one({'_id': ObjectId(data['plan_id'])})
        if not plan:
            raise ValueError("Plan no encontrado")
        
        # Calcular fechas
        fecha_inicio = data.get('fecha_inicio', datetime.now())
        fecha_fin = fecha_inicio + timedelta(days=plan['duracion_dias'])
        
        membresia = {
            'usuario_id': int(data['usuario_id']),
            'usuario_nombre': f"{usuario['nombre']} {usuario['apellido']}",
            'plan_id': plan['_id'],
            'plan_nombre': plan['nombre'],
            'duracion_dias': plan['duracion_dias'],
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
            'vigente': fecha_fin >= datetime.now(),
            'precio_pagado': data.get('precio_pagado', plan['precio']),
            'metodo_pago': data.get('metodo_pago', 'Efectivo'),
            'notas': data.get('notas', ''),
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        
        result = self.collection.insert_one(membresia)
        return result.inserted_id
    
    def update(self, membresia_id, data):
        """Actualizar membresía"""
        # Recalcular vigente si se cambian las fechas
        if 'fecha_fin' in data:
            data['vigente'] = data['fecha_fin'] >= datetime.now()
        
        data['updated_at'] = datetime.now()
        
        result = self.collection.update_one(
            {'_id': ObjectId(membresia_id)},
            {'$set': data}
        )
        return result.modified_count > 0
    
    def renovar(self, membresia_id, plan_id):
        """Renovar membresía"""
        membresia_actual = self.find_by_id(membresia_id)
        if not membresia_actual:
            raise ValueError("Membresía no encontrada")
        
        # Marcar la actual como no vigente
        self.update(membresia_id, {'vigente': False})
        
        # Crear nueva membresía
        plan = self.planes_collection.find_one({'_id': ObjectId(plan_id)})
        
        nueva_membresia = {
            'usuario_id': membresia_actual['usuario_id'],
            'plan_id': plan['_id'],
            'fecha_inicio': datetime.now(),
            'precio_pagado': plan['precio']
        }
        
        return self.create(nueva_membresia)
    
    def delete(self, membresia_id):
        """Eliminar membresía"""
        result = self.collection.delete_one({'_id': ObjectId(membresia_id)})
        return result.deleted_count > 0
    
    def get_stats(self):
        """Obtener estadísticas de membresías"""
        return {
            'total': self.collection.count_documents({}),
            'vigentes': self.collection.count_documents({'vigente': True}),
            'vencidas': self.collection.count_documents({'vigente': False}),
            'proximas_vencer': len(self.get_proximas_vencer(7))
        }
    
    def get_ingresos_mes(self):
        """Obtener ingresos del mes actual"""
        inicio_mes = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        pipeline = [
            {'$match': {
                'fecha_inicio': {'$gte': inicio_mes}
            }},
            {'$group': {
                '_id': None,
                'total': {'$sum': '$precio_pagado'}
            }}
        ]
        
        result = list(self.collection.aggregate(pipeline))
        return result[0]['total'] if result else 0
