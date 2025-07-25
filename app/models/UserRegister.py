from typing import Optional
from pydantic import BaseModel, field_validator, Field
import re

from app.utils.globalf import validate_sql_injection

class UserRegister(BaseModel):

    email: str = Field(
        pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
        description="Email del usuario, debe ser un correo válido"
    )

    password: str = Field(
        min_length=8,
        max_length=64,
        description="Contraseña del usuario, debe tener ntre 8 y 64 caracteres, incluir por lo menos un numero, una mayuscula y un caracter especial"
    )

    firstname: str = Field(
        min_length=1,
        max_length=50,
        description="Nombres del usuario, debe tener entre 1 y 50 caracteres",
        pattern=r"^[a-zA-ZÀ-ÿ\s]+$"
    )

    lastname: str = Field(
        min_length=1,
        max_length=50,
        description="Apellidos del usuario, debe tener entre 1 y 50 caracteres",
        pattern=r"^[a-zA-ZÀ-ÿ\s]+$"
    )

    is_active: Optional[bool] = Field(
        default=True,
        description="Indica si el usuario está activo, por defecto es true"
    )

    is_admin: Optional[bool] = Field(
        default=True,
        description="Indica si el usuario tiene permisos administrativos"
    )

    @field_validator('password')
    @classmethod
    def password_validation(cls, value):
        if len(value) < 8:
            raise ValueError('La contraseña debe tener al menos 6 caracteres')

        if not re.search(r'[A-Z]', value):
            raise ValueError('La contraseña debe contener al menos una letra mayúscula')

        if not re.search(r'[0-9]', value):
            raise ValueError('La contraseña debe contener al menos un número')

        if not re.search(r'[\W_]', value):  
            raise ValueError('La contraseña debe contener al menos un carácter especial')
        return value

    @field_validator('firstname')
    @classmethod
    def name_validation(cls, value):
        if validate_sql_injection(value):
            raise ValueError('Invalid name')

        return value

    @field_validator('lastname')
    @classmethod
    def name_validation(cls, value):
        if validate_sql_injection(value):
            raise ValueError('Invalid name')

        return value

    @field_validator('email')
    @classmethod
    def email_validation(cls, value):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", value):
            raise ValueError('Invalid email address')

        return value