import os
import jwt
import logging

from datetime import datetime, timedelta, timezone 
from fastapi import HTTPException
from dotenv import load_dotenv
from jwt import PyJWKError
from functools import wraps

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("uvicorn")

SECRET_KEY = os.getenv("FIREBASE_API_KEY")

# Función para crear un JWT
def create_jwt_token(email: str, firstname:str, lastname:str, is_active: bool, is_admin: bool):
    logger.info("create jwt")
    now = datetime.now(timezone.utc)
    expiration = now + timedelta(hours=1)

    payload = {
        "email": email,
        "firstname": firstname,
        "lastname": lastname,
        "active": is_active,
        "admin": is_admin,
        "exp": expiration.timestamp(),
        "iat": now.timestamp()
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    return token