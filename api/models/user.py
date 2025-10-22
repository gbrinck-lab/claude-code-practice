"""Modelo de Usuario para la API.

Este módulo define el modelo User usando SQLAlchemy con métodos
para autenticación y gestión de usuarios.
"""

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
import bcrypt

# Instancia de SQLAlchemy (se inicializa en app.py)
db = SQLAlchemy()


class User(db.Model):
    """Modelo de Usuario para autenticación y gestión.

    Attributes:
        id (int): ID único del usuario (primary key).
        username (str): Nombre de usuario único.
        email (str): Email único del usuario.
        password_hash (str): Hash de la contraseña del usuario.
        first_name (str): Nombre del usuario.
        last_name (str): Apellido del usuario.
        is_active (bool): Indica si el usuario está activo.
        is_admin (bool): Indica si el usuario es administrador.
        created_at (datetime): Fecha de creación del usuario.
        updated_at (datetime): Fecha de última actualización.
    """

    __tablename__ = 'users'

    # Campos del modelo
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(100), nullable=True)
    last_name = db.Column(db.String(100), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    def __repr__(self):
        """Representación del modelo User."""
        return f'<User {self.username}>'

    def set_password(self, password):
        """Genera y almacena el hash de la contraseña.

        Args:
            password (str): Contraseña en texto plano.
        """
        # Generar salt y hash de la contraseña
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def check_password(self, password):
        """Verifica si una contraseña coincide con el hash almacenado.

        Args:
            password (str): Contraseña en texto plano a verificar.

        Returns:
            bool: True si la contraseña es correcta, False en caso contrario.
        """
        if not password or not self.password_hash:
            return False

        return bcrypt.checkpw(
            password.encode('utf-8'),
            self.password_hash.encode('utf-8')
        )

    def to_dict(self, include_email=False):
        """Convierte el usuario a diccionario para respuestas JSON.

        Args:
            include_email (bool): Si incluir el email en la respuesta.

        Returns:
            dict: Diccionario con los datos del usuario.
        """
        data = {
            'id': self.id,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

        # Solo incluir email si es solicitado (por ejemplo, para el propio usuario)
        if include_email:
            data['email'] = self.email

        # Solo incluir is_admin si es True
        if self.is_admin:
            data['is_admin'] = self.is_admin

        return data

    @property
    def full_name(self):
        """Obtiene el nombre completo del usuario.

        Returns:
            str: Nombre completo o username si no hay nombre/apellido.
        """
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        else:
            return self.username

    @classmethod
    def find_by_username(cls, username):
        """Busca un usuario por nombre de usuario.

        Args:
            username (str): Nombre de usuario a buscar.

        Returns:
            User: Usuario encontrado o None.
        """
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_email(cls, email):
        """Busca un usuario por email.

        Args:
            email (str): Email a buscar.

        Returns:
            User: Usuario encontrado o None.
        """
        return cls.query.filter_by(email=email).first()

    @classmethod
    def find_by_id(cls, user_id):
        """Busca un usuario por ID.

        Args:
            user_id (int): ID del usuario a buscar.

        Returns:
            User: Usuario encontrado o None.
        """
        return cls.query.get(user_id)

    def save(self):
        """Guarda el usuario en la base de datos."""
        db.session.add(self)
        db.session.commit()

    def delete(self):
        """Elimina el usuario de la base de datos."""
        db.session.delete(self)
        db.session.commit()

    def update(self, **kwargs):
        """Actualiza los campos del usuario.

        Args:
            **kwargs: Campos a actualizar.
        """
        for key, value in kwargs.items():
            if hasattr(self, key) and key != 'id':
                setattr(self, key, value)

        self.updated_at = datetime.utcnow()
        db.session.commit()
