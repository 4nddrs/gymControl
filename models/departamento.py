"""
Modelo de Departamento
"""
from datetime import datetime
from bson import ObjectId

class Departamento:
    """Modelo para gestionar departamentos"""
    
    def __init__(self, db):
        self.collection = db.departamentos
    
    def find_all(self):
        """Obtener todos los departamentos"""
        return list(self.collection.find({'activo': True}).sort('nombre', 1))
    
    def find_by_id(self, departamento_id):
        """Obtener departamento por ID"""
        return self.collection.find_one({'_id': ObjectId(departamento_id)})
    
    def create(self, nombre, descripcion=''):
        """Crear nuevo departamento"""
        departamento = {
            'nombre': nombre,
            'descripcion': descripcion,
            'activo': True,
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        
        result = self.collection.insert_one(departamento)
        return result.inserted_id
    
    def update(self, departamento_id, data):
        """Actualizar departamento"""
        data['updated_at'] = datetime.now()
        
        result = self.collection.update_one(
            {'_id': ObjectId(departamento_id)},
            {'$set': data}
        )
        return result.modified_count > 0
    
    def delete(self, departamento_id):
        """Eliminar departamento (soft delete)"""
        return self.update(departamento_id, {'activo': False})
