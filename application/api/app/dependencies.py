from db.Auth import GatorGuidesAuth
from db.Sessions import GatorGuidesSessions

_auth_instance = None
_session_manager_instance = None


def set_auth_instance(instance: GatorGuidesAuth):
    global _auth_instance
    _auth_instance = instance


def set_session_manager_instance(instance: GatorGuidesSessions):
    global _session_manager_instance
    _session_manager_instance = instance


def get_auth_manager() -> GatorGuidesAuth:
    if not _auth_instance:
        raise RuntimeError("Auth manager not initialized")
    return _auth_instance


def get_session_manager() -> GatorGuidesSessions:
    if not _session_manager_instance:
        raise RuntimeError("Session manager not initialized")
    return _session_manager_instance