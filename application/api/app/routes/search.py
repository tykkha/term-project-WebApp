from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from db.Search import GatorGuidesSearch
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

# Searches for tutors based on tags and names
@router.get("/search/{query}", response_model=List[Dict[str, Any]])
async def search(query: str, search_db: GatorGuidesSearch = Depends(get_search)):

    try:
        results = search_db.search(query)
        return results
    except Exception as e:
        logger.error(f"Search error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    
# Gets top tutors based on ratings
@router.get("/tutors/top", response_model=List[Dict[str, Any]])
async def get_top_tutors(search_db: GatorGuidesSearch = Depends(get_search)):
    try:
        results = search_db.get_top_tutors(limit=10)
        return results
    except Exception as e:
        logger.error(f"Top tutors error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))