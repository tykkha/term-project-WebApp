import mysql.connector
from mysql.connector import pooling
from typing import Optional
from datetime import datetime, timedelta
import secrets
import logging
import threading

logger = logging.getLogger(__name__)

class ConnectionPool:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def initialize(self, host: str, database: str, user: str, password: str, pool_size: int = 10, pool_name: str = "gatorguides_pool"):
        if self._initialized:
            logger.warning("Connection pool already initialized")
            return
        
        try:
            host_parts = host.split(':')
            db_host = host_parts[0]
            db_port = int(host_parts[1]) if len(host_parts) > 1 else 3306
            
            self.pool = pooling.MySQLConnectionPool(
                pool_name=pool_name,
                pool_size=pool_size,
                pool_reset_session=True,
                host=db_host,
                port=db_port,
                database=database,
                user=user,
                password=password,
                autocommit=True
            )
            self._initialized = True
            logger.info(f"Connection pool initialized")
        except Exception as e:
            logger.error(f"Failed to initialize connection pool")
            raise
    
    def get_connection(self):
        if not self._initialized:
            raise RuntimeError("Connection pool not initialized")
        try:
            return self.pool.get_connection()
        except Exception as e:
            logger.error(f"Failed to get connection from pool")
            raise
    
    def close_all(self):
        if hasattr(self, 'pool'):
            try:
                logger.info("Closing all pool connections")
                del self.pool
                self._initialized = False
            except Exception as e:
                logger.error(f"Error closing pool")


class ConnectionCleaner:
    
    def __init__(self, check_interval: int = 300):
        self.check_interval = check_interval
        self._stop_event = threading.Event()
        self._thread = None
    
    def start(self):
        if self._thread and self._thread.is_alive():
            logger.warning("Cleanup thread already running")
            return
        
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self._thread.start()
        logger.info(f"Connection cleanup thread started")
    
    def stop(self):
        if self._thread and self._thread.is_alive():
            logger.info("Stopping cleanup thread")
            self._stop_event.set()
            self._thread.join(timeout=5)
    
    def _cleanup_loop(self):
        while not self._stop_event.is_set():
            try:
                self._perform_cleanup()
            except Exception as e:
                logger.error(f"Error in cleanup loop")
    
            self._stop_event.wait(self.check_interval)
    
    def _perform_cleanup(self):
        pool = ConnectionPool()
        
        try:
            conn = pool.get_connection()
            cursor = conn.cursor()
            query = """
                SELECT CONCAT('KILL ', id, ';') as kill_cmd
                FROM information_schema.processlist
                WHERE command = 'Sleep'
                AND time > 3600
                AND user = USER()
            """
            
            cursor.execute(query)
            idle_connections = cursor.fetchall()
            
            killed_count = 0
            for (kill_cmd,) in idle_connections:
                try:
                    cursor.execute(kill_cmd)
                    killed_count += 1
                except Exception as e:
                    logger.warning(f"Failed to kill connection")
            
            if killed_count > 0:
                logger.info(f"Killed idle connections")
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            logger.error(f"Cleanup operation failed")

class GatorGuidesAuth:
    def __init__(self):
        self.pool = ConnectionPool()
    
    def _get_connection(self):
        return self.pool.get_connection()
        
    # Create a new session
    def create_session(self, uid: int, duration_hours: int = 24) -> Optional[str]:
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)
            
            session_id = secrets.token_urlsafe(32)
            expires_at = datetime.now() + timedelta(hours=duration_hours)
            
            query = """
                INSERT INTO LoginSessions (sessionID, uid, expiresAt)
                VALUES (%s, %s, %s)
            """
            
            cursor.execute(query, (session_id, uid, expires_at))
            cursor.close()
            logger.info(f"Session created for user {uid}")
            return session_id
            
        except Exception as e:
            logger.error(f"Create session error: {e}", exc_info=True)
            return None
        finally:
            if conn:
                conn.close()

    # Validate session and return user ID if true
    def validate_session(self, session_id: str) -> Optional[int]:
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT uid, expiresAt
                FROM LoginSessions
                WHERE sessionID = %s
            """
            
            cursor.execute(query, (session_id,))
            session = cursor.fetchone()
            cursor.close()
            
            if not session:
                return None
            
            if session['expiresAt'] < datetime.now():
                self.delete_session(session_id)
                return None
            
            return session['uid']
            
        except Exception as e:
            logger.error(f"Validate session error: {e}", exc_info=True)
            return None
        finally:
            if conn:
                conn.close()
        
    # Delete a specific session
    def delete_session(self, session_id: str) -> bool:
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            query = "DELETE FROM LoginSessions WHERE sessionID = %s"
            cursor.execute(query, (session_id,))
            rowcount = cursor.rowcount
            cursor.close()
            return rowcount > 0
            
        except Exception as e:
            logger.error(f"Delete session error: {e}", exc_info=True)
            return False
        finally:
            if conn:
                conn.close()
        
    # Logout from all devices
    def delete_user_sessions(self, uid: int) -> bool:
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            query = "DELETE FROM LoginSessions WHERE uid = %s"
            cursor.execute(query, (uid,))
            cursor.close()
            return True
            
        except Exception as e:
            logger.error(f"Delete user sessions error: {e}", exc_info=True)
            return False
        finally:
            if conn:
                conn.close()
        
    # Remove old sessions
    def cleanup_expired_sessions(self) -> int:
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            query = "DELETE FROM LoginSessions WHERE expiresAt < NOW()"
            cursor.execute(query)
            count = cursor.rowcount
            cursor.close()
            logger.info(f"Cleaned up expired sessions")
            return count
            
        except Exception as e:
            logger.error(f"Cleanup error: {e}", exc_info=True)
            return 0
        finally:
            if conn:
                conn.close()