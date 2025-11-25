import mysql.connector
from typing import List, Dict, Any
import logging

# Dependency: pip install mysql-connector-python

logger = logging.getLogger(__name__)

class GatorGuidesSearch:
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
                pool_name='gatorguides_pool',
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

    def search(self, query: str) -> List[Dict[str, Any]]:
        if not self._ensure_connection():
            logger.error("Search failed: database connection unavailable")
            return []

        try:
            results = []
            if not query or query.strip() == '':
                all_tutors_query = """
                    SELECT 
                        p.pid, p.tid, p.content, p.timestamp,
                        t.rating, t.status,
                        u.firstName, u.lastName, u.email, u.bio,
                        tg.tags as post_tag
                    FROM Posts p
                    INNER JOIN Tags tg ON p.tagsID = tg.tagsID
                    INNER JOIN Tutor t ON p.tid = t.tid
                    INNER JOIN User u ON t.uid = u.uid
                    WHERE t.verificationStatus = 'approved'
                    ORDER BY t.rating DESC, p.timestamp DESC
                """
                self.cursor.execute(all_tutors_query)
                posts_by_tag = self.cursor.fetchall()
            else:
                tag_search_query = """
                    SELECT 
                        p.pid, p.tid, p.content, p.timestamp,
                        t.rating, t.status,
                        u.firstName, u.lastName, u.email, u.bio,
                        tg.tags as post_tag
                    FROM Posts p
                    INNER JOIN Tags tg ON p.tagsID = tg.tagsID
                    INNER JOIN Tutor t ON p.tid = t.tid
                    INNER JOIN User u ON t.uid = u.uid
                    WHERE tg.tags LIKE %s
                    AND t.verificationStatus = 'approved'
                    ORDER BY t.rating DESC, p.timestamp DESC
                """
                self.cursor.execute(tag_search_query, (f'%{query}%',))
                posts_by_tag = self.cursor.fetchall()

            unique_tids = set()
            tag_tutor_data = {}

            for post in posts_by_tag:
                tid = post['tid']
                unique_tids.add(tid)

                if tid not in tag_tutor_data:
                    tag_tutor_data[tid] = {
                        'tid': tid,
                        'name': f"{post['firstName']} {post['lastName']}",
                        'email': post['email'],
                        'rating': post['rating'],
                        'status': post['status'],
                        'profile_tags': [],
                        'bio': post['bio'],
                        'match_type': 'tag',
                        'posts': [],
                        'courses': set()
                    }

                tag_tutor_data[tid]['posts'].append({
                    'pid': post['pid'],
                    'course': post['post_tag'],
                    'content': post['content'],
                    'timestamp': post['timestamp']
                })
                tag_tutor_data[tid]['courses'].add(post['post_tag'])

            if unique_tids:
                placeholders = ','.join(['%s'] * len(unique_tids))
                expertise_query = f"""
                    SELECT tt.tid, tg.tags
                    FROM TutorTags tt
                    INNER JOIN Tags tg ON tt.tagsID = tg.tagsID
                    WHERE tt.tid IN ({placeholders})
                    ORDER BY tt.tid, tg.tags
                """
                self.cursor.execute(expertise_query, tuple(unique_tids))
                expertise_results = self.cursor.fetchall()

                for row in expertise_results:
                    tid = row['tid']
                    if tid in tag_tutor_data:
                        tag_tutor_data[tid]['profile_tags'].append(row['tags'])

            for data in tag_tutor_data.values():
                data['courses'] = list(data['courses'])
                results.append(data)

            if not query or query.strip() == '':
                return results

            name_search_query = """
                SELECT DISTINCT
                    t.tid, t.rating, t.status,
                    u.firstName, u.lastName, u.email, u.bio,
                    CASE 
                        WHEN u.firstName LIKE %s THEN 1
                        WHEN u.lastName LIKE %s THEN 2
                        ELSE 3
                    END as name_priority
                FROM Tutor t
                INNER JOIN User u ON t.uid = u.uid
                WHERE (u.firstName LIKE %s OR u.lastName LIKE %s)
                AND t.verificationStatus = 'approved'
                ORDER BY name_priority, u.firstName, u.lastName
            """

            self.cursor.execute(name_search_query, (f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%'))
            tutors_by_name = self.cursor.fetchall()

            name_tids = []
            name_tutor_data = {}

            for tutor in tutors_by_name:
                tid = tutor['tid']
                if tid not in tag_tutor_data:
                    name_tids.append(tid)
                    name_tutor_data[tid] = {
                        'tid': tid,
                        'name': f"{tutor['firstName']} {tutor['lastName']}",
                        'email': tutor['email'],
                        'rating': tutor['rating'],
                        'status': tutor['status'],
                        'profile_tags': [],
                        'bio': tutor['bio'],
                        'match_type': 'name',
                        'posts': [],
                        'courses': set()
                    }

            if name_tids:
                placeholders = ','.join(['%s'] * len(name_tids))
                posts_query = f"""
                    SELECT p.pid, p.tid, p.content, p.timestamp, tg.tags
                    FROM Posts p
                    INNER JOIN Tags tg ON p.tagsID = tg.tagsID
                    WHERE p.tid IN ({placeholders})
                    ORDER BY p.tid, p.timestamp DESC
                """
                self.cursor.execute(posts_query, tuple(name_tids))
                posts_results = self.cursor.fetchall()

                for post in posts_results:
                    tid = post['tid']
                    if tid in name_tutor_data:
                        name_tutor_data[tid]['posts'].append({
                            'pid': post['pid'],
                            'course': post['tags'],
                            'content': post['content'],
                            'timestamp': post['timestamp']
                        })
                        name_tutor_data[tid]['courses'].add(post['tags'])

                expertise_query = f"""
                    SELECT tt.tid, tg.tags
                    FROM TutorTags tt
                    INNER JOIN Tags tg ON tt.tagsID = tg.tagsID
                    WHERE tt.tid IN ({placeholders})
                    ORDER BY tt.tid, tg.tags
                """
                self.cursor.execute(expertise_query, tuple(name_tids))
                expertise_results = self.cursor.fetchall()

                for row in expertise_results:
                    tid = row['tid']
                    if tid in name_tutor_data:
                        name_tutor_data[tid]['profile_tags'].append(row['tags'])

            for data in name_tutor_data.values():
                data['courses'] = list(data['courses'])
                results.append(data)

            return results

        except Exception as e:
            logger.error(f"Search error for query '{query}': {e}", exc_info=True)
            return []

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

    def close(self):
        try:
            if self.cursor:
                self.cursor.close()
            if self.connection and self.connection.is_connected():
                self.connection.close()
        except Exception as e:
            logger.error(f"Error closing connection: {e}")