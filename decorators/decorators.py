from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity

def role_required(required_role):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()

            # 🔑 IMPORT HERE (avoids circular import)
            from models.user import User

            user_id = get_jwt_identity()
            user = User.query.get(user_id)

            if not user or not user.is_active:
                return jsonify({"msg": "Unauthorized"}), 401

            # 🛠️ FIX: Safely handle both Enum objects and Strings
            # This prevents the "AttributeError: 'str' object has no attribute 'value'"
            role_val = required_role.value if hasattr(required_role, 'value') else required_role

            if user.role != role_val:
                return jsonify({
                    "msg": "Forbidden", 
                    "error": f"Requires {role_val} role"
                }), 403

            return fn(*args, **kwargs)
        return wrapper
    return decorator


def any_role_required(*roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()

            # 🔑 IMPORT HERE (avoids circular import)
            from models.user import User

            user_id = get_jwt_identity()
            user = User.query.get(user_id)

            if not user or not user.is_active:
                return jsonify({"msg": "Unauthorized"}), 401

            # 🛠️ FIX: Convert all passed roles to strings, handling Enums safely
            allowed_roles = [role.value if hasattr(role, 'value') else role for role in roles]

            if user.role not in allowed_roles:
                return jsonify({
                    "msg": "Forbidden", 
                    "error": f"Requires one of: {', '.join(allowed_roles)}"
                }), 403

            return fn(*args, **kwargs)
        return wrapper
    return decorator