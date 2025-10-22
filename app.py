"""Aplicación Flask principal.

Este módulo inicializa y configura la aplicación Flask con todas
las extensiones, blueprints y middlewares necesarios.
"""

import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate

from config import get_config
from api.models.user import db
from api.routes.users import users_bp
from api.routes.auth import auth_bp


def create_app(config_name=None):
    """Factory para crear la aplicación Flask.

    Args:
        config_name (str, opcional): Nombre de la configuración a usar.
            Si no se especifica, se usa FLASK_ENV.

    Returns:
        Flask: Aplicación Flask configurada.
    """
    app = Flask(__name__)

    # Cargar configuración
    if config_name:
        from config import config as config_dict
        app.config.from_object(config_dict[config_name])
    else:
        app.config.from_object(get_config())

    # Inicializar extensiones
    init_extensions(app)

    # Registrar blueprints
    register_blueprints(app)

    # Registrar manejadores de errores
    register_error_handlers(app)

    # Registrar comandos CLI
    register_cli_commands(app)

    return app


def init_extensions(app):
    """Inicializa las extensiones de Flask.

    Args:
        app (Flask): Instancia de la aplicación Flask.
    """
    # Inicializar SQLAlchemy
    db.init_app(app)

    # Inicializar CORS
    CORS(app, origins=app.config['CORS_ORIGINS'])

    # Inicializar JWT
    jwt = JWTManager(app)

    # Inicializar Flask-Migrate
    Migrate(app, db)

    # Configurar callbacks de JWT
    @jwt.unauthorized_loader
    def unauthorized_callback(reason):
        """Callback para errores de autenticación."""
        return jsonify({
            'error': 'Token de autorización no proporcionado',
            'message': reason
        }), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(reason):
        """Callback para tokens inválidos."""
        return jsonify({
            'error': 'Token inválido',
            'message': reason
        }), 422

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_data):
        """Callback para tokens expirados."""
        return jsonify({
            'error': 'Token expirado',
            'message': 'El token de autorización ha expirado'
        }), 401

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_data):
        """Callback para tokens revocados."""
        return jsonify({
            'error': 'Token revocado',
            'message': 'El token de autorización ha sido revocado'
        }), 401


def register_blueprints(app):
    """Registra los blueprints de la aplicación.

    Args:
        app (Flask): Instancia de la aplicación Flask.
    """
    # Registrar blueprints
    app.register_blueprint(users_bp)
    app.register_blueprint(auth_bp)

    # Ruta de health check
    @app.route('/health', methods=['GET'])
    def health_check():
        """Endpoint de health check."""
        return jsonify({
            'status': 'healthy',
            'message': 'API funcionando correctamente'
        }), 200

    # Ruta raíz
    @app.route('/', methods=['GET'])
    def root():
        """Endpoint raíz de la API."""
        return jsonify({
            'message': 'API REST con Flask',
            'version': '1.0.0',
            'endpoints': {
                'auth': {
                    'register': 'POST /api/auth/register',
                    'login': 'POST /api/auth/login',
                    'refresh': 'POST /api/auth/refresh',
                    'logout': 'POST /api/auth/logout',
                    'me': 'GET /api/auth/me'
                },
                'users': {
                    'list': 'GET /api/users',
                    'get': 'GET /api/users/<id>',
                    'create': 'POST /api/users',
                    'update': 'PUT /api/users/<id>',
                    'delete': 'DELETE /api/users/<id>'
                }
            }
        }), 200


def register_error_handlers(app):
    """Registra los manejadores de errores globales.

    Args:
        app (Flask): Instancia de la aplicación Flask.
    """
    @app.errorhandler(404)
    def not_found(error):
        """Maneja errores 404 Not Found."""
        return jsonify({
            'error': 'Recurso no encontrado',
            'message': str(error)
        }), 404

    @app.errorhandler(405)
    def method_not_allowed(error):
        """Maneja errores 405 Method Not Allowed."""
        return jsonify({
            'error': 'Método no permitido',
            'message': str(error)
        }), 405

    @app.errorhandler(500)
    def internal_error(error):
        """Maneja errores 500 Internal Server Error."""
        return jsonify({
            'error': 'Error interno del servidor',
            'message': 'Ha ocurrido un error inesperado'
        }), 500


def register_cli_commands(app):
    """Registra comandos CLI personalizados.

    Args:
        app (Flask): Instancia de la aplicación Flask.
    """
    @app.cli.command('init-db')
    def init_db():
        """Inicializa la base de datos (crea todas las tablas)."""
        with app.app_context():
            db.create_all()
            print('Base de datos inicializada exitosamente')

    @app.cli.command('create-admin')
    def create_admin():
        """Crea un usuario administrador."""
        from api.models.user import User

        with app.app_context():
            # Verificar si ya existe un admin
            admin = User.find_by_username('admin')
            if admin:
                print('El usuario admin ya existe')
                return

            # Crear usuario admin
            admin = User(
                username='admin',
                email='admin@example.com',
                first_name='Admin',
                last_name='User',
                is_admin=True
            )
            admin.set_password('Admin123!')

            admin.save()
            print('Usuario administrador creado exitosamente')
            print('Username: admin')
            print('Password: Admin123!')


# Crear la aplicación
app = create_app()


if __name__ == '__main__':
    # Obtener puerto de variable de entorno o usar 5000 por defecto
    port = int(os.getenv('PORT', 5000))

    # Ejecutar aplicación
    app.run(
        host='0.0.0.0',
        port=port,
        debug=app.config['DEBUG']
    )
