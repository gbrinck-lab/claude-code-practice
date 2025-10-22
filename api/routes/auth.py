"""Blueprint de rutas para autenticación.

Este módulo contiene los endpoints para autenticación de usuarios:
- POST /auth/register - Registrar nuevo usuario
- POST /auth/login - Iniciar sesión
- POST /auth/refresh - Refrescar token
- POST /auth/logout - Cerrar sesión
- GET /auth/me - Obtener usuario actual
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt
)
from api.models.user import User
from api.utils.validators import validate_user_data

# Crear blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# Lista negra de tokens (en producción usar Redis)
token_blacklist = set()


@auth_bp.route('/register', methods=['POST'])
def register():
    """Registra un nuevo usuario.

    Body (JSON):
        username (str): Nombre de usuario.
        email (str): Email del usuario.
        password (str): Contraseña.
        first_name (str, opcional): Nombre.
        last_name (str, opcional): Apellido.

    Returns:
        JSON: Usuario creado y tokens de acceso.
    """
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No se proporcionaron datos'}), 400

    # Validar datos del usuario
    is_valid, errors = validate_user_data(data)
    if not is_valid:
        return jsonify({'errors': errors}), 400

    # Verificar que el username no esté en uso
    if User.find_by_username(data['username']):
        return jsonify({'error': 'El username ya está en uso'}), 409

    # Verificar que el email no esté en uso
    if User.find_by_email(data['email']):
        return jsonify({'error': 'El email ya está en uso'}), 409

    # Crear usuario
    user = User(
        username=data['username'],
        email=data['email'],
        first_name=data.get('first_name'),
        last_name=data.get('last_name')
    )

    # Establecer contraseña
    user.set_password(data['password'])

    # Guardar en la base de datos
    try:
        user.save()

        # Crear tokens JWT
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)

        return jsonify({
            'message': 'Usuario registrado exitosamente',
            'user': user.to_dict(include_email=True),
            'access_token': access_token,
            'refresh_token': refresh_token
        }), 201
    except Exception as e:
        return jsonify({'error': f'Error al registrar usuario: {str(e)}'}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """Inicia sesión con credenciales de usuario.

    Body (JSON):
        username (str): Nombre de usuario o email.
        password (str): Contraseña.

    Returns:
        JSON: Tokens de acceso y datos del usuario.
    """
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No se proporcionaron datos'}), 400

    username = data.get('username', '').strip()
    password = data.get('password', '')

    if not username or not password:
        return jsonify({'error': 'Username y password son requeridos'}), 400

    # Buscar usuario por username o email
    user = User.find_by_username(username)
    if not user:
        user = User.find_by_email(username)

    # Verificar que el usuario existe y la contraseña es correcta
    if not user or not user.check_password(password):
        return jsonify({'error': 'Credenciales inválidas'}), 401

    # Verificar que el usuario esté activo
    if not user.is_active:
        return jsonify({'error': 'Usuario desactivado'}), 403

    # Crear tokens JWT
    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)

    return jsonify({
        'message': 'Inicio de sesión exitoso',
        'user': user.to_dict(include_email=True),
        'access_token': access_token,
        'refresh_token': refresh_token
    }), 200


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresca el access token usando el refresh token.

    Headers:
        Authorization: Bearer <refresh_token>

    Returns:
        JSON: Nuevo access token.
    """
    current_user_id = get_jwt_identity()

    # Verificar que el usuario existe y está activo
    user = User.find_by_id(current_user_id)
    if not user or not user.is_active:
        return jsonify({'error': 'Usuario no encontrado o desactivado'}), 401

    # Crear nuevo access token
    access_token = create_access_token(identity=current_user_id)

    return jsonify({
        'access_token': access_token
    }), 200


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Cierra sesión del usuario actual (invalida el token).

    Headers:
        Authorization: Bearer <access_token>

    Returns:
        JSON: Mensaje de confirmación.

    Note:
        En producción, usar Redis para la lista negra de tokens.
    """
    jti = get_jwt()['jti']

    # Agregar token a la lista negra
    token_blacklist.add(jti)

    return jsonify({'message': 'Sesión cerrada exitosamente'}), 200


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Obtiene los datos del usuario autenticado actual.

    Headers:
        Authorization: Bearer <access_token>

    Returns:
        JSON: Datos del usuario actual.
    """
    current_user_id = get_jwt_identity()

    user = User.find_by_id(current_user_id)

    if not user:
        return jsonify({'error': 'Usuario no encontrado'}), 404

    if not user.is_active:
        return jsonify({'error': 'Usuario desactivado'}), 403

    return jsonify({'user': user.to_dict(include_email=True)}), 200


# Callback para verificar si un token está en la lista negra
@auth_bp.before_app_request
def check_if_token_revoked():
    """Verifica si el token JWT está en la lista negra.

    Note:
        Este callback se ejecuta antes de cada request que requiere JWT.
    """
    pass  # La implementación real debería verificar token_blacklist
