"""
Modelo de Usuario
"""
from datetime import datetime
from bson import ObjectId

class Usuario:
    """Modelo para gestionar usuarios"""
    
    def __init__(self, db):
        self.collection = db.usuarios
    
    def find_all(self, page=1, per_page=20, filtros=None):
        """Obtener todos los usuarios con paginación"""
        skip = (page - 1) * per_page
        query = filtros if filtros else {}
        
        usuarios = list(self.collection.find(query).skip(skip).limit(per_page))
        total = self.collection.count_documents(query)
        
        return {
            'usuarios': usuarios,
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': (total + per_page - 1) // per_page
        }
    
    def find_by_id(self, usuario_id):
        """Obtener usuario por ID"""
        try:
            return self.collection.find_one({'_id': int(usuario_id)})
        except:
            return None
    
    def search(self, query):
        """Buscar usuarios por nombre, apellido o documento"""
        filtro = {
            '$or': [
                {'nombre': {'$regex': query, '$options': 'i'}},
                {'apellido': {'$regex': query, '$options': 'i'}},
                {'numero_documento': {'$regex': query, '$options': 'i'}},
                {'email': {'$regex': query, '$options': 'i'}}
            ]
        }
        return list(self.collection.find(filtro).limit(50))
    
    def create(self, data):
        """Crear nuevo usuario"""
        usuario = {
            '_id': data.get('id'),
            'nombre': data.get('nombre'),
            'apellido': data.get('apellido'),
            'departamento_id': data.get('departamento_id'),
            'departamento_nombre': data.get('departamento_nombre'),
            'genero': data.get('genero'),
            'fecha_nacimiento': data.get('fecha_nacimiento'),
            'celular': data.get('celular'),
            'email': data.get('email'),
            'tipo_documento': data.get('tipo_documento'),
            'numero_documento': data.get('numero_documento'),
            'plantillas_biometricas': [],
            'tiene_foto': False,
            'foto_path': None,
            'tiene_biometria': False,
            'total_plantillas': 0,
            'activo': True,
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        
        result = self.collection.insert_one(usuario)
        return result.inserted_id
    
    def update(self, usuario_id, data):
        """Actualizar usuario"""
        data['updated_at'] = datetime.now()
        
        result = self.collection.update_one(
            {'_id': int(usuario_id)},
            {'$set': data}
        )
        return result.modified_count > 0
    
    def delete(self, usuario_id):
        """Eliminar usuario (soft delete)"""
        return self.update(usuario_id, {'activo': False})
    
    def get_stats(self):
        """Obtener estadísticas de usuarios"""
        return {
            'total': self.collection.count_documents({}),
            'activos': self.collection.count_documents({'activo': True}),
            'inactivos': self.collection.count_documents({'activo': False}),
            'con_foto': self.collection.count_documents({'tiene_foto': True}),
            'con_biometria': self.collection.count_documents({'tiene_biometria': True}),
            'con_email': self.collection.count_documents({'email': {'$ne': ''}}),
        }
    
    def get_by_departamento(self):
        """Obtener usuarios agrupados por departamento"""
        pipeline = [
            {'$group': {
                '_id': '$departamento_nombre',
                'total': {'$sum': 1}
            }},
            {'$sort': {'total': -1}}
        ]
        return list(self.collection.aggregate(pipeline))
