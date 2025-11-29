import mysql.connector
from typing import Optional, Dict, Any, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class GatorGuidesPosts:
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
                pool_name='posts_pool',
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

    def create_post(self, tid: int, tags_id: int, content: str) -> Optional[Dict[str, Any]]:
        if not self._ensure_connection():
            logger.error("Create post failed: database connection unavailable")
            return None

        try:
            tutor_check = "SELECT tid FROM Tutor WHERE tid = %s"
            self.cursor.execute(tutor_check, (tid,))
            if not self.cursor.fetchone():
                logger.error(f"Tutor {tid} does not exist")
                return None

            tag_check = "SELECT tagsID FROM Tags WHERE tagsID = %s"
            self.cursor.execute(tag_check, (tags_id,))
            if not self.cursor.fetchone():
                logger.error(f"Tag {tags_id} does not exist")
                return None

            query = """
                INSERT INTO Posts (tid, tagsID, content, timestamp)
                VALUES (%s, %s, %s, NOW())
            """
            
            self.cursor.execute(query, (tid, tags_id, content))
            post_id = self.cursor.lastrowid

            return self.get_post(post_id)

        except Exception as e:
            logger.error(f"Create post error: {e}", exc_info=True)
            return None

    # Fetches post by post ID
    def get_post(self, pid: int) -> Optional[Dict[str, Any]]:
        if not self._ensure_connection():
            logger.error("Get post failed: database connection unavailable")
            return None

        try:
            query = """
                SELECT 
                    p.pid, p.tid, p.tagsID, p.content, p.timestamp,
                    u.firstName, u.lastName,
                    t.rating,
                    tg.tags as course
                FROM Posts p
                INNER JOIN Tutor t ON p.tid = t.tid
                INNER JOIN User u ON t.uid = u.uid
                INNER JOIN Tags tg ON p.tagsID = tg.tagsID
                WHERE p.pid = %s
            """
            
            self.cursor.execute(query, (pid,))
            post = self.cursor.fetchone()

            if post:
                return {
                    'pid': post['pid'],
                    'tid': post['tid'],
                    'tutorName': f"{post['firstName']} {post['lastName']}",
                    'rating': post['rating'],
                    'course': post['course'],
                    'tagsID': post['tagsID'],
                    'content': post['content'],
                    'timestamp': post['timestamp'].isoformat() if isinstance(post['timestamp'], datetime) else str(post['timestamp'])
                }
            
            return None

        except Exception as e:
            logger.error(f"Get post error: {e}", exc_info=True)
            return None
    
    # Fetches tutor ID from post ID
    def get_tutor_id_from_post(self, pid: int) -> Optional[int]:
        if not self._ensure_connection():
            logger.error("Get tutor from post failed: database connection unavailable")
            return None

        try:
            query = "SELECT tid FROM Posts WHERE pid = %s"
            self.cursor.execute(query, (pid,))
            result = self.cursor.fetchone()
            
            return result['tid'] if result else None

        except Exception as e:
            logger.error(f"Get tutor from post error: {e}", exc_info=True)
            return None
        
    # Return all posts made by a specific tutor (think profile/post manager)
    def get_posts_by_tutor(self, tid: int, limit: int = 50) -> List[Dict[str, Any]]:
        if not self._ensure_connection():
            logger.error("Get tutor posts failed: database connection unavailable")
            return []

        try:
            query = """
                SELECT 
                    p.pid, p.tid, p.tagsID, p.content, p.timestamp,
                    tg.tags as course
                FROM Posts p
                INNER JOIN Tags tg ON p.tagsID = tg.tagsID
                WHERE p.tid = %s
                ORDER BY p.timestamp DESC
                LIMIT %s
            """
            
            self.cursor.execute(query, (tid, limit))
            posts = self.cursor.fetchall()

            results = []
            for post in posts:
                results.append({
                    'pid': post['pid'],
                    'tid': post['tid'],
                    'course': post['course'],
                    'tagsID': post['tagsID'],
                    'content': post['content'],
                    'timestamp': post['timestamp'].isoformat() if isinstance(post['timestamp'], datetime) else str(post['timestamp'])
                })

            return results

        except Exception as e:
            logger.error(f"Get tutor posts error: {e}", exc_info=True)
            return []

    # Update post content or tag
    def update_post(self, pid: int, content: Optional[str] = None, tags_id: Optional[int] = None) -> bool:
        if not self._ensure_connection():
            logger.error("Update post failed: database connection unavailable")
            return False

        try:
            updates = []
            values = []

            if content is not None:
                updates.append("content = %s")
                values.append(content)
            
            if tags_id is not None:
                tag_check = "SELECT tagsID FROM Tags WHERE tagsID = %s"
                self.cursor.execute(tag_check, (tags_id,))
                if not self.cursor.fetchone():
                    logger.error(f"Tag {tags_id} does not exist")
                    return False
                
                updates.append("tagsID = %s")
                values.append(tags_id)

            if not updates:
                logger.warning("No fields to update")
                return False

            values.append(pid)
            query = f"UPDATE Posts SET {', '.join(updates)} WHERE pid = %s"
            
            self.cursor.execute(query, tuple(values))
            return self.cursor.rowcount > 0

        except Exception as e:
            logger.error(f"Update post error: {e}", exc_info=True)
            return False
        
    # Deletes post by ID from db
    def delete_post(self, pid: int) -> bool:
        if not self._ensure_connection():
            logger.error("Delete post failed: database connection unavailable")
            return False

        try:
            query = "DELETE FROM Posts WHERE pid = %s"
            self.cursor.execute(query, (pid,))
            return self.cursor.rowcount > 0

        except Exception as e:
            logger.error(f"Delete post error: {e}", exc_info=True)
            return False

    def close(self):
        try:
            if self.cursor:
                self.cursor.close()
            if self.connection and self.connection.is_connected():
                self.connection.close()
        except Exception as e:
            logger.error(f"Error closing connection: {e}")