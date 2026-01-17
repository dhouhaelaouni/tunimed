from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from models.user import User
from utils.enums import UserRole

def role_required(required_role):
    """
    Decorator for Role-Based Access Control (RBAC).
    Verifies if the user has the specified role to access the resource.
    """
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            # Verify JWT token is valid
            verify_jwt_in_request()
            
            # Get current user ID from token
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)
            
            # Check if user exists and has the required role
            if user and user.role == required_role:
                return fn(*args, **kwargs)
            else:
                return jsonify({
                    "error_code": "insufficient_permissions",
                    "message": f"Access denied: {required_role} role required",
                    "status": 403
                }), 403
        return decorator
    return wrapper

def any_role_required(*allowed_roles):
    """
    Decorator for checking if user has ANY of the specified roles.
    Useful when multiple roles can access the same endpoint.
    """
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            # Verify JWT token is valid
            verify_jwt_in_request()
            
            # Get current user ID from token
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)
            
            # Check if user exists and has any of the allowed roles
            if user and user.role in allowed_roles:
                return fn(*args, **kwargs)
            else:
                roles_str = ", ".join(allowed_roles)
                return jsonify({
                    "error_code": "insufficient_permissions",
                    "message": f"Access denied: one of [{roles_str}] role required",
                    "status": 403
                }), 403
        return decorator
    return wrapper

