from typing import Union
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import search, sessions, users, tutors, messages, posts, uploads
from db.Auth import ConnectionPool, ConnectionCleaner, GatorGuidesAuth
from db.Sessions import GatorGuidesSessions
from db.Users import GatorGuidesUsers
from db.Tutors import GatorGuidesTutors
from db.Posts import GatorGuidesPosts
from db.Messages import GatorGuidesMessages
from db.Search import GatorGuidesSearch
from db.Availability import GatorGuidesAvailability
from dependencies import (
    set_auth_manager_instance, 
    set_session_manager_instance, 
    set_users_manager_instance, 
    set_tutors_manager_instance, 
    set_posts_manager_instance, 
    set_messages_manager_instance, 
    set_search_manager_instance,
    set_availability_manager_instance
)
from core.config import settings
import logging
from contextlib import asynccontextmanager
import asyncio

logger = logging.getLogger(__name__)

# Global instances
auth_manager_instance = None
session_manager_instance = None
cleaner = ConnectionCleaner(check_interval=600)


async def cleanup_sessions_task():
    while True:
        try:
            await asyncio.sleep(14400)
            
            if auth_manager_instance:
                count = auth_manager_instance.cleanup_expired_sessions()
                logger.info(f"Cleaned up {count} expired sessions")
            
        except asyncio.CancelledError:
            logger.info("Session cleanup task cancelled")
            break
        except Exception as e:
            logger.error(f"Session cleanup error: {e}", exc_info=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    global auth_manager_instance, session_manager_instance
    
    # Startup
    logger.info("Starting GatorGuides API...")
    
    cleanup_task = None
    
    try:
        pool = ConnectionPool()
        pool.initialize(
            host=settings.DATABASE_HOST,
            database=settings.DATABASE_NAME,
            user=settings.DATABASE_USER,
            password=settings.DATABASE_PASSWORD,
            pool_size=10
        )
        logger.info("Connection pool initialized")

        cleaner.start()
        logger.info("Connection cleaner started")
        
        auth_manager_instance = GatorGuidesAuth()
        session_manager_instance = GatorGuidesSessions()
        users_manager = GatorGuidesUsers()
        tutors_manager = GatorGuidesTutors()
        posts_manager = GatorGuidesPosts()
        messages_manager = GatorGuidesMessages()
        search_manager = GatorGuidesSearch()
        availability_manager = GatorGuidesAvailability()

        set_tutors_manager_instance(tutors_manager)
        set_users_manager_instance(users_manager)
        set_auth_manager_instance(auth_manager_instance)
        set_session_manager_instance(session_manager_instance)
        set_posts_manager_instance(posts_manager)
        set_messages_manager_instance(messages_manager)
        set_search_manager_instance(search_manager)
        set_availability_manager_instance(availability_manager)
        
        logger.info("Manager instances initialized")

        cleanup_task = asyncio.create_task(cleanup_sessions_task())
        logger.info("Session cleanup task started")
        
    except Exception as e:
        logger.error(f"Startup failed: {e}", exc_info=True)
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down GatorGuides API...")
    
    try:
        if cleanup_task:
            cleanup_task.cancel()
            try:
                await cleanup_task
            except asyncio.CancelledError:
                pass
        
        cleaner.stop()
        logger.info("Connection cleaner stopped")
        
        pool.close_all()
        logger.info("Connection pool closed")
        
    except Exception as e:
        logger.error(f"Shutdown error: {e}", exc_info=True)
    
    logger.info("Shutdown complete")

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

@app.get("/health")
async def health_check():
    conn = None
    cursor = None
    try:
        pool = ConnectionPool()
        conn = pool.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        
        return {
            "status": "healthy",
            "database": "connected",
            "auth_initialized": auth_manager_instance is not None,
            "session_manager_initialized": session_manager_instance is not None
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

app.include_router(search.router, prefix="/api")
app.include_router(sessions.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(tutors.router, prefix="/api")
app.include_router(messages.router, prefix="/api")
app.include_router(posts.router, prefix="/api")
app.include_router(uploads.router, prefix="/api")