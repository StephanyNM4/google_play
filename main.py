import json
import logging
from typing import Optional


from fastapi import FastAPI, HTTPException, Query, Request, Response
from contextlib import asynccontextmanager

import uvicorn

from app.models.UserLogin import UserLogin
from app.models.UserRegister import UserRegister
from app.models.MusicCatalog import MusicCatalog

from app.controllers.firebase import register_user_firebase, login_user_firebase
from app.controllers.MusicCatalog import get_music_catalog, create_music_review

from app.utils.database import execute_query_json
from app.utils.security import validateadmin, validate
from app.utils.telemetry import instrument_fastapi_app, setup_simple_telemetry

logging.basicConfig( level=logging.INFO )
logger = logging.getLogger("uvicorn")

telemetry_enabled = setup_simple_telemetry()
if telemetry_enabled:
    logger.info("Application Insights enabled")
else:
    logger.warning("Application Insight disabled")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting API...")
    yield
    logger.info("Shutting down API...")

app = FastAPI(
    title="Google Play Music API",
    description="Music Review API Expert System",
    version="0.0.1",
    lifespan=lifespan
)

if telemetry_enabled:
    instrument_fastapi_app(app)
    logger.info("Application Insights enabled")
    logger.info("FastAPI Instrumented")
else:
    logger.warning("Application Insight disabled")

@app.get("/health")
async def health_check():
    return {
        "status": "healthy"
        , "version": "0.0.1"
    }

@app.get("/")
def read_root():
    return {"message": "¡Hello world!"}

@app.get("/prueba")
@validateadmin
async def read_root(request: Request, response: Response):
    query = "select * from music.TBL_USERS"
    try:
        result = await execute_query_json(query, needs_commit=False)
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

@app.get("/music", response_model=list[MusicCatalog])
async def get_music_review(app: Optional[str] = Query(default=None)):
    music: list[MusicCatalog] = await get_music_catalog(app)
    return music

@app.post("/music", response_model=MusicCatalog, status_code=201)
@validate
async def create_new_music(request: Request, response: Response, music_data: MusicCatalog) -> MusicCatalog:
    cm = await create_music_review(music_data)
    return cm

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")


