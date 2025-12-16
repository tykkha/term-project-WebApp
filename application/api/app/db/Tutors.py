from typing import Optional, Dict, Any, List
import logging
from db.Auth import ConnectionPool
import mysql.connector

logger = logging.getLogger(__name__)


class GatorGuidesTutors:
    def __init__(self):
        self.pool = ConnectionPool()
    
    def _get_connection(self):
        return self.pool.get_connection()

    def update_tutor_rating(self, tid: int) -> bool:
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)
            
            avg_query = """
                        SELECT AVG(rating) AS avg_rating, COUNT(*) AS rating_count
                        FROM Ratings
                        WHERE tid = %s
                        """
            cursor.execute(avg_query, (tid,))
            result = cursor.fetchone()

            if result and result['rating_count'] > 0:
                avg_rating = round(result['avg_rating'], 2)
                update_query = "UPDATE Tutor SET rating = %s WHERE tid = %s"
                cursor.execute(update_query, (avg_rating, tid))
            else:
                update_query = "UPDATE Tutor SET rating = 0.0 WHERE tid = %s"
                cursor.execute(update_query, (tid,))
            
            conn.commit()  
            cursor.close()
            return True

        except Exception as e:
            logger.error(f"Update tutor rating error: {e}", exc_info=True)
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                conn.close()

    def create_tutor(self, uid: int, rating: float = 0.0, status: str = 'available') -> Optional[Dict[str, Any]]:
        conn = None
        try:
            valid_statuses = ['available', 'away', 'busy']
            if status not in valid_statuses:
                logger.error(f"Invalid status: {status}")
                return None

            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)
            
            user_check = """
                         SELECT uid, firstName, lastName, email
                         FROM User
                         WHERE uid = %s
                         """
            cursor.execute(user_check, (uid,))
            user = cursor.fetchone()

            if not user:
                logger.error(f"User {uid} does not exist")
                cursor.close()
                return None

            tutor_check = "SELECT tid FROM Tutor WHERE uid = %s"
            cursor.execute(tutor_check, (uid,))
            if cursor.fetchone():
                logger.error(f"User {uid} is already a tutor")
                cursor.close()
                return None

            query = """
                    INSERT INTO Tutor (uid, rating, status, verificationStatus)
                    VALUES (%s, %s, %s, 'pending')
                    """
            cursor.execute(query, (uid, rating, status))
            conn.commit()  
            tutor_id = cursor.lastrowid
            cursor.close()

            return {
                'tid': tutor_id,
                'uid': uid,
                'name': f"{user['firstName']} {user['lastName']}",
                'email': user['email'],
                'rating': rating,
                'status': status,
                'verificationStatus': 'pending'
            }

        except Exception as e:
            logger.error(f"Create tutor error: {e}", exc_info=True)
            if conn:
                conn.rollback()
            return None
        finally:
            if conn:
                conn.close()

    def update_verification_status(self, tid: int, status: str) -> bool:
        conn = None
        try:
            valid_statuses = ['unapproved', 'pending', 'approved']
            if status not in valid_statuses:
                logger.error(f"Invalid verification status: {status}")
                return False

            conn = self._get_connection()
            cursor = conn.cursor()
            
            query = "UPDATE Tutor SET verificationStatus = %s WHERE tid = %s"
            cursor.execute(query, (status, tid))
            conn.commit()  
            rowcount = cursor.rowcount
            cursor.close()
            
            return rowcount > 0

        except Exception as e:
            logger.error(f"Update verification error: {e}", exc_info=True)
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                conn.close()

    def add_tutor_tags(self, tid: int, tag_ids: List[int]) -> bool:
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            check_query = "SELECT tid FROM Tutor WHERE tid = %s"
            cursor.execute(check_query, (tid,))
            if not cursor.fetchone():
                logger.error(f"Tutor {tid} does not exist")
                cursor.close()
                return False

            for tag_id in tag_ids:
                try:
                    query = "INSERT INTO TutorTags (tid, tagsID) VALUES (%s, %s)"
                    cursor.execute(query, (tid, tag_id))
                except mysql.connector.IntegrityError:
                    # Tag already exists for this tutor, skip
                    continue

            conn.commit()  
            cursor.close()
            return True

        except Exception as e:
            logger.error(f"Add tutor tags error: {e}", exc_info=True)
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                conn.close()

    def get_tutor(self, tid: int) -> Optional[Dict[str, Any]]:
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = """
                    SELECT
                        t.tid, t.uid, t.rating, t.status, t.verificationStatus,
                        u.firstName, u.lastName, u.email, u.bio, u.profilePicture
                    FROM Tutor t
                             INNER JOIN User u ON t.uid = u.uid
                    WHERE t.tid = %s
                    """
            cursor.execute(query, (tid,))
            tutor = cursor.fetchone()

            if not tutor:
                cursor.close()
                return None

            tags_query = """
                         SELECT tg.tagsID, tg.tags
                         FROM TutorTags tt
                                  INNER JOIN Tags tg ON tt.tagsID = tg.tagsID
                         WHERE tt.tid = %s
                         ORDER BY tg.tags
                         """
            cursor.execute(tags_query, (tid,))
            tags = cursor.fetchall()
            cursor.close()

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
                'expertise': [
                    {'id': tag['tagsID'], 'name': tag['tags']}
                    for tag in tags
                ]
            }

        except Exception as e:
            logger.error(f"Get tutor error: {e}", exc_info=True)
            return None
        finally:
            if conn:
                conn.close()

    def get_tutor_by_uid(self, uid: int) -> Optional[Dict[str, Any]]:
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = """
                    SELECT
                        t.tid, t.uid, t.rating, t.status, t.verificationStatus,
                        u.firstName, u.lastName, u.email
                    FROM Tutor t
                             INNER JOIN User u ON t.uid = u.uid
                    WHERE t.uid = %s
                    """
            cursor.execute(query, (uid,))
            tutor = cursor.fetchone()
            cursor.close()

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
        finally:
            if conn:
                conn.close()

    def get_all_tutors(self) -> List[Dict[str, Any]]:
        """
        Return **all** tutors in the system with their tags included.
        Optimized to fetch all tutor-tag relationships in a single query.
        """
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)
            
            # First, get all tutors
            query = """
                    SELECT
                        t.tid,
                        u.firstName,
                        u.lastName,
                        u.email,
                        u.bio,
                        COALESCE(t.rating, 0) AS rating,
                        t.status,
                        t.verificationStatus
                    FROM Tutor t
                             INNER JOIN User u ON t.uid = u.uid
                    ORDER BY
                        CASE
                            WHEN t.verificationStatus = 'approved' THEN 0
                            WHEN t.verificationStatus = 'pending' THEN 1
                            ELSE 2
                            END,
                        rating DESC,
                        t.tid ASC
                    """
            cursor.execute(query)
            tutors = cursor.fetchall()

            if not tutors:
                cursor.close()
                return []

            # Get all tutor IDs
            tutor_ids = [t['tid'] for t in tutors]

            # Fetch all tags for all tutors in a single query
            tags_query = """
                         SELECT tt.tid, tg.tagsID, tg.tags
                         FROM TutorTags tt
                                  INNER JOIN Tags tg ON tt.tagsID = tg.tagsID
                         WHERE tt.tid IN (%s)
                         ORDER BY tt.tid, tg.tags
                         """ % ','.join(['%s'] * len(tutor_ids))

            cursor.execute(tags_query, tutor_ids)
            all_tags = cursor.fetchall()
            cursor.close()

            # Group tags by tutor ID
            tags_by_tutor = {}
            for tag in all_tags:
                tid = tag['tid']
                if tid not in tags_by_tutor:
                    tags_by_tutor[tid] = []
                tags_by_tutor[tid].append({
                    'id': tag['tagsID'],
                    'name': tag['tags']
                })

            # Build results with tags included
            results: List[Dict[str, Any]] = []
            for tutor in tutors:
                tid = tutor['tid']
                results.append({
                    'tid': tid,
                    'name': f"{tutor['firstName']} {tutor['lastName']}",
                    'email': tutor['email'],
                    'bio': tutor['bio'],
                    'rating': float(tutor['rating']) if tutor['rating'] is not None else 0.0,
                    'status': tutor['status'],
                    'verificationStatus': tutor['verificationStatus'],
                    'tags': tags_by_tutor.get(tid, [])
                })

            return results

        except Exception as e:
            logger.error(f"Get all tutors error: {e}", exc_info=True)
            return []
        finally:
            if conn:
                conn.close()

    def get_top_tutors(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Return top tutors with their tags included.
        Optimized to fetch all tutor-tag relationships in a single query.
        """
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)
            
            # First, get top tutors
            query = """
                    SELECT
                        t.tid,
                        u.firstName,
                        u.lastName,
                        u.email,
                        u.bio,
                        COALESCE(t.rating, 0) AS rating,
                        t.status,
                        t.verificationStatus
                    FROM Tutor t
                             INNER JOIN User u ON t.uid = u.uid
                    ORDER BY
                        CASE
                            WHEN t.verificationStatus = 'approved' THEN 0
                            WHEN t.verificationStatus = 'pending' THEN 1
                            ELSE 2
                            END,
                        rating DESC,
                        t.tid ASC
                        LIMIT %s
                    """
            cursor.execute(query, (limit,))
            tutors = cursor.fetchall()

            if not tutors:
                cursor.close()
                return []

            # Get all tutor IDs
            tutor_ids = [t['tid'] for t in tutors]

            # Fetch all tags for these tutors in a single query
            tags_query = """
                         SELECT tt.tid, tg.tagsID, tg.tags
                         FROM TutorTags tt
                                  INNER JOIN Tags tg ON tt.tagsID = tg.tagsID
                         WHERE tt.tid IN (%s)
                         ORDER BY tt.tid, tg.tags
                         """ % ','.join(['%s'] * len(tutor_ids))
        
            cursor.execute(tags_query, tutor_ids)
            all_tags = cursor.fetchall()
            cursor.close()

            # Group tags by tutor ID
            tags_by_tutor = {}
            for tag in all_tags:
                tid = tag['tid']
                if tid not in tags_by_tutor:
                    tags_by_tutor[tid] = []
                tags_by_tutor[tid].append({
                    'id': tag['tagsID'],
                    'name': tag['tags']
                })

            # Build results with tags included
            results: List[Dict[str, Any]] = []
            for tutor in tutors:
                tid = tutor['tid']
                results.append({
                    'tid': tid,
                    'name': f"{tutor['firstName']} {tutor['lastName']}",
                    'email': tutor['email'],
                    'bio': tutor['bio'],
                    'rating': float(tutor['rating']) if tutor['rating'] is not None else 0.0,
                    'status': tutor['status'],
                    'verificationStatus': tutor['verificationStatus'],
                    'tags': tags_by_tutor.get(tid, [])
                })

            return results

        except Exception as e:
            logger.error(f"Get top tutors error: {e}", exc_info=True)
            return []
        finally:
            if conn:
                conn.close()

    def create_rating(
            self,
            tid: int,
            uid: int,
            sid: int,
            rating: float
    ) -> Optional[Dict[str, Any]]:
        conn = None
        try:
            if not (0 <= rating <= 5):
                logger.error(f"Invalid rating value: {rating}. Must be between 0 and 5")
                return None

            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)
            
            session_check = """
                            SELECT sid
                            FROM Sessions
                            WHERE sid = %s AND tid = %s AND uid = %s AND concluded IS NOT NULL
                            """
            cursor.execute(session_check, (sid, tid, uid))
            if not cursor.fetchone():
                logger.error(
                    f"Invalid session: sid={sid}, tid={tid}, uid={uid} or session not concluded"
                )
                cursor.close()
                return None

            query = """
                    INSERT INTO Ratings (tid, uid, sid, rating, timestamp)
                    VALUES (%s, %s, %s, %s, NOW())
                    """
            cursor.execute(query, (tid, uid, sid, rating))
            conn.commit()  
            rating_id = cursor.lastrowid
            cursor.close()

            self.update_tutor_rating(tid)

            return {
                'rid': rating_id,
                'tid': tid,
                'uid': uid,
                'sid': sid,
                'rating': rating,
                'message': 'Rating submitted successfully. Tutor rating updated.'
            }

        except mysql.connector.IntegrityError as e:
            logger.error(f"User {uid} already rated session {sid}: {e}")
            if conn:
                conn.rollback()
            return None
        except Exception as e:
            logger.error(f"Create rating error: {e}", exc_info=True)
            if conn:
                conn.rollback()
            return None
        finally:
            if conn:
                conn.close()

    def get_tutor_rating_count(self, tid: int) -> int:
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = "SELECT COUNT(*) AS count FROM Ratings WHERE tid = %s"
            cursor.execute(query, (tid,))
            result = cursor.fetchone()
            cursor.close()
            
            return result['count'] if result else 0

        except Exception as e:
            logger.error(f"Get rating count error: {e}", exc_info=True)
            return 0
        finally:
            if conn:
                conn.close()

    def user_can_rate_session(self, uid: int, sid: int) -> bool:
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)
            
            session_query = """
                            SELECT sid
                            FROM Sessions
                            WHERE sid = %s AND uid = %s AND concluded IS NOT NULL
                            """
            cursor.execute(session_query, (sid, uid))
            if not cursor.fetchone():
                cursor.close()
                return False

            rating_query = "SELECT rid FROM Ratings WHERE uid = %s AND sid = %s"
            cursor.execute(rating_query, (uid, sid))
            result = cursor.fetchone() is None
            cursor.close()
            
            return result

        except Exception as e:
            logger.error(f"Check rating eligibility error: {e}", exc_info=True)
            return False
        finally:
            if conn:
                conn.close()

    def get_pending_tutors(self) -> List[Dict[str, Any]]:
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)
            
            # Get all pending tutors
            query = """
                    SELECT
                        t.tid,
                        t.uid,
                        u.firstName,
                        u.lastName,
                        u.email,
                        u.bio,
                        u.profilePicture,
                        COALESCE(t.rating, 0) AS rating,
                        t.status,
                        t.verificationStatus
                    FROM Tutor t
                             INNER JOIN User u ON t.uid = u.uid
                    WHERE t.verificationStatus = 'pending'
                    ORDER BY t.tid ASC
                    """
            cursor.execute(query)
            tutors = cursor.fetchall()

            if not tutors:
                cursor.close()
                return []

            # Get all tutor IDs
            tutor_ids = [t['tid'] for t in tutors]

            tags_query = """
                         SELECT tt.tid, tg.tagsID, tg.tags
                         FROM TutorTags tt
                                  INNER JOIN Tags tg ON tt.tagsID = tg.tagsID
                         WHERE tt.tid IN (%s)
                         ORDER BY tt.tid, tg.tags
                         """ % ','.join(['%s'] * len(tutor_ids))

            cursor.execute(tags_query, tutor_ids)
            all_tags = cursor.fetchall()
            cursor.close()

            # Group tags by tutor ID
            tags_by_tutor = {}
            for tag in all_tags:
                tid = tag['tid']
                if tid not in tags_by_tutor:
                    tags_by_tutor[tid] = []
                tags_by_tutor[tid].append({
                    'id': tag['tagsID'],
                    'name': tag['tags']
                })

            # Build results with tags included
            results: List[Dict[str, Any]] = []
            for tutor in tutors:
                tid = tutor['tid']
                results.append({
                    'tid': tid,
                    'uid': tutor['uid'],
                    'name': f"{tutor['firstName']} {tutor['lastName']}",
                    'email': tutor['email'],
                    'bio': tutor['bio'],
                    'profilePicture': tutor['profilePicture'],
                    'rating': float(tutor['rating']) if tutor['rating'] is not None else 0.0,
                    'status': tutor['status'],
                    'verificationStatus': tutor['verificationStatus'],
                    'tags': tags_by_tutor.get(tid, [])
                })

            return results

        except Exception as e:
            logger.error(f"Get pending tutors error: {e}", exc_info=True)
            return []
        finally:
            if conn:
                conn.close()

    def reject_tutor(self, tid: int) -> bool:
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)
            
            # Check current status
            check_query = "SELECT verificationStatus FROM Tutor WHERE tid = %s"
            cursor.execute(check_query, (tid,))
            tutor = cursor.fetchone()
            
            if not tutor:
                logger.error(f"Tutor {tid} does not exist")
                cursor.close()
                return False
            
            if tutor['verificationStatus'] != 'pending':
                logger.error(f"Tutor {tid} is not pending (current status: {tutor['verificationStatus']})")
                cursor.close()
                return False
            
            # Update to unapproved
            update_query = "UPDATE Tutor SET verificationStatus = 'unapproved' WHERE tid = %s"
            cursor.execute(update_query, (tid,))
            conn.commit()  
            rowcount = cursor.rowcount
            cursor.close()
            
            if rowcount > 0:
                logger.info(f"Tutor {tid} rejected (status set to unapproved)")
                return True
            
            return False

        except Exception as e:
            logger.error(f"Reject tutor error: {e}", exc_info=True)
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                conn.close()

    def approve_tutor(self, tid: int) -> bool:
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)
            
            # Check current status
            check_query = "SELECT verificationStatus FROM Tutor WHERE tid = %s"
            cursor.execute(check_query, (tid,))
            tutor = cursor.fetchone()
            
            if not tutor:
                logger.error(f"Tutor {tid} does not exist")
                cursor.close()
                return False
            
            if tutor['verificationStatus'] != 'pending':
                logger.error(f"Tutor {tid} is not pending (current status: {tutor['verificationStatus']})")
                cursor.close()
                return False
            
            # Update to approved
            update_query = "UPDATE Tutor SET verificationStatus = 'approved' WHERE tid = %s"
            cursor.execute(update_query, (tid,))
            conn.commit()  
            rowcount = cursor.rowcount
            cursor.close()
            
            if rowcount > 0:
                logger.info(f"Tutor {tid} accepted (status set to approved)")
                return True
            
            return False

        except Exception as e:
            logger.error(f"Tutor approval error: {e}", exc_info=True)
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                conn.close()