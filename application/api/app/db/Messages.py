import mysql.connector
from typing import Optional, Dict, Any, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class GatorGuidesMessages:
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
                pool_name='messages_pool',
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

    # Check if two users can message each other (session was scheduled)
    def can_message(self, sender_uid: int, receiver_uid: int) -> bool:
        if not self._ensure_connection():
            logger.error("Can message check failed: database connection unavailable")
            return False

        try:
            query = """
                SELECT COUNT(*) as session_count
                FROM Sessions s
                WHERE 
                    (s.uid = %s AND s.tid IN (SELECT tid FROM Tutor WHERE uid = %s))
                    OR 
                    (s.uid = %s AND s.tid IN (SELECT tid FROM Tutor WHERE uid = %s))
            """
            
            self.cursor.execute(query, (sender_uid, receiver_uid, receiver_uid, sender_uid))
            result = self.cursor.fetchone()
            
            return result['session_count'] > 0

        except Exception as e:
            logger.error(f"Can message check error: {e}", exc_info=True)
            return False

    # Stores message in database to be retrieved in user conversations
    def send_message(self, sender_uid: int, receiver_uid: int, content: str) -> Optional[Dict[str, Any]]:
        if not self._ensure_connection():
            logger.error("Send message failed: database connection unavailable")
            return None

        try:
            # Insert message
            query = """
                INSERT INTO Messages (senderUID, receiverUID, content, timestamp)
                VALUES (%s, %s, %s, NOW())
            """
            
            self.cursor.execute(query, (sender_uid, receiver_uid, content))
            message_id = self.cursor.lastrowid

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
            
            self.cursor.execute(select_query, (message_id,))
            message = self.cursor.fetchone()
            
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
            return None

    # Pulls up full conversation between tutor and user
    def get_conversation(self, uid1: int, uid2: int, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        if not self._ensure_connection():
            logger.error("Get conversation failed: database connection unavailable")
            return []

        try:
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
            
            self.cursor.execute(query, (uid1, uid2, uid2, uid1, limit, offset))
            messages = self.cursor.fetchall()
            
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
            
            # Reverse to show oldest first (most recent at bottom)
            return list(reversed(results))

        except Exception as e:
            logger.error(f"Get conversation error: {e}", exc_info=True)
            return []

    # Get message history for recent conversations
    def get_recent_conversations(self, uid: int, limit: int = 10) -> List[Dict[str, Any]]:
        if not self._ensure_connection():
            logger.error("Get recent conversations failed: database connection unavailable")
            return []

        try:
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
            
            self.cursor.execute(query, (uid, uid, uid, uid, uid, uid, limit))
            conversations = self.cursor.fetchall()
            
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

    def close(self):
        try:
            if self.cursor:
                self.cursor.close()
            if self.connection and self.connection.is_connected():
                self.connection.close()
        except Exception as e:
            logger.error(f"Error closing connection: {e}")