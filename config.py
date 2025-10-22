"""Configuración de la aplicación Flask.

Este módulo maneja la configuración de la aplicación para diferentes entornos
(desarrollo, testing, producción) usando variables de entorno.
"""

import os
from datetime import timedelta
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()


class Config:
    """Configuración base para la aplicación."""

    # Configuración general
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = False
    TESTING = False

    # Configuración de base de datos
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'sqlite:///app.db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Configuración de JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    # Configuración de API
    JSON_SORT_KEYS = False
    JSONIFY_PRETTYPRINT_REGULAR = True

    # Configuración de CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')


class DevelopmentConfig(Config):
    """Configuración para entorno de desarrollo."""

    DEBUG = True
    SQLALCHEMY_ECHO = True  # Mostrar queries SQL en consola


class TestingConfig(Config):
    """Configuración para entorno de testing."""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # Base de datos en memoria
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    """Configuración para entorno de producción."""

    # En producción, estas variables DEBEN estar definidas
    SECRET_KEY = os.getenv('SECRET_KEY')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')

    # Validar que las variables críticas estén configuradas
    @classmethod
    def init_app(cls, app):
        """Inicialización específica para producción."""
        if not cls.SECRET_KEY:
            raise ValueError('SECRET_KEY debe estar definido en producción')
        if not cls.JWT_SECRET_KEY:
            raise ValueError('JWT_SECRET_KEY debe estar definido en producción')


# Mapeo de configuraciones según el entorno
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


def get_config():
    """Obtiene la configuración según la variable de entorno FLASK_ENV.

    Returns:
        Config: Clase de configuración apropiada para el entorno actual.
    """
    env = os.getenv('FLASK_ENV', 'development')
    return config.get(env, config['default'])
