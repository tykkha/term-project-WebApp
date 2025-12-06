from typing import Union
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
#from routes import search, sessions, users, tutors, messages, posts, uploads
from routes import search, sessions, users, tutors, messages, posts

from db.Auth import GatorGuidesAuth
from core.config import settings
import logging
from contextlib import asynccontextmanager
import asyncio

logger = logging.getLogger(__name__)

# Global auth instance for cleanup
auth_cleanup_instance = None


async def cleanup_sessions_task():
    global auth_cleanup_instance
    
    while True:
        try:
            await asyncio.sleep(14400)
            
            if not auth_cleanup_instance:
                auth_cleanup_instance = GatorGuidesAuth(
                    host=settings.DATABASE_HOST,
                    database=settings.DATABASE_NAME,
                    user=settings.DATABASE_USER,
                    password=settings.DATABASE_PASSWORD
                )
            
            count = auth_cleanup_instance.cleanup_expired_sessions()
            logger.info(f"Cleaned up {count} expired sessions")
            
        except Exception as e:
            logger.error(f"Session cleanup error: {e}", exc_info=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting GatorGuides API...")
    
    # Start cleanup task
    cleanup_task = asyncio.create_task(cleanup_sessions_task())
    
    yield
    
    # Shutdown
    logger.info("Shutting down GatorGuides API...")
    cleanup_task.cancel()
    
    # Close auth connection
    if auth_cleanup_instance:
        auth_cleanup_instance.close()


app = FastAPI(title="GatorGuides API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


app.include_router(search.router, prefix="/api")
app.include_router(sessions.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(tutors.router, prefix="/api")
app.include_router(messages.router, prefix="/api")
app.include_router(posts.router, prefix="/api")
#app.include_router(uploads.router, prefix="/api")