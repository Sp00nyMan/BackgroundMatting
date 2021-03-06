from enum import Enum

from kivy.utils import platform

class PermissionsManager:
    class RequestStates(Enum):
        UNKNOWN = "UNKNOWN"
        HAVE_PERMISSION = "HAVE_PERMISSION"
        DO_NOT_HAVE_PERMISSION = "DO_NOT_HAVE_PERMISSION"
        AWAITING_REQUEST_RESPONSE = "AWAITING_REQUEST_RESPONSE"

    @staticmethod
    def is_android():
        return platform == 'android'

    @staticmethod
    def check_permissions():
        """
        Android runtime `CAMERA` permission check.
        """
        if not PermissionsManager.is_android():
            return True
        from android.permissions import Permission, check_permission
        return check_permission(Permission.CAMERA) and check_permission(Permission.INTERNET)

    @staticmethod
    def check_request_permissions(callback=None):
        """
        Android runtime `CAMERA` permission check & request.
        """
        had_permission = PermissionsManager.check_permissions()
        if not had_permission:
            from android.permissions import Permission, request_permissions
            permissions = [Permission.CAMERA, Permission.INTERNET]
            request_permissions(permissions, callback)
        return had_permission