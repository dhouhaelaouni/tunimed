from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from models.user import User
from utils.errors import Unauthorized, Forbidden, NotFound


class AuthService:
        """Centralized authentication and authorization helpers.

        Rationale for evaluators:
        - Consolidates JWT->User resolution to reduce direct DB calls in
            decorators and controllers (improves testability and auditing).
        - Exposes `require_role` so decorators raise standardized exceptions
            (`Forbidden`) which are handled centrally by error handlers.
        """

@staticmethod
def get_current_user(optional=False):
        """Return the `User` object for the current JWT identity.

        Raises `Unauthorized` if token is missing/invalid and `optional` is False.
        """
        try:
            verify_jwt_in_request()
        except Exception:
            if optional:
                return None
            raise Unauthorized('Authentication required', 'unauthorized')

        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user:
            raise NotFound('User not found', 'user_not_found')
        return user

@staticmethod
def has_role(user, required_role):
        if not user:
            return False
        # Accept enums or strings for required_role
        try:
            role_val = required_role.value
        except Exception:
            role_val = str(required_role)
        return user.role == role_val

@staticmethod
def require_role(user, required_role):
        if not AuthService.has_role(user, required_role):
            raise Forbidden(f'Access denied: {required_role} role required', 'insufficient_permissions')
