"""Tests para endpoints de autenticación.

Este módulo contiene tests para los endpoints de autenticación y JWT.
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
def test_user(app):
    """Fixture que crea un usuario de prueba."""
    with app.app_context():
        user = User(
            username='testuser',
            email='test@example.com',
            first_name='Test',
            last_name='User'
        )
        user.set_password('Test123!@#')
        user.save()
        return {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'Test123!@#'
        }


class TestRegister:
    """Tests para POST /api/auth/register."""

    def test_register_success(self, client):
        """Verifica registro exitoso de usuario."""
        response = client.post('/api/auth/register', json={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'Test123!@#',
            'first_name': 'New',
            'last_name': 'User'
        })

        assert response.status_code == 201
        data = response.get_json()

        # Verificar respuesta
        assert 'user' in data
        assert 'access_token' in data
        assert 'refresh_token' in data
        assert data['user']['username'] == 'newuser'

    def test_register_duplicate_username(self, client, test_user):
        """Verifica que no se puede registrar username duplicado."""
        response = client.post('/api/auth/register', json={
            'username': 'testuser',  # Ya existe
            'email': 'new@example.com',
            'password': 'Test123!@#'
        })

        assert response.status_code == 409

    def test_register_duplicate_email(self, client, test_user):
        """Verifica que no se puede registrar email duplicado."""
        response = client.post('/api/auth/register', json={
            'username': 'newuser',
            'email': 'test@example.com',  # Ya existe
            'password': 'Test123!@#'
        })

        assert response.status_code == 409

    def test_register_invalid_email(self, client):
        """Verifica validación de email inválido."""
        response = client.post('/api/auth/register', json={
            'username': 'newuser',
            'email': 'invalid-email',
            'password': 'Test123!@#'
        })

        assert response.status_code == 400

    def test_register_weak_password(self, client):
        """Verifica validación de contraseña débil."""
        response = client.post('/api/auth/register', json={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': '123'  # Muy débil
        })

        assert response.status_code == 400


class TestLogin:
    """Tests para POST /api/auth/login."""

    def test_login_success_with_username(self, client, test_user):
        """Verifica login exitoso con username."""
        response = client.post('/api/auth/login', json={
            'username': 'testuser',
            'password': 'Test123!@#'
        })

        assert response.status_code == 200
        data = response.get_json()

        assert 'user' in data
        assert 'access_token' in data
        assert 'refresh_token' in data

    def test_login_success_with_email(self, client, test_user):
        """Verifica login exitoso con email."""
        response = client.post('/api/auth/login', json={
            'username': 'test@example.com',  # Usar email como username
            'password': 'Test123!@#'
        })

        assert response.status_code == 200

    def test_login_invalid_password(self, client, test_user):
        """Verifica que contraseña incorrecta retorne 401."""
        response = client.post('/api/auth/login', json={
            'username': 'testuser',
            'password': 'WrongPassword123!'
        })

        assert response.status_code == 401

    def test_login_nonexistent_user(self, client):
        """Verifica que usuario no existente retorne 401."""
        response = client.post('/api/auth/login', json={
            'username': 'nonexistent',
            'password': 'Test123!@#'
        })

        assert response.status_code == 401

    def test_login_missing_credentials(self, client):
        """Verifica que credenciales faltantes retornen 400."""
        response = client.post('/api/auth/login', json={
            'username': 'testuser'
            # Falta password
        })

        assert response.status_code == 400


class TestRefresh:
    """Tests para POST /api/auth/refresh."""

    def test_refresh_token_success(self, client):
        """Verifica refresh de token exitoso."""
        # Registrar usuario
        register_response = client.post('/api/auth/register', json={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'Test123!@#'
        })

        refresh_token = register_response.get_json()['refresh_token']

        # Refrescar token
        response = client.post('/api/auth/refresh',
                              headers={'Authorization': f'Bearer {refresh_token}'})

        assert response.status_code == 200
        data = response.get_json()
        assert 'access_token' in data

    def test_refresh_with_access_token_fails(self, client):
        """Verifica que no se puede refrescar con access token."""
        # Registrar usuario
        register_response = client.post('/api/auth/register', json={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'Test123!@#'
        })

        access_token = register_response.get_json()['access_token']

        # Intentar refrescar con access token (debería fallar)
        response = client.post('/api/auth/refresh',
                              headers={'Authorization': f'Bearer {access_token}'})

        assert response.status_code == 422


class TestLogout:
    """Tests para POST /api/auth/logout."""

    def test_logout_success(self, client):
        """Verifica logout exitoso."""
        # Registrar y hacer login
        register_response = client.post('/api/auth/register', json={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'Test123!@#'
        })

        access_token = register_response.get_json()['access_token']

        # Logout
        response = client.post('/api/auth/logout',
                              headers={'Authorization': f'Bearer {access_token}'})

        assert response.status_code == 200


class TestGetCurrentUser:
    """Tests para GET /api/auth/me."""

    def test_get_current_user(self, client):
        """Verifica obtención del usuario actual."""
        # Registrar usuario
        register_response = client.post('/api/auth/register', json={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'Test123!@#',
            'first_name': 'Test',
            'last_name': 'User'
        })

        access_token = register_response.get_json()['access_token']

        # Obtener usuario actual
        response = client.get('/api/auth/me',
                             headers={'Authorization': f'Bearer {access_token}'})

        assert response.status_code == 200
        data = response.get_json()

        assert 'user' in data
        assert data['user']['username'] == 'testuser'
        assert data['user']['email'] == 'test@example.com'

    def test_get_current_user_without_token(self, client):
        """Verifica que sin token retorne 401."""
        response = client.get('/api/auth/me')
        assert response.status_code == 401
