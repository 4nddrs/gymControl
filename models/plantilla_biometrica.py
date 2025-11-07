"""
Modelo de Plantilla Biométrica
"""
from datetime import datetime
from bson import ObjectId

class PlantillaBiometrica:
    """Modelo para gestionar plantillas biométricas"""
    
    def __init__(self, db):
        self.collection = db.plantillas_biometricas
        self.usuarios_collection = db.usuarios
    
    def find_all(self, page=1, per_page=20, filtros=None):
        """Obtener todas las plantillas con paginación"""
        skip = (page - 1) * per_page
        query = filtros if filtros else {}
        
        plantillas = list(self.collection.find(query).skip(skip).limit(per_page))
        total = self.collection.count_documents(query)
        
        return {
            'plantillas': plantillas,
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': (total + per_page - 1) // per_page
        }
    
    def find_by_usuario(self, usuario_id):
        """Obtener plantillas de un usuario"""
        return list(self.collection.find({'usuario_id': int(usuario_id)}))
    
    def find_by_tipo(self, tipo):
        """Obtener plantillas por tipo"""
        plantillas = list(self.collection.find({'tipo': tipo}))
        
        # Agregar información del usuario
        for plantilla in plantillas:
            if plantilla.get('usuario_id'):
                usuario = self.usuarios_collection.find_one({'_id': plantilla['usuario_id']})
                if usuario:
                    plantilla['usuario_nombre'] = f"{usuario['nombre']} {usuario['apellido']}"
        
        return plantillas
    
    def get_con_template(self):
        """Obtener plantillas con template real"""
        plantillas = list(self.collection.find({'tiene_template_real': True}).limit(100))
        
        # Agregar información del usuario
        for plantilla in plantillas:
            if plantilla.get('usuario_id'):
                usuario = self.usuarios_collection.find_one({'_id': plantilla['usuario_id']})
                if usuario:
                    plantilla['usuario_nombre'] = f"{usuario['nombre']} {usuario['apellido']}"
        
        return plantillas
    
    def get_stats(self):
        """Obtener estadísticas de plantillas"""
        pipeline_tipo = [
            {'$group': {
                '_id': '$tipo',
                'total': {'$sum': 1}
            }},
            {'$sort': {'total': -1}}
        ]
        
        return {
            'total': self.collection.count_documents({}),
            'con_template': self.collection.count_documents({'tiene_template_real': True}),
            'sin_template': self.collection.count_documents({'tiene_template_real': False}),
            'por_tipo': list(self.collection.aggregate(pipeline_tipo)),
            'activas': self.collection.count_documents({'activo': True})
        }
