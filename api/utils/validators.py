"""Validadores para la API.

Este módulo contiene funciones de validación para datos de entrada
como emails, passwords, usernames, etc.
"""

import re
from email_validator import validate_email, EmailNotValidError


def validate_username(username):
    """Valida que un username cumpla con los requisitos.

    Requisitos:
    - Entre 3 y 80 caracteres
    - Solo letras, números, guiones y guiones bajos
    - Debe comenzar con una letra

    Args:
        username (str): Username a validar.

    Returns:
        tuple: (es_valido, mensaje_error)
    """
    if not username:
        return False, "El username es requerido"

    if len(username) < 3:
        return False, "El username debe tener al menos 3 caracteres"

    if len(username) > 80:
        return False, "El username no puede exceder 80 caracteres"

    # Debe comenzar con letra
    if not username[0].isalpha():
        return False, "El username debe comenzar con una letra"

    # Solo letras, números, guiones y guiones bajos
    if not re.match(r'^[a-zA-Z][a-zA-Z0-9_-]*$', username):
        return False, "El username solo puede contener letras, números, guiones y guiones bajos"

    return True, None


def validate_email_address(email):
    """Valida que un email sea válido.

    Args:
        email (str): Email a validar.

    Returns:
        tuple: (es_valido, mensaje_error)
    """
    if not email:
        return False, "El email es requerido"

    try:
        # Validar email usando email-validator
        validate_email(email, check_deliverability=False)
        return True, None
    except EmailNotValidError as e:
        return False, f"Email inválido: {str(e)}"


def validate_password(password):
    """Valida que una contraseña cumpla con los requisitos de seguridad.

    Requisitos:
    - Al menos 8 caracteres
    - Al menos una letra mayúscula
    - Al menos una letra minúscula
    - Al menos un número
    - Al menos un carácter especial

    Args:
        password (str): Contraseña a validar.

    Returns:
        tuple: (es_valida, mensaje_error)
    """
    if not password:
        return False, "La contraseña es requerida"

    if len(password) < 8:
        return False, "La contraseña debe tener al menos 8 caracteres"

    if len(password) > 128:
        return False, "La contraseña no puede exceder 128 caracteres"

    # Al menos una letra mayúscula
    if not re.search(r'[A-Z]', password):
        return False, "La contraseña debe contener al menos una letra mayúscula"

    # Al menos una letra minúscula
    if not re.search(r'[a-z]', password):
        return False, "La contraseña debe contener al menos una letra minúscula"

    # Al menos un número
    if not re.search(r'\d', password):
        return False, "La contraseña debe contener al menos un número"

    # Al menos un carácter especial
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "La contraseña debe contener al menos un carácter especial (!@#$%^&*(),.?\":{}|<>)"

    return True, None


def validate_name(name, field_name="nombre"):
    """Valida que un nombre sea válido.

    Args:
        name (str): Nombre a validar.
        field_name (str): Nombre del campo para mensajes de error.

    Returns:
        tuple: (es_valido, mensaje_error)
    """
    if not name:
        return True, None  # Los nombres son opcionales

    if len(name) > 100:
        return False, f"El {field_name} no puede exceder 100 caracteres"

    # Solo letras, espacios, guiones y apóstrofes
    if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s'-]+$", name):
        return False, f"El {field_name} solo puede contener letras, espacios, guiones y apóstrofes"

    return True, None


def validate_user_data(data, is_update=False):
    """Valida los datos completos de un usuario.

    Args:
        data (dict): Diccionario con los datos del usuario.
        is_update (bool): Si es una actualización (campos opcionales).

    Returns:
        tuple: (es_valido, dict_errores)
    """
    errors = {}

    # Validar username
    if 'username' in data:
        is_valid, error = validate_username(data['username'])
        if not is_valid:
            errors['username'] = error
    elif not is_update:
        errors['username'] = "El username es requerido"

    # Validar email
    if 'email' in data:
        is_valid, error = validate_email_address(data['email'])
        if not is_valid:
            errors['email'] = error
    elif not is_update:
        errors['email'] = "El email es requerido"

    # Validar password (solo si está presente)
    if 'password' in data:
        is_valid, error = validate_password(data['password'])
        if not is_valid:
            errors['password'] = error
    elif not is_update:
        errors['password'] = "La contraseña es requerida"

    # Validar first_name (opcional)
    if 'first_name' in data and data['first_name']:
        is_valid, error = validate_name(data['first_name'], "nombre")
        if not is_valid:
            errors['first_name'] = error

    # Validar last_name (opcional)
    if 'last_name' in data and data['last_name']:
        is_valid, error = validate_name(data['last_name'], "apellido")
        if not is_valid:
            errors['last_name'] = error

    return len(errors) == 0, errors


def validate_pagination_params(page, per_page, max_per_page=100):
    """Valida los parámetros de paginación.

    Args:
        page (int): Número de página.
        per_page (int): Cantidad de items por página.
        max_per_page (int): Máximo de items por página permitidos.

    Returns:
        tuple: (es_valido, mensaje_error)
    """
    try:
        page = int(page) if page else 1
        per_page = int(per_page) if per_page else 10
    except (ValueError, TypeError):
        return False, "Los parámetros de paginación deben ser números"

    if page < 1:
        return False, "El número de página debe ser mayor a 0"

    if per_page < 1:
        return False, "La cantidad de items por página debe ser mayor a 0"

    if per_page > max_per_page:
        return False, f"La cantidad de items por página no puede exceder {max_per_page}"

    return True, None
