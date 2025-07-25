import json
import os
from dotenv import load_dotenv
import logging
from fastapi import HTTPException


import firebase_admin
from firebase_admin import credentials, auth as firebase_auth
import requests

from app.models.UserLogin import UserLogin
from app.models.UserRegister import UserRegister
from app.utils.database import execute_query_json
from app.utils.security import create_jwt_token

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("uvicorn")

# Inicializar la app de Firebase Admin
cred = credentials.Certificate("secrets/firebase-adminsdk.json")
firebase_admin.initialize_app(cred)

load_dotenv()

async def register_user_firebase(user: UserRegister):
    user_record = {}
    try:
        # Crear usuario en Firebase Authentication
        user_record = firebase_auth.create_user(
            email=user.email,
            password=user.password
        )

    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=400,
            detail=f"Error al registrar usuario: {e}"
        )

    query = f"exec music.create_user ?, ?, ?, ?, ?"
    params = (
        user_record.email,
        user.firstname,
        user.lastname,
        user.is_active,
        user.is_admin
    )

    try:
        result_json = await execute_query_json(query, params, needs_commit=True)
        logger.info(result_json)
        return json.loads(result_json)

    except Exception as e:
        firebase_auth.delete_user(user_record.uid)
        raise HTTPException(status_code=500, detail=str(e))


async def login_user_firebase(user: UserLogin):
        # Autenticar usuario con Firebase Authentication usando la API REST
        api_key = os.getenv("FIREBASE_API_KEY") 
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
        payload = {
            "email": user.email,
            "password": user.password,
            "returnSecureToken": True
        }
        response = requests.post(url, json=payload)
        response_data = response.json()

        if "error" in response_data:
            raise HTTPException(
                status_code=400,
                detail=f"Error al autenticar usuario: {response_data['error']['message']}"
            )
        
        query = f"""select
                        email
                        , firstname
                        , lastname
                        , is_active
                        , is_admin
                    from music.TBL_USERS
                    where email = ?
                    """

        try:
            result_json = await execute_query_json(query, (user.email,), needs_commit=False)
            logger.info(result_json)
            result_dict = json.loads(result_json)

            token = create_jwt_token(
                result_dict[0]["email"],
                result_dict[0]["firstname"],
                result_dict[0]["lastname"],
                result_dict[0]["is_active"],
                result_dict[0]["is_admin"],
            )

            logger.info(token)

            return {
                "message": "Usuario autenticado exitosamente",
                "idToken": token
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
