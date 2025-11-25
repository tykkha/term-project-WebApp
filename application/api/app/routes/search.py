from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from db.Search import GatorGuidesSearch  # Changed from app.db.Search to db.Search
from core.config import settings
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
search_instance = None

def get_search():
    global search_instance
    if not search_instance:
        search_instance = GatorGuidesSearch(
            host=settings.DATABASE_HOST,
            database=settings.DATABASE_NAME,
            user=settings.DATABASE_USER,
            password=settings.DATABASE_PASSWORD
        )
    return search_instance

# Search for tutors via tags and ratings
@router.get("/search/{query}", response_model=List[Dict[str, Any]])
async def search(query: str, search_db: GatorGuidesSearch = Depends(get_search)):

    try:
        results = search_db.search(query)
        return results
    except Exception as e:
        logger.error(f"Search error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# Returns top 10 tutors based on ratings 
@router.get("/tutors/top", response_model=List[Dict[str, Any]])
async def get_top_tutors(search_db: GatorGuidesSearch = Depends(get_search)):
    try:
        results = search_db.get_top_tutors(limit=10)
        return results
    except Exception as e:
        logger.error(f"Top tutors error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# Returns all available courses in the database
@router.get("/tags", response_model=List[Dict[str, Any]])
async def get_all_tags(search_db: GatorGuidesSearch = Depends(get_search)):
    try:
        if not search_db._ensure_connection():
            raise HTTPException(status_code=500, detail="Database connection failed")
        
        query = "SELECT tagsID, tags FROM Tags ORDER BY tags"
        search_db.cursor.execute(query)
        tags = search_db.cursor.fetchall()
        
        return [{"id": tag["tagsID"], "name": tag["tags"]} for tag in tags]
    except Exception as e:
        logger.error(f"Get tags error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))