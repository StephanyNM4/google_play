import os
import jwt
import logging

from datetime import datetime, timedelta, timezone 
from fastapi import HTTPException
from dotenv import load_dotenv
from jwt import PyJWKError, PyJWTError
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

def validate(func):
    @wraps(func)
    async def wrapper( *args, **kwargs ):
        request = kwargs.get('request')
        if not request:
            raise HTTPException(status_code=400, detail="Request object not found" )

        authorization: str = request.headers.get("Authorization")
        if not authorization:
            raise HTTPException(status_code=400, detail="Authorization header missing" )

        schema, token = authorization.split()
        if schema.lower() != "bearer":
            raise HTTPException(status_code=400, detail="Invalid auth schema" )


        try:
            payload = jwt.decode( token , SECRET_KEY , algorithms=["HS256"] )
            email = payload.get("email")
            firstname = payload.get("firstname")
            lastname = payload.get("lastname")
            active = payload.get("active")
            exp = payload.get("exp")

            if email is None or exp is None or active is None:
                raise HTTPException(status_code=400, detail="Invalid token 3" )

            if datetime.utcfromtimestamp(exp) < datetime.utcnow():
                raise HTTPException( status_code=401, detail="Expired token" )

            if not active:
                raise HTTPException( status_code=403, detail="Inactive user" )

            request.state.email = email
            request.state.firstname = firstname
            request.state.lastname = lastname

        except PyJWTError:
            raise HTTPException( status_code=401 , detail="Invalid token or expired token" )

        return await func( *args, **kwargs )
    return wrapper

def validateadmin(func):
    @wraps(func)
    async def wrapper( *args, **kwargs ):
        request = kwargs.get('request')
        if not request:
            raise HTTPException(status_code=400, detail="Request object not found" )

        authorization: str = request.headers.get("Authorization")
        if not authorization:
            raise HTTPException(status_code=400, detail="Authorization header missing" )

        schema, token = authorization.split()
        if schema.lower() != "bearer":
            raise HTTPException(status_code=400, detail="Invalid auth schema" )


        try:
            payload = jwt.decode( token , SECRET_KEY , algorithms=["HS256"] )
            email = payload.get("email")
            firstname = payload.get("firstname")
            lastname = payload.get("lastname")
            active = payload.get("active")
            admin = payload.get("admin")
            exp = payload.get("exp")

            if email is None or exp is None or active is None:
                raise HTTPException(status_code=400, detail="Invalid token 3" )

            if datetime.utcfromtimestamp(exp) < datetime.utcnow():
                raise HTTPException( status_code=401, detail="Expired token" )

            if not active:
                raise HTTPException( status_code=403, detail="Inactive user" )

            if not admin:
                raise HTTPException( status_code=403, detail="Not Admin!" )

            request.state.email = email
            request.state.firstname = firstname
            request.state.lastname = lastname

        except PyJWTError:
            raise HTTPException( status_code=401 , detail="Invalid token or expired token" )

        return await func( *args, **kwargs )
    return wrapper