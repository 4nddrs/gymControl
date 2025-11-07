"""
Configuración de la aplicación Flask
"""
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class Config:
    """Configuración base"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # MongoDB
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
    DATABASE_NAME = os.getenv('DATABASE_NAME', 'gimnasio_db')
    
    # Flask
    DEBUG = os.getenv('FLASK_DEBUG', 'False') == '1'
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))
    
    # Paginación
    ITEMS_PER_PAGE = 20
    
    # Upload
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

class DevelopmentConfig(Config):
    """Configuración de desarrollo"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Configuración de producción"""
    DEBUG = False
    TESTING = False

class TestingConfig(Config):
    """Configuración de testing"""
    DEBUG = True
    TESTING = True
    DATABASE_NAME = 'gimnasio_db_test'

# Configuración por defecto
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
