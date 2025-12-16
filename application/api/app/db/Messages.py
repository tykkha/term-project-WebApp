from typing import Optional, Dict, Any, List
from datetime import datetime
import logging
from db.Auth import ConnectionPool

logger = logging.getLogger(__name__)


class GatorGuidesMessages:
    def __init__(self):
        self.pool = ConnectionPool()
    
    def _get_connection(self):
        return self.pool.get_connection()

    def can_message(self, sender_uid: int, receiver_uid: int) -> bool:
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT COUNT(*) as session_count
                FROM Sessions s
                WHERE 
                    (s.uid = %s AND s.tid IN (SELECT tid FROM Tutor WHERE uid = %s))
                    OR 
                    (s.uid = %s AND s.tid IN (SELECT tid FROM Tutor WHERE uid = %s))
            """
            
            cursor.execute(query, (sender_uid, receiver_uid, receiver_uid, sender_uid))
            result = cursor.fetchone()
            cursor.close()
            
            return result['session_count'] > 0

        except Exception as e:
            logger.error(f"Can message check error: {e}", exc_info=True)
            return False
        finally:
            if conn:
                conn.close()

    def send_message(self, sender_uid: int, receiver_uid: int, content: str) -> Optional[Dict[str, Any]]:
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)
            
            # Insert message
            query = """
                INSERT INTO Messages (senderUID, receiverUID, content, timestamp)
                VALUES (%s, %s, %s, NOW())
            """
            
            cursor.execute(query, (sender_uid, receiver_uid, content))
            message_id = cursor.lastrowid
            
            conn.commit()

            # Get the created message with sender info
            select_query = """
                SELECT 
                    m.mid, m.senderUID, m.receiverUID, m.content, m.timestamp,
                    u.firstName as sender_first_name,
                    u.lastName as sender_last_name
                FROM Messages m
                INNER JOIN User u ON m.senderUID = u.uid
                WHERE m.mid = %s
            """
            
            cursor.execute(select_query, (message_id,))
            message = cursor.fetchone()
            cursor.close()
            
            if message:
                return {
                    'mid': message['mid'],
                    'senderUID': message['senderUID'],
                    'receiverUID': message['receiverUID'],
                    'senderName': f"{message['sender_first_name']} {message['sender_last_name']}",
                    'content': message['content'],
                    'timestamp': message['timestamp'].isoformat() if isinstance(message['timestamp'], datetime) else str(message['timestamp'])
                }
            
            return None

        except Exception as e:
            logger.error(f"Send message error: {e}", exc_info=True)
            if conn:
                conn.rollback()
            return None
        finally:
            if conn:
                conn.close()

    def get_conversation(self, uid1: int, uid2: int, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT 
                    m.mid, m.senderUID, m.receiverUID, m.content, m.timestamp,
                    u.firstName as sender_first_name,
                    u.lastName as sender_last_name
                FROM Messages m
                INNER JOIN User u ON m.senderUID = u.uid
                WHERE 
                    (m.senderUID = %s AND m.receiverUID = %s)
                    OR 
                    (m.senderUID = %s AND m.receiverUID = %s)
                ORDER BY m.timestamp DESC
                LIMIT %s OFFSET %s
            """
            
            cursor.execute(query, (uid1, uid2, uid2, uid1, limit, offset))
            messages = cursor.fetchall()
            cursor.close()
            
            results = []
            for msg in messages:
                results.append({
                    'mid': msg['mid'],
                    'senderUID': msg['senderUID'],
                    'receiverUID': msg['receiverUID'],
                    'senderName': f"{msg['sender_first_name']} {msg['sender_last_name']}",
                    'content': msg['content'],
                    'timestamp': msg['timestamp'].isoformat() if isinstance(msg['timestamp'], datetime) else str(msg['timestamp'])
                })
            
            return list(reversed(results))

        except Exception as e:
            logger.error(f"Get conversation error: {e}", exc_info=True)
            return []
        finally:
            if conn:
                conn.close()

    def get_recent_conversations(self, uid: int, limit: int = 10) -> List[Dict[str, Any]]:
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT 
                    CASE 
                        WHEN m.senderUID = %s THEN m.receiverUID
                        ELSE m.senderUID
                    END as other_uid,
                    u.firstName,
                    u.lastName,
                    MAX(m.timestamp) as last_message_time,
                    (SELECT content 
                     FROM Messages m2 
                     WHERE (m2.senderUID = %s AND m2.receiverUID = other_uid)
                        OR (m2.receiverUID = %s AND m2.senderUID = other_uid)
                     ORDER BY m2.timestamp DESC 
                     LIMIT 1) as last_message
                FROM Messages m
                INNER JOIN User u ON u.uid = CASE 
                    WHEN m.senderUID = %s THEN m.receiverUID
                    ELSE m.senderUID
                END
                WHERE m.senderUID = %s OR m.receiverUID = %s
                GROUP BY other_uid, u.firstName, u.lastName
                ORDER BY last_message_time DESC
                LIMIT %s
            """
            
            cursor.execute(query, (uid, uid, uid, uid, uid, uid, limit))
            conversations = cursor.fetchall()
            cursor.close()
            
            results = []
            for conv in conversations:
                results.append({
                    'otherUID': conv['other_uid'],
                    'otherName': f"{conv['firstName']} {conv['lastName']}",
                    'lastMessage': conv['last_message'],
                    'lastMessageTime': conv['last_message_time'].isoformat() if isinstance(conv['last_message_time'], datetime) else str(conv['last_message_time'])
                })
            
            return results

        except Exception as e:
            logger.error(f"Get recent conversations error: {e}", exc_info=True)
            return []
        finally:
            if conn:
                conn.close()