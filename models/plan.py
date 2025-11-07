"""
Modelo de Plan
"""
from datetime import datetime
from bson import ObjectId

class Plan:
    """Modelo para gestionar planes de membresía"""
    
    def __init__(self, db):
        self.collection = db.planes
    
    def find_all(self):
        """Obtener todos los planes"""
        return list(self.collection.find({'activo': True}))
    
    def find_by_id(self, plan_id):
        """Obtener plan por ID"""
        return self.collection.find_one({'_id': ObjectId(plan_id)})
    
    def create(self, data):
        """Crear nuevo plan"""
        plan = {
            'nombre': data['nombre'],
            'duracion_dias': int(data['duracion_dias']),
            'precio': float(data['precio']),
            'descripcion': data.get('descripcion', ''),
            'activo': True,
            'created_at': datetime.now()
        }
        
        result = self.collection.insert_one(plan)
        return result.inserted_id
    
    def update(self, plan_id, data):
        """Actualizar plan"""
        result = self.collection.update_one(
            {'_id': ObjectId(plan_id)},
            {'$set': data}
        )
        return result.modified_count > 0
    
    def delete(self, plan_id):
        """Eliminar plan (soft delete)"""
        return self.update(plan_id, {'activo': False})
