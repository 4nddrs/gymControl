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
        """Buscar usuarios por nombre, apellido, código, documento o email"""
        filtro = {
            '$or': [
                {'nombre': {'$regex': query, '$options': 'i'}},
                {'apellido': {'$regex': query, '$options': 'i'}},
                {'codigo': {'$regex': query, '$options': 'i'}},
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
            'codigo': data.get('codigo', ''),  # Nuevo campo código alfanumérico
            'departamento_id': data.get('departamento_id'),
            'departamento_nombre': data.get('departamento_nombre'),
            'genero': data.get('genero'),
            'fecha_nacimiento': data.get('fecha_nacimiento'),
            'fecha_inicio': data.get('fecha_inicio'),  # Nueva fecha inicio membresía
            'fecha_fin': data.get('fecha_fin'),  # Nueva fecha fin membresía
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
    
    def get_vigentes(self):
        """Obtener usuarios con membresía vigente"""
        return list(self.collection.find({
            'fecha_fin': {'$gte': datetime.now()},
            'activo': True
        }).sort('fecha_fin', 1))
    
    def get_vencidos(self):
        """Obtener usuarios con membresía vencida"""
        return list(self.collection.find({
            'fecha_fin': {'$lt': datetime.now()},
            'activo': True
        }).sort('fecha_fin', -1))
    
    def get_sin_membresia(self):
        """Obtener usuarios sin membresía (fecha_fin es None o no existe)"""
        return list(self.collection.find({
            '$or': [
                {'fecha_fin': None},
                {'fecha_fin': {'$exists': False}}
            ],
            'activo': True
        }).sort('nombre', 1))
    
    def get_proximos_vencer(self, dias=7):
        """Obtener usuarios con membresía próxima a vencer"""
        from datetime import timedelta
        fecha_limite = datetime.now() + timedelta(days=dias)
        return list(self.collection.find({
            'fecha_fin': {
                '$gte': datetime.now(),
                '$lte': fecha_limite
            },
            'activo': True
        }).sort('fecha_fin', 1))
