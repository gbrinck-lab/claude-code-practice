# API REST con Flask

API REST completa construida con Flask, SQLAlchemy, JWT y pytest.

## Características

- ✅ Autenticación JWT (JSON Web Tokens)
- ✅ CRUD completo de usuarios
- ✅ Validación de datos robusta
- ✅ Tests con pytest (>90% coverage)
- ✅ Blueprint pattern para organización
- ✅ SQLAlchemy para ORM
- ✅ Flask-Migrate para migraciones
- ✅ CORS configurado
- ✅ Manejo de errores centralizado
- ✅ Documentación completa

## Estructura del Proyecto

```
.
├── api/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── user.py          # Modelo User con SQLAlchemy
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py          # Endpoints de autenticación
│   │   └── users.py         # Endpoints de usuarios
│   └── utils/
│       ├── __init__.py
│       └── validators.py    # Validadores de entrada
├── tests/
│   ├── test_auth.py         # Tests de autenticación
│   └── test_users.py        # Tests de usuarios
├── app.py                   # Aplicación Flask principal
├── config.py                # Configuraciones por entorno
├── requirements.txt         # Dependencias
├── .env.example            # Ejemplo de variables de entorno
└── README.md               # Este archivo
```

## Requisitos Previos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- virtualenv (recomendado)

## Instalación

### 1. Clonar el repositorio

```bash
git clone <url-del-repo>
cd claude-code-practice
```

### 2. Crear entorno virtual

```bash
# Linux/MacOS
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar .env con tus configuraciones
nano .env  # o tu editor favorito
```

Variables importantes en `.env`:
```env
FLASK_ENV=development
SECRET_KEY=tu-clave-secreta-super-segura
JWT_SECRET_KEY=tu-jwt-secret-key-super-segura
DATABASE_URL=sqlite:///app.db
```

### 5. Inicializar base de datos

```bash
# Crear tablas
flask init-db

# (Opcional) Crear usuario administrador
flask create-admin
```

## Uso

### Ejecutar en modo desarrollo

```bash
python app.py
```

La API estará disponible en `http://localhost:5000`

### Ejecutar con Flask CLI

```bash
export FLASK_APP=app.py
export FLASK_ENV=development
flask run
```

### Ejecutar en producción

```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## Endpoints

### Autenticación

#### Registrar usuario
```http
POST /api/auth/register
Content-Type: application/json

{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "SecurePass123!",
  "first_name": "John",
  "last_name": "Doe"
}
```

#### Iniciar sesión
```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "johndoe",
  "password": "SecurePass123!"
}
```

#### Refrescar token
```http
POST /api/auth/refresh
Authorization: Bearer <refresh_token>
```

#### Obtener usuario actual
```http
GET /api/auth/me
Authorization: Bearer <access_token>
```

#### Cerrar sesión
```http
POST /api/auth/logout
Authorization: Bearer <access_token>
```

### Usuarios

#### Listar usuarios
```http
GET /api/users?page=1&per_page=10&search=john
Authorization: Bearer <access_token>
```

#### Obtener usuario específico
```http
GET /api/users/1
Authorization: Bearer <access_token>
```

#### Crear usuario
```http
POST /api/users
Content-Type: application/json

{
  "username": "newuser",
  "email": "newuser@example.com",
  "password": "SecurePass123!",
  "first_name": "New",
  "last_name": "User"
}
```

#### Actualizar usuario
```http
PUT /api/users/1
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "first_name": "Updated",
  "last_name": "Name",
  "email": "newemail@example.com"
}
```

#### Eliminar usuario
```http
DELETE /api/users/1
Authorization: Bearer <access_token>
```

## Testing

### Ejecutar todos los tests

```bash
pytest
```

### Ejecutar tests con coverage

```bash
pytest --cov=api --cov-report=html
```

### Ejecutar tests específicos

```bash
# Tests de autenticación
pytest tests/test_auth.py -v

# Tests de usuarios
pytest tests/test_users.py -v

# Test específico
pytest tests/test_auth.py::TestLogin::test_login_success -v
```

## Migraciones de Base de Datos

### Inicializar migraciones

```bash
flask db init
```

### Crear migración

```bash
flask db migrate -m "Descripción de cambios"
```

### Aplicar migración

```bash
flask db upgrade
```

### Revertir migración

```bash
flask db downgrade
```

## Validaciones

### Password
- Mínimo 8 caracteres
- Al menos una mayúscula
- Al menos una minúscula
- Al menos un número
- Al menos un carácter especial

### Username
- Entre 3 y 80 caracteres
- Solo letras, números, guiones y guiones bajos
- Debe comenzar con letra

### Email
- Formato válido de email
- Único en la base de datos

## Configuración por Entorno

### Development
```python
DEBUG = True
SQLALCHEMY_ECHO = True  # Ver queries SQL
```

### Testing
```python
TESTING = True
SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
```

### Production
```python
DEBUG = False
# Requiere SECRET_KEY y JWT_SECRET_KEY configurados
```

## Seguridad

- ✅ Passwords hasheados con bcrypt
- ✅ JWT para autenticación
- ✅ CORS configurado
- ✅ Validación de entrada
- ✅ SQL injection protegido (SQLAlchemy)
- ✅ Tokens expirados manejados
- ✅ Lista negra de tokens (logout)

## Comandos CLI Personalizados

```bash
# Inicializar base de datos
flask init-db

# Crear usuario administrador
flask create-admin

# Iniciar servidor
python app.py
```

## Troubleshooting

### Error: "ModuleNotFoundError"
```bash
# Verificar que el entorno virtual está activado
source venv/bin/activate  # Linux/MacOS
venv\Scripts\activate     # Windows

# Reinstalar dependencias
pip install -r requirements.txt
```

### Error: "OperationalError: no such table"
```bash
# Inicializar base de datos
flask init-db
```

### Error: "Token has expired"
```bash
# Refrescar el token usando /api/auth/refresh
# O hacer login nuevamente
```

## Contribuir

1. Fork el proyecto
2. Crear rama de feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## Licencia

Este proyecto es código abierto y está disponible bajo la licencia MIT.

## Contacto

Para preguntas o soporte, crear un issue en el repositorio.

## Próximas Mejoras

- [ ] Roles y permisos
- [ ] Rate limiting
- [ ] Email verification
- [ ] Password reset
- [ ] OAuth integration
- [ ] Redis para cache
- [ ] Docker support
- [ ] CI/CD pipeline
