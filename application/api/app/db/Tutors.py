import mysql.connector
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class GatorGuidesTutors:
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
                pool_name='tutors_pool',
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

    def update_tutor_rating(self, tid: int) -> bool:
        try:
            avg_query = """
                SELECT AVG(rating) as avg_rating, COUNT(*) as rating_count
                FROM Ratings
                WHERE tid = %s
            """
            self.cursor.execute(avg_query, (tid,))
            result = self.cursor.fetchone()
            
            if result and result['rating_count'] > 0:
                avg_rating = round(result['avg_rating'], 2)
                update_query = "UPDATE Tutor SET rating = %s WHERE tid = %s"
                self.cursor.execute(update_query, (avg_rating, tid))
                logger.info(f"Updated tutor {tid} rating to {avg_rating} (based on {result['rating_count']} ratings)")
                return True
            else:
                update_query = "UPDATE Tutor SET rating = 0.0 WHERE tid = %s"
                self.cursor.execute(update_query, (tid,))
                return True
                
        except Exception as e:
            logger.error(f"Update tutor rating error: {e}", exc_info=True)
            return False

    def create_tutor(self, uid: int, rating: float = 0.0, status: str = 'available') -> Optional[Dict[str, Any]]:
        if not self._ensure_connection():
            logger.error("Create tutor failed: database connection unavailable")
            return None

        # Validate status
        valid_statuses = ['available', 'away', 'busy']
        if status not in valid_statuses:
            logger.error(f"Invalid status: {status}")
            return None

        try:
            # Check if user exists
            user_check = "SELECT uid, firstName, lastName, email FROM User WHERE uid = %s"
            self.cursor.execute(user_check, (uid,))
            user = self.cursor.fetchone()
            
            if not user:
                logger.error(f"User {uid} does not exist")
                return None

            # Check if user is already a tutor
            tutor_check = "SELECT tid FROM Tutor WHERE uid = %s"
            self.cursor.execute(tutor_check, (uid,))
            if self.cursor.fetchone():
                logger.error(f"User {uid} is already a tutor")
                return None

            # Create tutor
            query = """
                INSERT INTO Tutor (uid, rating, status, verificationStatus)
                VALUES (%s, %s, %s, 'unapproved')
            """
            
            self.cursor.execute(query, (uid, rating, status))
            tutor_id = self.cursor.lastrowid

            return {
                'tid': tutor_id,
                'uid': uid,
                'name': f"{user['firstName']} {user['lastName']}",
                'email': user['email'],
                'rating': rating,
                'status': status,
                'verificationStatus': 'unapproved'
            }

        except Exception as e:
            logger.error(f"Create tutor error: {e}", exc_info=True)
            return None

    def update_verification_status(self, tid: int, status: str) -> bool:
        if not self._ensure_connection():
            logger.error("Update verification failed: database connection unavailable")
            return False

        valid_statuses = ['unapproved', 'pending', 'approved']
        if status not in valid_statuses:
            logger.error(f"Invalid verification status: {status}")
            return False

        try:
            query = "UPDATE Tutor SET verificationStatus = %s WHERE tid = %s"
            self.cursor.execute(query, (status, tid))
            return self.cursor.rowcount > 0

        except Exception as e:
            logger.error(f"Update verification error: {e}", exc_info=True)
            return False

    def add_tutor_tags(self, tid: int, tag_ids: List[int]) -> bool:
        if not self._ensure_connection():
            logger.error("Add tutor tags failed: database connection unavailable")
            return False

        try:
            # Verify tutor exists
            check_query = "SELECT tid FROM Tutor WHERE tid = %s"
            self.cursor.execute(check_query, (tid,))
            if not self.cursor.fetchone():
                logger.error(f"Tutor {tid} does not exist")
                return False

            # Insert tags
            for tag_id in tag_ids:
                try:
                    query = "INSERT INTO TutorTags (tid, tagsID) VALUES (%s, %s)"
                    self.cursor.execute(query, (tid, tag_id))
                except mysql.connector.IntegrityError:
                    # Skip if exists
                    continue

            return True

        except Exception as e:
            logger.error(f"Add tutor tags error: {e}", exc_info=True)
            return False

    def get_tutor(self, tid: int) -> Optional[Dict[str, Any]]:
        if not self._ensure_connection():
            logger.error("Get tutor failed: database connection unavailable")
            return None

        try:
            query = """
                SELECT 
                    t.tid, t.uid, t.rating, t.status, t.verificationStatus,
                    u.firstName, u.lastName, u.email, u.bio, u.profilePicture
                FROM Tutor t
                INNER JOIN User u ON t.uid = u.uid
                WHERE t.tid = %s
            """
            
            self.cursor.execute(query, (tid,))
            tutor = self.cursor.fetchone()

            if not tutor:
                return None

            # Get tutor's tags
            tags_query = """
                SELECT tg.tagsID, tg.tags
                FROM TutorTags tt
                INNER JOIN Tags tg ON tt.tagsID = tg.tagsID
                WHERE tt.tid = %s
                ORDER BY tg.tags
            """
            self.cursor.execute(tags_query, (tid,))
            tags = self.cursor.fetchall()

            return {
                'tid': tutor['tid'],
                'uid': tutor['uid'],
                'name': f"{tutor['firstName']} {tutor['lastName']}",
                'email': tutor['email'],
                'bio': tutor['bio'],
                'profilePicture': tutor['profilePicture'],
                'rating': tutor['rating'],
                'status': tutor['status'],
                'verificationStatus': tutor['verificationStatus'],
                'expertise': [{'id': tag['tagsID'], 'name': tag['tags']} for tag in tags]
            }

        except Exception as e:
            logger.error(f"Get tutor error: {e}", exc_info=True)
            return None

    def get_tutor_by_uid(self, uid: int) -> Optional[Dict[str, Any]]:
        if not self._ensure_connection():
            logger.error("Get tutor by uid failed: database connection unavailable")
            return None

        try:
            query = """
                SELECT 
                    t.tid, t.uid, t.rating, t.status, t.verificationStatus,
                    u.firstName, u.lastName, u.email
                FROM Tutor t
                INNER JOIN User u ON t.uid = u.uid
                WHERE t.uid = %s
            """
            
            self.cursor.execute(query, (uid,))
            tutor = self.cursor.fetchone()

            if tutor:
                return {
                    'tid': tutor['tid'],
                    'uid': tutor['uid'],
                    'name': f"{tutor['firstName']} {tutor['lastName']}",
                    'email': tutor['email'],
                    'rating': tutor['rating'],
                    'status': tutor['status'],
                    'verificationStatus': tutor['verificationStatus']
                }
            
            return None

        except Exception as e:
            logger.error(f"Get tutor by uid error: {e}", exc_info=True)
            return None

    def get_top_tutors(self, limit: int = 10) -> List[Dict[str, Any]]:
        if not self._ensure_connection():
            logger.error("Get top tutors failed: database connection unavailable")
            return []

        try:
            query = """
                SELECT DISTINCT
                    t.tid,
                    u.firstName,
                    u.lastName,
                    u.email,
                    u.bio,
                    t.rating,
                    t.status
                FROM Tutor t
                INNER JOIN User u ON t.uid = u.uid
                INNER JOIN Posts p ON t.tid = p.tid
                WHERE t.verificationStatus = 'approved'
                GROUP BY t.tid
                ORDER BY t.rating DESC
                LIMIT %s
            """
            
            self.cursor.execute(query, (limit,))
            tutors = self.cursor.fetchall()
            
            results = []
            for tutor in tutors:
                results.append({
                    'tid': tutor['tid'],
                    'name': f"{tutor['firstName']} {tutor['lastName']}",
                    'email': tutor['email'],
                    'bio': tutor['bio'],
                    'rating': tutor['rating'],
                    'status': tutor['status']
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Get top tutors error: {e}", exc_info=True)
            return []

    def create_rating(self, tid: int, uid: int, sid: int, rating: float) -> Optional[Dict[str, Any]]:
        if not self._ensure_connection():
            logger.error("Create rating failed: database connection unavailable")
            return None

        if not (0 <= rating <= 5):
            logger.error(f"Invalid rating value: {rating}. Must be between 0 and 5")
            return None

        try:
            # Verify session meets criteria
            session_check = """
                SELECT sid FROM Sessions 
                WHERE sid = %s AND tid = %s AND uid = %s AND concluded IS NOT NULL
            """
            self.cursor.execute(session_check, (sid, tid, uid))
            if not self.cursor.fetchone():
                logger.error(f"Invalid session: sid={sid}, tid={tid}, uid={uid} or session not concluded")
                return None

            # Insert rating
            query = """
                INSERT INTO Ratings (tid, uid, sid, rating, timestamp)
                VALUES (%s, %s, %s, %s, NOW())
            """
            self.cursor.execute(query, (tid, uid, sid, rating))
            rating_id = self.cursor.lastrowid

            # Update tutor's average rating
            self.update_tutor_rating(tid)

            return {
                'rid': rating_id,
                'tid': tid,
                'uid': uid,
                'sid': sid,
                'rating': rating,
                'message': 'Rating submitted successfully. Tutor rating updated.'
            }

        except mysql.connector.IntegrityError:
            logger.error(f"User {uid} already rated session {sid}")
            return None
        except Exception as e:
            logger.error(f"Create rating error: {e}", exc_info=True)
            return None

    def get_tutor_rating_count(self, tid: int) -> int:
        if not self._ensure_connection():
            logger.error("Get rating count failed: database connection unavailable")
            return 0

        try:
            query = "SELECT COUNT(*) as count FROM Ratings WHERE tid = %s"
            self.cursor.execute(query, (tid,))
            result = self.cursor.fetchone()
            return result['count'] if result else 0

        except Exception as e:
            logger.error(f"Get rating count error: {e}", exc_info=True)
            return 0

    def user_can_rate_session(self, uid: int, sid: int) -> bool:
        if not self._ensure_connection():
            return False

        try:
            # Check session exists
            session_query = """
                SELECT sid FROM Sessions 
                WHERE sid = %s AND uid = %s AND concluded IS NOT NULL
            """
            self.cursor.execute(session_query, (sid, uid))
            if not self.cursor.fetchone():
                return False

            # Check if already rated
            rating_query = "SELECT rid FROM Ratings WHERE uid = %s AND sid = %s"
            self.cursor.execute(rating_query, (uid, sid))
            return self.cursor.fetchone() is None

        except Exception as e:
            logger.error(f"Check rating eligibility error: {e}", exc_info=True)
            return False

    def close(self):
        try:
            if self.cursor:
                self.cursor.close()
            if self.connection and self.connection.is_connected():
                self.connection.close()
        except Exception as e:
            logger.error(f"Error closing connection: {e}")