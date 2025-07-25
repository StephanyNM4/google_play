import json
import logging
from typing import Optional

from fastapi import HTTPException

from app.utils.database import execute_query_json
from app.utils.redis_cache import get_redis_client, store_in_cache, get_from_cache, delete_cache
from app.models.MusicCatalog import MusicCatalog

logger = logging.getLogger(__name__)

MUSIC_CACHE_KEY1 = "music:catalog:all"
CACHE_TTL = 1800

async def get_music_catalog(app : Optional[str] = None) -> list[MusicCatalog]:
    redis_client = get_redis_client()
    
    MUSIC_CACHE_KEY = f"{MUSIC_CACHE_KEY1}:app:{app}" if app else MUSIC_CACHE_KEY1

    if redis_client:
        cache_data = get_from_cache(redis_client, MUSIC_CACHE_KEY)
        if cache_data:
            return [MusicCatalog(**item) for item in cache_data]
    else:
        logger.warning("Redis client is None, skipping cache.")
    
    if app:
        query = """ 
            SELECT * FROM music.music_review 
            WHERE app = ? 
        """
        result = await execute_query_json(query, [app])
    else:
        query = "SELECT TOP 40000 * FROM music.music_review"
        result = await execute_query_json(query)
    
    
    dict = json.loads(result)
    
    if not dict:
        raise HTTPException(status_code=401, detail="Music catalog not found")
    
    if redis_client:
        store_in_cache( redis_client , MUSIC_CACHE_KEY , dict , CACHE_TTL )

    return [ MusicCatalog(**item) for item in dict ]

async def create_music_review( music_data: MusicCatalog ) -> MusicCatalog:

    insert_query = """
        insert into music.music_review(
            app
            , review
            , rating
            , version
            , date
        ) values(
            ?, ?, ?, ?, ?
        )
    """

    params = [
    str(music_data.app) if music_data.app else None,
    str(music_data.review) if music_data.review else None,
    float(music_data.rating) if music_data.rating is not None else None,
    str(music_data.version) if music_data.version else None,
    music_data.review_date.isoformat() if music_data.review_date else None
]

    await execute_query_json( insert_query , params, needs_commit=True )

    created_object = MusicCatalog(
        app= music_data.app,
        review= music_data.review,
        rating= music_data.rating,
        version= music_data.version,
        review_date= music_data.review_date
    )

    redis_client = get_redis_client()
    
    if redis_client:
        delete_cache( redis_client, MUSIC_CACHE_KEY1 )

        app = music_data.app
        if app:
            key = f"{MUSIC_CACHE_KEY1}:app:{app}"
            delete_cache(redis_client, key)


    return created_object