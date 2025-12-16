import logging
from typing import Optional, List, Dict, Any
from db.Auth import ConnectionPool

logger = logging.getLogger(__name__)


class GatorGuidesAvailability:
    def __init__(self):
        self.pool = ConnectionPool()
    
    def _get_connection(self):
        return self.pool.get_connection()

    def add_availability(self, tid: int, day: str, start_time: int, end_time: int) -> Optional[Dict[str, Any]]:
        """Add a new availability slot for a tutor"""
        conn = None
        try:
            if start_time >= end_time:
                logger.error(f"Invalid time range: start_time={start_time}, end_time={end_time}")
                return None

            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = """
                INSERT INTO TutorAvailability (tid, day, startTime, endTime)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE isActive = TRUE
            """
            
            cursor.execute(query, (tid, day, start_time, end_time))
            conn.commit()
            availability_id = cursor.lastrowid
            
            cursor.execute("SELECT * FROM TutorAvailability WHERE availabilityID = %s", (availability_id,))
            availability = cursor.fetchone()
            cursor.close()
            
            logger.info(f"Availability added: tid={tid}, day={day}, time={start_time}-{end_time}")
            return availability
            
        except Exception as e:
            logger.error(f"Add availability error: {e}", exc_info=True)
            if conn:
                conn.rollback()
            return None
        finally:
            if conn:
                conn.close()

    def get_tutor_availability(self, tid: int) -> List[Dict[str, Any]]:
        """Get all availability slots for a tutor"""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT availabilityID, tid, day, startTime, endTime, isActive
                FROM TutorAvailability
                WHERE tid = %s AND isActive = TRUE
                ORDER BY 
                    FIELD(day, 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'),
                    startTime
            """
            
            cursor.execute(query, (tid,))
            availability = cursor.fetchall()
            cursor.close()
            
            return availability
            
        except Exception as e:
            logger.error(f"Get tutor availability error: {e}", exc_info=True)
            return []
        finally:
            if conn:
                conn.close()

    def remove_availability(self, availability_id: int, tid: int) -> bool:
        """Remove an availability slot"""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            query = "DELETE FROM TutorAvailability WHERE availabilityID = %s AND tid = %s"
            cursor.execute(query, (availability_id, tid))
            conn.commit()
            rowcount = cursor.rowcount
            cursor.close()
            
            if rowcount > 0:
                logger.info(f"Availability removed: availabilityID={availability_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Remove availability error: {e}", exc_info=True)
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                conn.close()

    def set_bulk_availability(self, tid: int, availability_slots: List[Dict[str, Any]]) -> bool:
        """Set multiple availability slots at once, replacing existing ones"""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Clear existing availability
            cursor.execute("DELETE FROM TutorAvailability WHERE tid = %s", (tid,))
            
            # Insert new slots
            if availability_slots:
                query = """
                    INSERT INTO TutorAvailability (tid, day, startTime, endTime)
                    VALUES (%s, %s, %s, %s)
                """
                for slot in availability_slots:
                    cursor.execute(query, (
                        tid,
                        slot['day'],
                        slot['startTime'],
                        slot['endTime']
                    ))
            conn.commit()
            cursor.close()
            logger.info(f"Bulk availability set for tid={tid}, {len(availability_slots)} slots")
            return True
            
        except Exception as e:
            logger.error(f"Set bulk availability error: {e}", exc_info=True)
            if conn:
                conn.rollback()
            return False
        finally:
            if conn:
                conn.close()

    def check_availability(self, tid: int, day: str, time: int) -> bool:
        """Check if a tutor is available at a specific day and time"""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT COUNT(*) as count
                FROM TutorAvailability
                WHERE tid = %s 
                  AND day = %s 
                  AND startTime <= %s 
                  AND endTime > %s
                  AND isActive = TRUE
            """
            
            cursor.execute(query, (tid, day, time, time))
            result = cursor.fetchone()
            cursor.close()
            
            return result['count'] > 0
            
        except Exception as e:
            logger.error(f"Check availability error: {e}", exc_info=True)
            return False
        finally:
            if conn:
                conn.close()

    def get_available_times_for_day(self, tid: int, day: str) -> List[int]:
        """Get all available hours for a tutor on a specific day"""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT startTime, endTime
                FROM TutorAvailability
                WHERE tid = %s AND day = %s AND isActive = TRUE
                ORDER BY startTime
            """
            
            cursor.execute(query, (tid, day))
            slots = cursor.fetchall()
            cursor.close()
            
            # Generate list of all available hours
            available_hours = []
            for slot in slots:
                for hour in range(slot['startTime'], slot['endTime']):
                    if hour not in available_hours:
                        available_hours.append(hour)
            
            return sorted(available_hours)
            
        except Exception as e:
            logger.error(f"Get available times error: {e}", exc_info=True)
            return []
        finally:
            if conn:
                conn.close()