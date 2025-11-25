import mysql.connector
from typing import Optional, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class GatorGuidesSessions:
    def __init__(self, host: str, database: str, user: str, password: str):
        try:
            host_parts = host.split(':')
            db_host = host_parts[0]
            db_port = int(host_parts[1]) if len(host_parts) > 1 else 3663

            self.connection = mysql.connector.connect(
                host=db_host,
                port=db_port,
                database=database,
                user=user,
                password=password,
                autocommit=True,
                pool_name='sessions_pool',
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

    def create_session(
        self,
        uid: int,
        tid: int,
        tags_id: int,
        day: str,
        time: int
    ) -> Optional[Dict[str, Any]]:
        if not self._ensure_connection():
            logger.error("Create session failed: database connection unavailable")
            return None

        # Validate inputs
        valid_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        if day not in valid_days:
            logger.error(f"Invalid day: {day}")
            return None

        if not (0 <= time <= 23):
            logger.error(f"Invalid time: {time}. Must be 0-23")
            return None

        try:
            query = """
                INSERT INTO Sessions (uid, tid, tagsID, day, time, started, concluded)
                VALUES (%s, %s, %s, %s, %s, NULL, NULL)
            """
            
            self.cursor.execute(query, (uid, tid, tags_id, day, time))
            session_id = self.cursor.lastrowid

            # Fetch the created session
            select_query = """
                SELECT 
                    s.sid, s.uid, s.tid, s.tagsID, s.day, s.time,
                    s.started, s.concluded,
                    u.firstName as student_first_name,
                    u.lastName as student_last_name,
                    tu.firstName as tutor_first_name,
                    tu.lastName as tutor_last_name,
                    tg.tags as course
                FROM Sessions s
                INNER JOIN User u ON s.uid = u.uid
                INNER JOIN Tutor t ON s.tid = t.tid
                INNER JOIN User tu ON t.uid = tu.uid
                INNER JOIN Tags tg ON s.tagsID = tg.tagsID
                WHERE s.sid = %s
            """
            
            self.cursor.execute(select_query, (session_id,))
            session = self.cursor.fetchone()
            
            if session:
                return {
                    'sid': session['sid'],
                    'student': {
                        'uid': session['uid'],
                        'name': f"{session['student_first_name']} {session['student_last_name']}"
                    },
                    'tutor': {
                        'tid': session['tid'],
                        'name': f"{session['tutor_first_name']} {session['tutor_last_name']}"
                    },
                    'course': session['course'],
                    'day': session['day'],
                    'time': session['time'],
                    'started': session['started'],
                    'concluded': session['concluded']
                }
            
            return None

        except Exception as e:
            logger.error(f"Create session error: {e}", exc_info=True)
            return None

    def start_session(self, session_id: int) -> bool:
        if not self._ensure_connection():
            logger.error("Start session failed: database connection unavailable")
            return False

        try:
            query = """
                UPDATE Sessions
                SET started = NOW()
                WHERE sid = %s AND started IS NULL
            """
            
            self.cursor.execute(query, (session_id,))
            return self.cursor.rowcount > 0

        except Exception as e:
            logger.error(f"Start session error: {e}", exc_info=True)
            return False

    def end_session(self, session_id: int) -> bool:
        if not self._ensure_connection():
            logger.error("End session failed: database connection unavailable")
            return False

        try:
            query = """
                UPDATE Sessions
                SET concluded = NOW()
                WHERE sid = %s AND concluded IS NULL
            """
            
            self.cursor.execute(query, (session_id,))
            return self.cursor.rowcount > 0

        except Exception as e:
            logger.error(f"End session error: {e}", exc_info=True)
            return False

    def get_session(self, session_id: int) -> Optional[Dict[str, Any]]:
        if not self._ensure_connection():
            logger.error("Get session failed: database connection unavailable")
            return None

        try:
            query = """
                SELECT 
                    s.sid, s.uid, s.tid, s.tagsID, s.day, s.time,
                    s.started, s.concluded,
                    u.firstName as student_first_name,
                    u.lastName as student_last_name,
                    tu.firstName as tutor_first_name,
                    tu.lastName as tutor_last_name,
                    tg.tags as course
                FROM Sessions s
                INNER JOIN User u ON s.uid = u.uid
                INNER JOIN Tutor t ON s.tid = t.tid
                INNER JOIN User tu ON t.uid = tu.uid
                INNER JOIN Tags tg ON s.tagsID = tg.tagsID
                WHERE s.sid = %s
            """
            
            self.cursor.execute(query, (session_id,))
            session = self.cursor.fetchone()
            
            if session:
                return {
                    'sid': session['sid'],
                    'student': {
                        'uid': session['uid'],
                        'name': f"{session['student_first_name']} {session['student_last_name']}"
                    },
                    'tutor': {
                        'tid': session['tid'],
                        'name': f"{session['tutor_first_name']} {session['tutor_last_name']}"
                    },
                    'course': session['course'],
                    'day': session['day'],
                    'time': session['time'],
                    'started': session['started'],
                    'concluded': session['concluded']
                }
            
            return None

        except Exception as e:
            logger.error(f"Get session error: {e}", exc_info=True)
            return None

    def get_user_sessions(self, uid: int) -> list:
        if not self._ensure_connection():
            logger.error("Get user sessions failed: database connection unavailable")
            return []

        try:
            query = """
                SELECT 
                    s.sid, s.uid, s.tid, s.tagsID, s.day, s.time,
                    s.started, s.concluded,
                    tu.firstName as tutor_first_name,
                    tu.lastName as tutor_last_name,
                    tg.tags as course
                FROM Sessions s
                INNER JOIN Tutor t ON s.tid = t.tid
                INNER JOIN User tu ON t.uid = tu.uid
                INNER JOIN Tags tg ON s.tagsID = tg.tagsID
                WHERE s.uid = %s
                ORDER BY s.sid DESC
            """
            
            self.cursor.execute(query, (uid,))
            sessions = self.cursor.fetchall()
            
            results = []
            for session in sessions:
                results.append({
                    'sid': session['sid'],
                    'tutor': {
                        'tid': session['tid'],
                        'name': f"{session['tutor_first_name']} {session['tutor_last_name']}"
                    },
                    'course': session['course'],
                    'day': session['day'],
                    'time': session['time'],
                    'started': session['started'],
                    'concluded': session['concluded']
                })
            
            return results

        except Exception as e:
            logger.error(f"Get user sessions error: {e}", exc_info=True)
            return []

    def get_tutor_sessions(self, tid: int) -> list:
        if not self._ensure_connection():
            logger.error("Get tutor sessions failed: database connection unavailable")
            return []

        try:
            query = """
                SELECT 
                    s.sid, s.uid, s.tid, s.tagsID, s.day, s.time,
                    s.started, s.concluded,
                    u.firstName as student_first_name,
                    u.lastName as student_last_name,
                    tg.tags as course
                FROM Sessions s
                INNER JOIN User u ON s.uid = u.uid
                INNER JOIN Tags tg ON s.tagsID = tg.tagsID
                WHERE s.tid = %s
                ORDER BY s.sid DESC
            """
            
            self.cursor.execute(query, (tid,))
            sessions = self.cursor.fetchall()
            
            results = []
            for session in sessions:
                results.append({
                    'sid': session['sid'],
                    'student': {
                        'uid': session['uid'],
                        'name': f"{session['student_first_name']} {session['student_last_name']}"
                    },
                    'course': session['course'],
                    'day': session['day'],
                    'time': session['time'],
                    'started': session['started'],
                    'concluded': session['concluded']
                })
            
            return results

        except Exception as e:
            logger.error(f"Get tutor sessions error: {e}", exc_info=True)
            return []

    def close(self):
        try:
            if self.cursor:
                self.cursor.close()
            if self.connection and self.connection.is_connected():
                self.connection.close()
        except Exception as e:
            logger.error(f"Error closing connection: {e}")