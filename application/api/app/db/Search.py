from typing import List, Dict, Any
import logging
from db.Auth import ConnectionPool

logger = logging.getLogger(__name__)


class GatorGuidesSearch:
    def __init__(self):
        self.pool = ConnectionPool()
    
    def _get_connection(self):
        return self.pool.get_connection()

    def search(self, query: str) -> List[Dict[str, Any]]:
        conn = None
        cursor = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)
            
            results = []
            
            if not query or query.strip() == '':
                all_tutors_query = """
                    SELECT 
                        p.pid, p.tid, p.content, p.timestamp,
                        tutor.rating, tutor.status,
                        u.firstName, u.lastName, u.email, u.bio,
                        tg.tags as post_tag
                    FROM Posts p
                    INNER JOIN Tags tg ON p.tagsID = tg.tagsID
                    INNER JOIN Tutor tutor ON p.tid = tutor.tid
                    INNER JOIN User u ON tutor.uid = u.uid
                    WHERE tutor.verificationStatus = 'approved'
                    ORDER BY tutor.rating DESC, p.timestamp DESC
                """
                cursor.execute(all_tutors_query)
                posts_by_tag = cursor.fetchall()
            else:
                normalized_query = query.replace(' ', '').lower()
                
                tag_search_query = """
                    SELECT 
                        p.pid, p.tid, p.content, p.timestamp,
                        tutor.rating, tutor.status,
                        u.firstName, u.lastName, u.email, u.bio,
                        tg.tags as post_tag
                    FROM Posts p
                    INNER JOIN Tags tg ON p.tagsID = tg.tagsID
                    INNER JOIN Tutor tutor ON p.tid = tutor.tid
                    INNER JOIN User u ON tutor.uid = u.uid
                    WHERE REPLACE(LOWER(tg.tags), ' ', '') LIKE %s
                    AND tutor.verificationStatus = 'approved'
                    ORDER BY tutor.rating DESC, p.timestamp DESC
                """
                cursor.execute(tag_search_query, (f'%{normalized_query}%',))
                posts_by_tag = cursor.fetchall()

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
                    'timestamp': post['timestamp'].isoformat() if hasattr(post['timestamp'], 'isoformat') else str(post['timestamp'])
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
                cursor.execute(expertise_query, tuple(unique_tids))
                expertise_results = cursor.fetchall()

                for row in expertise_results:
                    tid = row['tid']
                    if tid in tag_tutor_data:
                        tag_tutor_data[tid]['profile_tags'].append(row['tags'])

            for data in tag_tutor_data.values():
                data['courses'] = list(data['courses'])
                results.append(data)

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

            cursor.execute(name_search_query, (f'%{query}%', f'%{query}%', f'%{query}%', f'%{query}%'))
            tutors_by_name = cursor.fetchall()

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
                cursor.execute(posts_query, tuple(name_tids))
                posts_results = cursor.fetchall()

                for post in posts_results:
                    tid = post['tid']
                    if tid in name_tutor_data:
                        name_tutor_data[tid]['posts'].append({
                            'pid': post['pid'],
                            'course': post['tags'],
                            'content': post['content'],
                            'timestamp': post['timestamp'].isoformat() if hasattr(post['timestamp'], 'isoformat') else str(post['timestamp'])
                        })
                        name_tutor_data[tid]['courses'].add(post['tags'])

                expertise_query = f"""
                    SELECT tt.tid, tg.tags
                    FROM TutorTags tt
                    INNER JOIN Tags tg ON tt.tagsID = tg.tagsID
                    WHERE tt.tid IN ({placeholders})
                    ORDER BY tt.tid, tg.tags
                """
                cursor.execute(expertise_query, tuple(name_tids))
                expertise_results = cursor.fetchall()

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
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def get_all_tags(self) -> List[Dict[str, Any]]:
        conn = None
        cursor = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = "SELECT tagsID, tags FROM Tags ORDER BY tags"
            cursor.execute(query)
            tags = cursor.fetchall()
            
            return [{"id": tag["tagsID"], "name": tag["tags"]} for tag in tags]
            
        except Exception as e:
            logger.error(f"Get tags error: {e}", exc_info=True)
            return []
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()