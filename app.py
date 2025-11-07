"""
Aplicación Flask para el Sistema de Gestión de Gimnasio - VITO'S GYM
"""
from flask import Flask, render_template, jsonify
from pymongo import MongoClient
from datetime import datetime
import os
from config import config

# Importar modelos
from models import db_manager, Usuario, Membresia, Asistencia, PlantillaBiometrica, Plan

# Importar blueprints
from routes import usuarios_bp, membresias_bp, asistencias_bp, biometria_bp, fotos_bp

# Crear la aplicación Flask
app = Flask(__name__)

# Cargar configuración
env = os.getenv('FLASK_ENV', 'development')
app.config.from_object(config[env])

# Conectar a MongoDB usando el singleton
db_manager.connect(app.config['MONGO_URI'], app.config['DATABASE_NAME'])

# Registrar blueprints
app.register_blueprint(usuarios_bp)
app.register_blueprint(membresias_bp)
app.register_blueprint(asistencias_bp)
app.register_blueprint(biometria_bp)
app.register_blueprint(fotos_bp)

# =====================================
# RUTAS PRINCIPALES
# =====================================

@app.route('/')
def index():
    """Dashboard principal"""
    if db_manager.db is None:
        return "Error: No se pudo conectar a la base de datos", 500
    
    # Obtener estadísticas usando los modelos
    usuario_model = Usuario(db_manager.db)
    membresia_model = Membresia(db_manager.db)
    asistencia_model = Asistencia(db_manager.db)
    
    stats = {
        'total_usuarios': usuario_model.get_stats()['total'],
        'usuarios_activos': usuario_model.get_stats()['activos'],
        'membresias_vigentes': membresia_model.get_stats()['vigentes'],
        'asistencias_hoy': len(asistencia_model.get_hoy()),
    }
    
    return render_template('index.html', stats=stats)

@app.route('/api/stats')
def api_stats():
    """API: Estadísticas generales"""
    if db_manager.db is None:
        return jsonify({'error': 'Database connection failed'}), 500
    
    # Obtener estadísticas de cada modelo
    usuario_model = Usuario(db_manager.db)
    membresia_model = Membresia(db_manager.db)
    plantilla_model = PlantillaBiometrica(db_manager.db)
    asistencia_model = Asistencia(db_manager.db)
    
    stats = {
        'usuarios': usuario_model.get_stats(),
        'membresias': membresia_model.get_stats(),
        'plantillas': plantilla_model.get_stats(),
        'asistencias_hoy': len(asistencia_model.get_hoy())
    }
    
    return jsonify(stats)

@app.route('/usuarios')
def usuarios_redirect():
    """Redireccionar a la lista de usuarios"""
    from flask import redirect, url_for
    return redirect(url_for('usuarios.index'))

@app.route('/membresias')
def membresias_redirect():
    """Redireccionar a membresías"""
    from flask import redirect, url_for
    return redirect(url_for('membresias.index'))

@app.route('/asistencias')
def asistencias_redirect():
    """Redireccionar a asistencias"""
    from flask import redirect, url_for
    return redirect(url_for('asistencias.index'))

@app.route('/biometria')
def biometria_redirect():
    """Redireccionar a biometría"""
    from flask import redirect, url_for
    return redirect(url_for('biometria.index'))

@app.route('/reportes')
def reportes():
    """Reportes y estadísticas"""
    return render_template('reportes.html')


# =====================================
# MANEJADORES DE ERRORES
# =====================================

@app.errorhandler(404)
def not_found(error):
    """Página no encontrada"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Error interno del servidor"""
    return render_template('500.html'), 500

# =====================================
# PUNTO DE ENTRADA
# =====================================

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🏋️  VITO'S GYM - Sistema de Gestión de Gimnasio")
    print("="*60)
    print(f"Entorno: {env}")
    print(f"Debug: {app.config['DEBUG']}")
    print(f"Base de datos: {app.config['DATABASE_NAME']}")
    print(f"Puerto: {app.config['PORT']}")
    print("="*60 + "\n")
    
    app.run(
        host=app.config['HOST'],
        port=app.config['PORT'],
        debug=app.config['DEBUG']
    )

