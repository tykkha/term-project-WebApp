from typing import Optional, Dict, Any, List
from datetime import datetime
import logging
from db.Auth import ConnectionPool

logger = logging.getLogger(__name__)


class GatorGuidesPosts:
    def __init__(self):
        self.pool = ConnectionPool()
    
    def _get_connection(self):
        return self.pool.get_connection()

    def create_post(self, tid: int, tags_id: int, content: str) -> Optional[Dict[str, Any]]:
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)
            
            tutor_check = "SELECT tid FROM Tutor WHERE tid = %s"
            cursor.execute(tutor_check, (tid,))
            if not cursor.fetchone():
                logger.error(f"Tutor {tid} does not exist")
                cursor.close()
                return None

            tag_check = "SELECT tagsID FROM Tags WHERE tagsID = %s"
            cursor.execute(tag_check, (tags_id,))
            if not cursor.fetchone():
                logger.error(f"Tag {tags_id} does not exist")
                cursor.close()
                return None

            query = """
                INSERT INTO Posts (tid, tagsID, content, timestamp)
                VALUES (%s, %s, %s, NOW())
            """
            
            cursor.execute(query, (tid, tags_id, content))
            conn.commit()
            post_id = cursor.lastrowid
            cursor.close()

            return self.get_post(post_id)

        except Exception as e:
            logger.error(f"Create post error: {e}", exc_info=True)
            if conn:
                conn.rollback()
            return None

        finally:
            if conn:
                conn.close()

    def get_post(self, pid: int) -> Optional[Dict[str, Any]]:
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)
            
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
            
            cursor.execute(query, (pid,))
            post = cursor.fetchone()
            cursor.close()

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
        finally:
            if conn:
                conn.close()
    
    def get_tutor_id_from_post(self, pid: int) -> Optional[int]:
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = "SELECT tid FROM Posts WHERE pid = %s"
            cursor.execute(query, (pid,))
            result = cursor.fetchone()
            cursor.close()
            
            return result['tid'] if result else None

        except Exception as e:
            logger.error(f"Get tutor from post error: {e}", exc_info=True)
            return None
        finally:
            if conn:
                conn.close()
        
    def get_posts_by_tutor(self, tid: int, limit: int = 50) -> List[Dict[str, Any]]:
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)
            
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
            
            cursor.execute(query, (tid, limit))
            posts = cursor.fetchall()
            cursor.close()

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
        finally:
            if conn:
                conn.close()

    def update_post(self, pid: int, content: Optional[str] = None, tags_id: Optional[int] = None) -> bool:
        conn = None
        try:
            updates = []
            values = []

            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)

            if content is not None:
                updates.append("content = %s")
                values.append(content)
            
            if tags_id is not None:
                tag_check = "SELECT tagsID FROM Tags WHERE tagsID = %s"
                cursor.execute(tag_check, (tags_id,))
                if not cursor.fetchone():
                    logger.error(f"Tag {tags_id} does not exist")
                    cursor.close()
                    return False
                
                updates.append("tagsID = %s")
                values.append(tags_id)

            if not updates:
                logger.warning("No fields to update")
                cursor.close()
                return False

            values.append(pid)
            query = f"UPDATE Posts SET {', '.join(updates)} WHERE pid = %s"
            
            cursor.execute(query, tuple(values))
            conn.commit()
            rowcount = cursor.rowcount
            cursor.close()
            
            return rowcount > 0

        except Exception as e:
            logger.error(f"Update post error: {e}", exc_info=True)
            if conn:
                conn.rollback()
            return False
        
        finally:
            if conn:
                conn.close()
        
    def delete_post(self, pid: int) -> bool:
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            query = "DELETE FROM Posts WHERE pid = %s"
            cursor.execute(query, (pid,))
            conn.commit()
            rowcount = cursor.rowcount
            cursor.close()
            
            return rowcount > 0

        except Exception as e:
            logger.error(f"Delete post error: {e}", exc_info=True)
            if conn:
                conn.rollback()
            return False
        
        finally:
            if conn:
                conn.close()