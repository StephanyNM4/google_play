from pydantic import BaseModel, field_validator
import re


class UserLogin(BaseModel):
    email: str
    password: str

    @field_validator('password')
    @classmethod
    def password_validation(cls, value):
        if len(value) < 6:
            raise ValueError('INVALID_LOGIN_CREDENTIALS')

        if not re.search(r'[A-Z]', value):
            raise ValueError('INVALID_LOGIN_CREDENTIALS')

        if not re.search(r'[\W_]', value):  # \W matches any non-word character
            raise ValueError('INVALID_LOGIN_CREDENTIALS')

        if re.search(r'(012|123|234|345|456|567|678|789|890)', value):
            raise ValueError('INVALID_LOGIN_CREDENTIALS')

        return value

    @field_validator('email')
    @classmethod
    def email_validation(cls, value):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", value):
            raise ValueError('Invalid email address')

        return value