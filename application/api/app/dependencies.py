from db.Auth import GatorGuidesAuth
from db.Messages import GatorGuidesMessages
from db.Posts import GatorGuidesPosts
from db.Search import GatorGuidesSearch
from db.Sessions import GatorGuidesSessions
from db.Tutors import GatorGuidesTutors
from db.Users import GatorGuidesUsers
from db.Availability import GatorGuidesAvailability

_auth_manager_instance = None
_session_manager_instance = None
_users_manager_instance = None
_tutors_manager_instance = None
_posts_manager_instance = None
_messages_manager_instance = None
_search_manager_instance = None
_availability_manager_instance = None

def set_auth_manager_instance(instance: GatorGuidesAuth):
    global _auth_manager_instance
    _auth_manager_instance = instance

def set_session_manager_instance(instance: GatorGuidesSessions):
    global _session_manager_instance
    _session_manager_instance = instance

def set_users_manager_instance(instance: GatorGuidesUsers):
    global _users_manager_instance
    _users_manager_instance = instance

def set_tutors_manager_instance(instance: GatorGuidesTutors):
    global _tutors_manager_instance
    _tutors_manager_instance = instance

def set_posts_manager_instance(instance: GatorGuidesPosts):
    global _posts_manager_instance
    _posts_manager_instance = instance

def set_messages_manager_instance(instance: GatorGuidesMessages):
    global _messages_manager_instance
    _messages_manager_instance = instance

def set_search_manager_instance(instance: GatorGuidesSearch):
    global _search_manager_instance
    _search_manager_instance = instance

def set_availability_manager_instance(instance: GatorGuidesAvailability):
    global _availability_manager_instance
    _availability_manager_instance = instance

def get_auth_manager() -> GatorGuidesAuth:
    if not _auth_manager_instance:
        raise RuntimeError("Auth manager not initialized")
    return _auth_manager_instance

def get_session_manager() -> GatorGuidesSessions:
    if not _session_manager_instance:
        raise RuntimeError("Session manager not initialized")
    return _session_manager_instance

def get_users_manager() -> GatorGuidesUsers:
    if not _users_manager_instance:
        raise RuntimeError("Users manager not initialized")
    return _users_manager_instance

def get_tutors_manager() -> GatorGuidesTutors:
    if not _tutors_manager_instance:
        raise RuntimeError("Tutors manager not initialized")
    return _tutors_manager_instance

def get_posts_manager() -> GatorGuidesPosts:
    if not _posts_manager_instance:
        raise RuntimeError("Posts manager not initialized")
    return _posts_manager_instance

def get_messages_manager() -> GatorGuidesMessages:
    if not _messages_manager_instance:
        raise RuntimeError("Messages manager not initialized")
    return _messages_manager_instance

def get_search_manager() -> GatorGuidesSearch:
    if not _search_manager_instance:
        raise RuntimeError("Search manager not initialized")
    return _search_manager_instance

def get_availability_manager() -> GatorGuidesAvailability:
    if not _availability_manager_instance:
        raise RuntimeError("Availability manager not initialized")
    return _availability_manager_instance