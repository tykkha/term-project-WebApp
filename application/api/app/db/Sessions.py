import logging
from typing import Optional, List, Dict, Any
from db.Auth import ConnectionPool

logger = logging.getLogger(__name__)


class GatorGuidesSessions:
    def __init__(self):
        self.pool = ConnectionPool()
    
    def _get_connection(self):
        return self.pool.get_connection()
    
    def create_session(self, uid: int, tid: int, tags_id: int, day: str, time: int, location: str = 'Zoom') -> Optional[Dict[str, Any]]:
        conn = None
        cursor = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = """
                INSERT INTO Sessions (uid, tid, tagsID, day, time, location)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            
            cursor.execute(query, (uid, tid, tags_id, day, time, location))
            conn.commit()
            session_id = cursor.lastrowid
            
            # Fetch the created session
            cursor.execute("SELECT * FROM Sessions WHERE sid = %s", (session_id,))
            session = cursor.fetchone()
            
            if session:
                logger.info(f"Tutoring session created: {session_id}")
            return session
            
        except Exception as e:
            logger.error(f"Create session error: {e}", exc_info=True)
            if conn:
                conn.rollback()
            return None
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    def get_session_notification_info(self, session_id: int) -> Optional[Dict[str, Any]]:
        conn = None
        cursor = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT 
                    s.uid as student_uid,
                    s.tid,
                    s.day,
                    s.time,
                    u.firstName as student_first_name,
                    u.lastName as student_last_name,
                    tu.uid as tutor_uid,
                    tags.tags as course_name
                FROM Sessions s
                INNER JOIN User u ON s.uid = u.uid
                INNER JOIN Tutor t ON s.tid = t.tid
                INNER JOIN User tu ON t.uid = tu.uid
                INNER JOIN Tags tags ON s.tagsID = tags.tagsID
                WHERE s.sid = %s
            """
            
            cursor.execute(query, (session_id,))
            info = cursor.fetchone()
            
            return info
            
        except Exception as e:
            logger.error(f"Get session notification info error: {e}", exc_info=True)
            return None
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    def get_session(self, session_id: int) -> Optional[Dict[str, Any]]:
        conn = None
        cursor = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT 
                    s.*,
                    u.uid as student_uid, u.firstName as student_firstName, 
                    u.lastName as student_lastName, u.email as student_email,
                    t.tid, t.uid as tutor_uid, t.rating as tutor_rating,
                    tu.firstName as tutor_firstName, tu.lastName as tutor_lastName,
                    tu.email as tutor_email,
                    tag.tags as course_tag
                FROM Sessions s
                LEFT JOIN User u ON s.uid = u.uid
                LEFT JOIN Tutor t ON s.tid = t.tid
                LEFT JOIN User tu ON t.uid = tu.uid
                LEFT JOIN Tags tag ON s.tagsID = tag.tagsID
                WHERE s.sid = %s
            """
            
            cursor.execute(query, (session_id,))
            session = cursor.fetchone()
            
            return session
            
        except Exception as e:
            logger.error(f"Get session error: {e}", exc_info=True)
            return None
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    def start_session(self, session_id: int) -> bool:
        conn = None
        cursor = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            query = """
                UPDATE Sessions 
                SET started = NOW() 
                WHERE sid = %s AND started IS NULL
            """
            
            cursor.execute(query, (session_id,))
            conn.commit()
            rowcount = cursor.rowcount
            
            if rowcount > 0:
                logger.info(f"Session {session_id} started")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Start session error: {e}", exc_info=True)
            if conn:
                conn.rollback()
            return False
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    def end_session(self, session_id: int) -> bool:
        conn = None
        cursor = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            query = """
                UPDATE Sessions 
                SET concluded = NOW() 
                WHERE sid = %s AND started IS NOT NULL AND concluded IS NULL
            """
            
            cursor.execute(query, (session_id,))
            conn.commit()
            rowcount = cursor.rowcount
            
            if rowcount > 0:
                logger.info(f"Session {session_id} ended")
                return True
            return False
            
        except Exception as e:
            logger.error(f"End session error: {e}", exc_info=True)
            if conn:
                conn.rollback()
            return False
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def delete_session(self, session_id: int) -> bool:
        conn = None
        cursor = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            query = "DELETE FROM Sessions WHERE sid = %s"
            
            cursor.execute(query, (session_id,))
            conn.commit()
            rowcount = cursor.rowcount
            
            if rowcount > 0:
                logger.info(f"Session {session_id} deleted")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Delete session error: {e}", exc_info=True)
            if conn:
                conn.rollback()
            return False
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    def get_user_sessions(self, uid: int) -> List[Dict[str, Any]]:
        conn = None
        cursor = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT 
                    s.*,
                    t.tid, t.rating as tutor_rating,
                    tu.firstName as tutor_firstName, tu.lastName as tutor_lastName,
                    tag.tags as course_tag
                FROM Sessions s
                LEFT JOIN Tutor t ON s.tid = t.tid
                LEFT JOIN User tu ON t.uid = tu.uid
                LEFT JOIN Tags tag ON s.tagsID = tag.tagsID
                WHERE s.uid = %s
                ORDER BY s.sid DESC
            """
            
            cursor.execute(query, (uid,))
            sessions = cursor.fetchall()
            
            result = []
            for session in sessions:
                result.append({
                    'sid': session['sid'],
                    'uid': session['uid'],
                    'tid': session['tid'],
                    'tagsID': session['tagsID'],
                    'day': session['day'],
                    'time': session['time'],
                    'location': session.get('location', 'Zoom'),
                    'started': session.get('started'),
                    'concluded': session.get('concluded'),
                    'course': session.get('course_tag', 'Unknown'),
                    'tutor': {
                        'tid': session['tid'],
                        'name': f"{session.get('tutor_firstName', '')} {session.get('tutor_lastName', '')}".strip() or 'Unknown Tutor',
                        'rating': session.get('tutor_rating', 0.0)
                    }
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Get user sessions error: {e}", exc_info=True)
            return []
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def get_tutor_sessions(self, tid: int) -> List[Dict[str, Any]]:
        conn = None
        cursor = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT 
                    s.*,
                    u.firstName as student_firstName, u.lastName as student_lastName,
                    u.email as student_email,
                    tag.tags as course_tag
                FROM Sessions s
                LEFT JOIN User u ON s.uid = u.uid
                LEFT JOIN Tags tag ON s.tagsID = tag.tagsID
                WHERE s.tid = %s
                ORDER BY s.sid DESC
            """
            
            cursor.execute(query, (tid,))
            sessions = cursor.fetchall()
            
            result = []
            for session in sessions:
                result.append({
                    'sid': session['sid'],
                    'uid': session['uid'],
                    'tid': session['tid'],
                    'tagsID': session['tagsID'],
                    'day': session['day'],
                    'time': session['time'],
                    'location': session.get('location', 'Zoom'),
                    'started': session.get('started'),
                    'concluded': session.get('concluded'),
                    'course': session.get('course_tag', 'Unknown'),
                    'student': {
                        'uid': session['uid'],
                        'name': f"{session.get('student_firstName', '')} {session.get('student_lastName', '')}".strip() or 'Unknown Student',
                        'email': session.get('student_email', '')
                    }
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Get tutor sessions error: {e}", exc_info=True)
            return []
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()