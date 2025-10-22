"""Blueprint de rutas para gestión de usuarios.

Este módulo contiene los endpoints REST para la gestión de usuarios:
- GET /users - Listar usuarios
- GET /users/<id> - Obtener un usuario específico
- POST /users - Crear un nuevo usuario
- PUT /users/<id> - Actualizar un usuario
- DELETE /users/<id> - Eliminar un usuario
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from api.models.user import User, db
from api.utils.validators import validate_user_data, validate_pagination_params

# Crear blueprint
users_bp = Blueprint('users', __name__, url_prefix='/api/users')


@users_bp.route('', methods=['GET'])
@jwt_required()
def get_users():
    """Obtiene lista de usuarios con paginación.

    Query params:
        page (int): Número de página (default: 1).
        per_page (int): Usuarios por página (default: 10, max: 100).
        search (str): Buscar por username o email.

    Returns:
        JSON: Lista de usuarios y metadata de paginación.
    """
    # Obtener parámetros de paginación
    page = request.args.get('page', 1)
    per_page = request.args.get('per_page', 10)
    search = request.args.get('search', '').strip()

    # Validar parámetros de paginación
    is_valid, error = validate_pagination_params(page, per_page)
    if not is_valid:
        return jsonify({'error': error}), 400

    page = int(page)
    per_page = int(per_page)

    # Construir query
    query = User.query.filter_by(is_active=True)

    # Aplicar búsqueda si existe
    if search:
        query = query.filter(
            db.or_(
                User.username.ilike(f'%{search}%'),
                User.email.ilike(f'%{search}%')
            )
        )

    # Ejecutar paginación
    pagination = query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    # Preparar respuesta
    users = [user.to_dict() for user in pagination.items]

    return jsonify({
        'users': users,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': pagination.total,
            'pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    }), 200


@users_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """Obtiene un usuario específico por ID.

    Args:
        user_id (int): ID del usuario.

    Returns:
        JSON: Datos del usuario.
    """
    user = User.find_by_id(user_id)

    if not user:
        return jsonify({'error': 'Usuario no encontrado'}), 404

    if not user.is_active:
        return jsonify({'error': 'Usuario no encontrado'}), 404

    # Obtener ID del usuario actual
    current_user_id = get_jwt_identity()

    # Incluir email solo si es el propio usuario
    include_email = (current_user_id == user_id)

    return jsonify({'user': user.to_dict(include_email=include_email)}), 200


@users_bp.route('', methods=['POST'])
def create_user():
    """Crea un nuevo usuario.

    Body (JSON):
        username (str): Nombre de usuario.
        email (str): Email del usuario.
        password (str): Contraseña.
        first_name (str, opcional): Nombre.
        last_name (str, opcional): Apellido.

    Returns:
        JSON: Usuario creado.
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
        return jsonify({
            'message': 'Usuario creado exitosamente',
            'user': user.to_dict(include_email=True)
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al crear usuario: {str(e)}'}), 500


@users_bp.route('/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    """Actualiza un usuario existente.

    Solo el propio usuario puede actualizar sus datos (excepto admins).

    Args:
        user_id (int): ID del usuario a actualizar.

    Body (JSON):
        email (str, opcional): Nuevo email.
        first_name (str, opcional): Nuevo nombre.
        last_name (str, opcional): Nuevo apellido.
        password (str, opcional): Nueva contraseña.

    Returns:
        JSON: Usuario actualizado.
    """
    current_user_id = get_jwt_identity()

    # Solo el propio usuario puede actualizar sus datos
    if current_user_id != user_id:
        return jsonify({'error': 'No autorizado'}), 403

    user = User.find_by_id(user_id)

    if not user:
        return jsonify({'error': 'Usuario no encontrado'}), 404

    data = request.get_json()

    if not data:
        return jsonify({'error': 'No se proporcionaron datos'}), 400

    # No permitir cambiar username
    if 'username' in data:
        return jsonify({'error': 'No se puede cambiar el username'}), 400

    # Validar datos
    is_valid, errors = validate_user_data(data, is_update=True)
    if not is_valid:
        return jsonify({'errors': errors}), 400

    # Verificar que el email no esté en uso por otro usuario
    if 'email' in data and data['email'] != user.email:
        existing_user = User.find_by_email(data['email'])
        if existing_user and existing_user.id != user_id:
            return jsonify({'error': 'El email ya está en uso'}), 409

    # Actualizar campos
    try:
        if 'email' in data:
            user.email = data['email']
        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']
        if 'password' in data:
            user.set_password(data['password'])

        user.update()

        return jsonify({
            'message': 'Usuario actualizado exitosamente',
            'user': user.to_dict(include_email=True)
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al actualizar usuario: {str(e)}'}), 500


@users_bp.route('/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    """Elimina (desactiva) un usuario.

    Solo el propio usuario puede eliminar su cuenta.

    Args:
        user_id (int): ID del usuario a eliminar.

    Returns:
        JSON: Mensaje de confirmación.
    """
    current_user_id = get_jwt_identity()

    # Solo el propio usuario puede eliminar su cuenta
    if current_user_id != user_id:
        return jsonify({'error': 'No autorizado'}), 403

    user = User.find_by_id(user_id)

    if not user:
        return jsonify({'error': 'Usuario no encontrado'}), 404

    try:
        # En lugar de eliminar, desactivar el usuario
        user.is_active = False
        user.update()

        return jsonify({'message': 'Usuario eliminado exitosamente'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al eliminar usuario: {str(e)}'}), 500
