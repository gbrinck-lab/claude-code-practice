"""Tests para endpoints de usuarios.

Este módulo contiene tests para los endpoints REST de gestión de usuarios.
"""

import pytest
from app import create_app
from api.models.user import db, User


@pytest.fixture
def app():
    """Fixture que crea la aplicación Flask en modo testing."""
    app = create_app('testing')

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Fixture que crea un cliente de testing."""
    return app.test_client()


@pytest.fixture
def auth_headers(client):
    """Fixture que crea un usuario y retorna headers de autenticación."""
    # Registrar usuario
    response = client.post('/api/auth/register', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'Test123!@#'
    })

    data = response.get_json()
    token = data['access_token']

    return {'Authorization': f'Bearer {token}'}


class TestGetUsers:
    """Tests para GET /api/users."""

    def test_get_users_without_auth(self, client):
        """Verifica que sin autenticación retorne 401."""
        response = client.get('/api/users')
        assert response.status_code == 401

    def test_get_users_empty_list(self, client, auth_headers):
        """Verifica que retorne lista vacía si no hay usuarios."""
        response = client.get('/api/users', headers=auth_headers)
        assert response.status_code == 200

        data = response.get_json()
        assert 'users' in data
        assert isinstance(data['users'], list)
        assert 'pagination' in data

    def test_get_users_with_pagination(self, client, auth_headers, app):
        """Verifica la paginación de usuarios."""
        # Crear varios usuarios
        with app.app_context():
            for i in range(5):
                user = User(
                    username=f'user{i}',
                    email=f'user{i}@example.com'
                )
                user.set_password('Test123!@#')
                user.save()

        response = client.get('/api/users?page=1&per_page=2', headers=auth_headers)
        assert response.status_code == 200

        data = response.get_json()
        assert len(data['users']) <= 2
        assert data['pagination']['per_page'] == 2


class TestGetUser:
    """Tests para GET /api/users/<id>."""

    def test_get_user_by_id(self, client, auth_headers, app):
        """Verifica que retorne un usuario específico."""
        with app.app_context():
            user = User(username='john', email='john@example.com')
            user.set_password('Test123!@#')
            user.save()
            user_id = user.id

        response = client.get(f'/api/users/{user_id}', headers=auth_headers)
        assert response.status_code == 200

        data = response.get_json()
        assert 'user' in data
        assert data['user']['username'] == 'john'

    def test_get_nonexistent_user(self, client, auth_headers):
        """Verifica que retorne 404 para usuario no existente."""
        response = client.get('/api/users/9999', headers=auth_headers)
        assert response.status_code == 404


class TestCreateUser:
    """Tests para POST /api/users."""

    def test_create_user_success(self, client):
        """Verifica la creación exitosa de un usuario."""
        response = client.post('/api/users', json={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'Test123!@#',
            'first_name': 'New',
            'last_name': 'User'
        })

        assert response.status_code == 201
        data = response.get_json()
        assert 'user' in data
        assert data['user']['username'] == 'newuser'

    def test_create_user_duplicate_username(self, client, app):
        """Verifica que no se puede crear usuario con username duplicado."""
        with app.app_context():
            user = User(username='existing', email='existing@example.com')
            user.set_password('Test123!@#')
            user.save()

        response = client.post('/api/users', json={
            'username': 'existing',
            'email': 'new@example.com',
            'password': 'Test123!@#'
        })

        assert response.status_code == 409

    def test_create_user_invalid_password(self, client):
        """Verifica validación de contraseña débil."""
        response = client.post('/api/users', json={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': '123'  # Contraseña débil
        })

        assert response.status_code == 400
        data = response.get_json()
        assert 'errors' in data


class TestUpdateUser:
    """Tests para PUT /api/users/<id>."""

    def test_update_own_user(self, client, auth_headers, app):
        """Verifica que un usuario puede actualizar sus propios datos."""
        # Obtener ID del usuario actual
        response = client.get('/api/auth/me', headers=auth_headers)
        user_id = response.get_json()['user']['id']

        # Actualizar usuario
        response = client.put(f'/api/users/{user_id}', headers=auth_headers, json={
            'first_name': 'Updated',
            'last_name': 'Name'
        })

        assert response.status_code == 200
        data = response.get_json()
        assert data['user']['first_name'] == 'Updated'

    def test_update_other_user_forbidden(self, client, auth_headers, app):
        """Verifica que no se puede actualizar otro usuario."""
        # Crear otro usuario
        with app.app_context():
            other_user = User(username='other', email='other@example.com')
            other_user.set_password('Test123!@#')
            other_user.save()
            other_id = other_user.id

        # Intentar actualizar otro usuario
        response = client.put(f'/api/users/{other_id}', headers=auth_headers, json={
            'first_name': 'Hacked'
        })

        assert response.status_code == 403


class TestDeleteUser:
    """Tests para DELETE /api/users/<id>."""

    def test_delete_own_user(self, client, auth_headers):
        """Verifica que un usuario puede eliminar su propia cuenta."""
        # Obtener ID del usuario actual
        response = client.get('/api/auth/me', headers=auth_headers)
        user_id = response.get_json()['user']['id']

        # Eliminar usuario
        response = client.delete(f'/api/users/{user_id}', headers=auth_headers)
        assert response.status_code == 200

    def test_delete_other_user_forbidden(self, client, auth_headers, app):
        """Verifica que no se puede eliminar otro usuario."""
        # Crear otro usuario
        with app.app_context():
            other_user = User(username='other', email='other@example.com')
            other_user.set_password('Test123!@#')
            other_user.save()
            other_id = other_user.id

        # Intentar eliminar otro usuario
        response = client.delete(f'/api/users/{other_id}', headers=auth_headers)
        assert response.status_code == 403
