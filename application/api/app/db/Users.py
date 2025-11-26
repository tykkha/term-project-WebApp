import mysql.connector
from typing import Optional, Dict, Any
import bcrypt
import logging

logger = logging.getLogger(__name__)


class GatorGuidesUsers:
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
                pool_name='users_pool',
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

    def _hash_password(self, password: str) -> str:
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    def _verify_password(self, password: str, hashed: str) -> bool:
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

    def create_user(
        self,
        first_name: str,
        last_name: str,
        email: str,
        password: str,
        user_type: str = 'user',
        profile_picture: Optional[str] = None,
        bio: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        if not self._ensure_connection():
            logger.error("Create user failed: database connection unavailable")
            return None

        # Validate user type
        if user_type not in ['user', 'admin']:
            logger.error(f"Invalid user type: {user_type}")
            return None

        try:
            # Hash the password
            hashed_password = self._hash_password(password)

            # Insert new user
            query = """
                INSERT INTO User (firstName, lastName, email, password, Type, profilePicture, bio)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            
            self.cursor.execute(
                query,
                (first_name, last_name, email, hashed_password, user_type, profile_picture, bio)
            )
            user_id = self.cursor.lastrowid

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

    def authenticate_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        if not self._ensure_connection():
            logger.error("Authentication failed: database connection unavailable")
            return None

        try:
            query = """
                SELECT uid, firstName, lastName, email, password, Type, profilePicture, bio
                FROM User
                WHERE email = %s
            """
            
            self.cursor.execute(query, (email,))
            user = self.cursor.fetchone()

            if not user:
                logger.warning(f"Authentication failed: user not found for email {email}")
                return None

            # Verify password
            if not self._verify_password(password, user['password']):
                logger.warning(f"Authentication failed: invalid password for email {email}")
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

    def get_user(self, uid: int) -> Optional[Dict[str, Any]]:
        if not self._ensure_connection():
            logger.error("Get user failed: database connection unavailable")
            return None

        try:
            query = """
                SELECT uid, firstName, lastName, email, Type, profilePicture, bio
                FROM User
                WHERE uid = %s
            """
            
            self.cursor.execute(query, (uid,))
            user = self.cursor.fetchone()

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

    def update_user(
        self,
        uid: int,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        profile_picture: Optional[str] = None,
        bio: Optional[str] = None
    ) -> bool:
        if not self._ensure_connection():
            logger.error("Update user failed: database connection unavailable")
            return False

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

            values.append(uid)
            query = f"UPDATE User SET {', '.join(updates)} WHERE uid = %s"
            
            self.cursor.execute(query, tuple(values))
            return self.cursor.rowcount > 0

        except Exception as e:
            logger.error(f"Update user error: {e}", exc_info=True)
            return False

    def close(self):
        try:
            if self.cursor:
                self.cursor.close()
            if self.connection and self.connection.is_connected():
                self.connection.close()
        except Exception as e:
            logger.error(f"Error closing connection: {e}")