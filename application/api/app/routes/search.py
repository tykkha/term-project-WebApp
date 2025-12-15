from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from dependencies import get_search_manager
from db.Search import GatorGuidesSearch
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Searches for tutors based on tags and names
@router.get("/search", response_model=List[Dict[str, Any]])
@router.get("/search/{query}", response_model=List[Dict[str, Any]])
async def search(query: str = "", search_db: GatorGuidesSearch = Depends(get_search_manager)):
    try:
        search_query = query.strip() if query else ""
        results = search_db.search(search_query)
        return results
    except Exception as e:
        logger.error(f"Search error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# Returns all available courses in the database
@router.get("/tags", response_model=List[Dict[str, Any]])
async def get_all_tags(search_db: GatorGuidesSearch = Depends(get_search_manager)):
    try:
        tags = search_db.get_all_tags()
        return tags
    except Exception as e:
        logger.error(f"Get tags error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))