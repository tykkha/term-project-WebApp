import mysql.connector
from typing import Optional
from datetime import datetime, timedelta
import secrets
import logging

logger = logging.getLogger(__name__)


class GatorGuidesAuth:
    def __init__(self, host: str, database: str, user: str, password: str):
        try:
            host_parts = host.split(':')
            db_host = host_parts[0]
            db_port = int(host_parts[1]) if len(host_parts) > 1 else 3306

            self.connection = mysql.connector.connect(
                host=db_host,
                port=db_port,
                database=database,
                user=user,
                password=password,
                autocommit=True,
                pool_name='auth_pool',
                pool_size=10
            )
            self.cursor = self.connection.cursor(dictionary=True)
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            self.connection = None
            self.cursor = None

    def _ensure_connection(self):
        try:
            if self.connection and self.connection.is_connected():
                return True
            self.connection.reconnect(attempts=3, delay=1)
            self.cursor = self.connection.cursor(dictionary=True)
            return True
        except Exception as e:
            logger.error(f"Reconnection failed: {e}")
            self.connection = None
            self.cursor = None
            return False
        
    # Create a new session
    def create_session(self, uid: int, duration_hours: int = 24) -> Optional[str]:
        if not self._ensure_connection():
            logger.error("Create session failed: database connection unavailable")
            return None

        try:
            # Generate secure random session ID
            session_id = secrets.token_urlsafe(32)
            expires_at = datetime.now() + timedelta(hours=duration_hours)

            query = """
                INSERT INTO LoginSessions (sessionID, uid, expiresAt)
                VALUES (%s, %s, %s)
            """
            
            self.cursor.execute(query, (session_id, uid, expires_at))
            logger.info(f"Session created for user {uid}")
            return session_id

        except Exception as e:
            logger.error(f"Create session error: {e}", exc_info=True)
            return None

    # Validate session and return user ID if true
    def validate_session(self, session_id: str) -> Optional[int]:
        if not self._ensure_connection():
            logger.error("Validate session failed: database connection unavailable")
            return None

        try:
            query = """
                SELECT uid, expiresAt
                FROM LoginSessions
                WHERE sessionID = %s
            """
            
            self.cursor.execute(query, (session_id,))
            session = self.cursor.fetchone()

            if not session:
                return None

            # Check if expired
            if session['expiresAt'] < datetime.now():
                # Delete expired session
                self.delete_session(session_id)
                return None

            return session['uid']

        except Exception as e:
            logger.error(f"Validate session error: {e}", exc_info=True)
            return None
        
    # Delete a specific session
    def delete_session(self, session_id: str) -> bool:
        if not self._ensure_connection():
            logger.error("Delete session failed: database connection unavailable")
            return False

        try:
            query = "DELETE FROM LoginSessions WHERE sessionID = %s"
            self.cursor.execute(query, (session_id,))
            return self.cursor.rowcount > 0

        except Exception as e:
            logger.error(f"Delete session error: {e}", exc_info=True)
            return False
        
    # Logout from all devices
    def delete_user_sessions(self, uid: int) -> bool:
        if not self._ensure_connection():
            logger.error("Delete user sessions failed: database connection unavailable")
            return False

        try:
            query = "DELETE FROM LoginSessions WHERE uid = %s"
            self.cursor.execute(query, (uid,))
            return True

        except Exception as e:
            logger.error(f"Delete user sessions error: {e}", exc_info=True)
            return False
        
    # Remove old sessions
    def cleanup_expired_sessions(self) -> int:
        if not self._ensure_connection():
            logger.error("Cleanup failed: database connection unavailable")
            return 0

        try:
            query = "DELETE FROM LoginSessions WHERE expiresAt < NOW()"
            self.cursor.execute(query)
            count = self.cursor.rowcount
            logger.info(f"Cleaned up {count} expired sessions")
            return count

        except Exception as e:
            logger.error(f"Cleanup error: {e}", exc_info=True)
            return 0

    def close(self):
        try:
            if self.cursor:
                self.cursor.close()
            if self.connection and self.connection.is_connected():
                self.connection.close()
        except Exception as e:
            logger.error(f"Error closing connection: {e}")