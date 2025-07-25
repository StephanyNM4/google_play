from fastapi import FastAPI, HTTPException

from app.models.UserLogin import UserLogin
from app.models.UserRegister import UserRegister

from app.controllers.firebase import register_user_firebase, login_user_firebase

from app.utils.database import execute_query_json
import json

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "¡Hello world!"}

@app.get("/prueba")
async def read_root():
    query = "select * from music.USERS"
    try:
        result = await execute_query_json(query, needs_commit=False)
        print(result)
        result_dict = json.loads(result)
        return result_dict
    except Exception as e:
        return HTTPException(status_code=500, detail=str(e))
    
@app.post("/login/custom")
async def login_custom(user: UserLogin):
    return await login_user_firebase(user)

@app.post("/signup")
async def register(user: UserRegister):
    return await register_user_firebase(user)


