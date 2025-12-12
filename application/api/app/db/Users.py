import mysql.connector
from typing import Optional, Dict, Any
import bcrypt
import logging
from db.Auth import ConnectionPool

logger = logging.getLogger(__name__)


class GatorGuidesUsers:
    def __init__(self):
        self.pool = ConnectionPool()
    
    def _get_connection(self):
        return self.pool.get_connection()

    def _hash_password(self, password: str) -> str:
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    def _verify_password(self, password: str, hashed: str) -> bool:
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

    def create_user(self, first_name: str, last_name: str, email: str, password: str, user_type: str = 'user', profile_picture: Optional[str] = None, bio: Optional[str] = None) -> Optional[Dict[str, Any]]:
        conn = None
        try:
            if user_type not in ['user', 'admin']:
                logger.error(f"Invalid user type: {user_type}")
                return None

            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)
            
            # Hash the password
            hashed_password = self._hash_password(password)

            # Insert new user
            query = """
                INSERT INTO User (firstName, lastName, email, password, Type, profilePicture, bio)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            
            cursor.execute(
                query,
                (first_name, last_name, email, hashed_password, user_type, profile_picture, bio)
            )
            user_id = cursor.lastrowid
            cursor.close()

            # Return user info
            return {
                'uid': user_id,
                'firstName': first_name,
                'lastName': last_name,
                'email': email,
                'type': user_type,
                'profilePicture': profile_picture,
                'bio': bio
            }

        except mysql.connector.IntegrityError as e:
            logger.error(f"Create user failed - integrity error: {e}")
            return None
        except Exception as e:
            logger.error(f"Create user error: {e}", exc_info=True)
            return None
        finally:
            if conn:
                conn.close()

    def authenticate_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT uid, firstName, lastName, email, password, Type, profilePicture, bio
                FROM User
                WHERE email = %s
            """
            
            cursor.execute(query, (email,))
            user = cursor.fetchone()
            cursor.close()

            if not user:
                logger.warning(f"Authentication failed: user not found")
                return None

            # Verify password
            if not self._verify_password(password, user['password']):
                logger.warning(f"Authentication failed: invalid password")
                return None

            # Return user info
            return {
                'uid': user['uid'],
                'firstName': user['firstName'],
                'lastName': user['lastName'],
                'email': user['email'],
                'type': user['Type'],
                'profilePicture': user['profilePicture'],
                'bio': user['bio']
            }

        except Exception as e:
            logger.error(f"Authentication error: {e}", exc_info=True)
            return None
        finally:
            if conn:
                conn.close()

    def get_user(self, uid: int) -> Optional[Dict[str, Any]]:
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT uid, firstName, lastName, email, Type, profilePicture, bio
                FROM User
                WHERE uid = %s
            """
            
            cursor.execute(query, (uid,))
            user = cursor.fetchone()
            cursor.close()

            if user:
                return {
                    'uid': user['uid'],
                    'firstName': user['firstName'],
                    'lastName': user['lastName'],
                    'email': user['email'],
                    'type': user['Type'],
                    'profilePicture': user['profilePicture'],
                    'bio': user['bio']
                }
            
            return None

        except Exception as e:
            logger.error(f"Get user error: {e}", exc_info=True)
            return None
        finally:
            if conn:
                conn.close()

    def update_user(self, uid: int, first_name: Optional[str] = None, last_name: Optional[str] = None, profile_picture: Optional[str] = None, bio: Optional[str] = None) -> bool:
        conn = None
        try:
            updates = []
            values = []

            if first_name is not None:
                updates.append("firstName = %s")
                values.append(first_name)
            if last_name is not None:
                updates.append("lastName = %s")
                values.append(last_name)
            if profile_picture is not None:
                updates.append("profilePicture = %s")
                values.append(profile_picture)
            if bio is not None:
                updates.append("bio = %s")
                values.append(bio)

            if not updates:
                return False

            conn = self._get_connection()
            cursor = conn.cursor()
            
            values.append(uid)
            query = f"UPDATE User SET {', '.join(updates)} WHERE uid = %s"
            
            cursor.execute(query, tuple(values))
            rowcount = cursor.rowcount
            cursor.close()
            
            return rowcount > 0

        except Exception as e:
            logger.error(f"Update user error: {e}", exc_info=True)
            return False
        finally:
            if conn:
                conn.close()