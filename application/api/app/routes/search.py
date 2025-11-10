from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from ..db.Search import GatorGuidesSearch
from ..core.config import settings

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

@router.get("/search/{query}", response_model=List[Dict[str, Any]])
async def search(query: str, search_db: GatorGuidesSearch = Depends(get_search)):

    try:
        results = search_db.search(query)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))