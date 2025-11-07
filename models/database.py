"""
Database Connection Manager
"""
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

class Database:
    """Singleton para la conexión a MongoDB"""
    _instance = None
    _client = None
    _db = None
    
    def __new__(cls, uri=None, db_name=None):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
        return cls._instance
    
    def connect(self, uri, db_name):
        """Conectar a MongoDB"""
        try:
            self._client = MongoClient(uri, serverSelectionTimeoutMS=5000)
            self._client.server_info()  # Verificar conexión
            self._db = self._client[db_name]
            print(f"✓ Conectado a MongoDB: {db_name}")
            return True
        except ConnectionFailure as e:
            print(f"✗ Error al conectar a MongoDB: {e}")
            return False
    
    @property
    def db(self):
        """Obtener instancia de la base de datos"""
        return self._db
    
    @property
    def client(self):
        """Obtener cliente de MongoDB"""
        return self._client
    
    def close(self):
        """Cerrar conexión"""
        if self._client:
            self._client.close()
            print("✓ Conexión a MongoDB cerrada")

# Instancia global
db_manager = Database()
