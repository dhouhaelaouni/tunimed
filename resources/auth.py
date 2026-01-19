from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from models.user import User
from db import db
from datetime import datetime
from utils.enums import UserRole
from utils.audit_logging import log_user_registration, log_user_login
from utils.validation import validate_required_fields, validate_string_field
from decorators.decorators import role_required, any_role_required


# Create auth blueprint
blp = Blueprint('auth', __name__, url_prefix='/auth')

@blp.route('/register', methods=['POST'])
def register():
    """
    Register a new user in the system.
    ---
    tags:
      - Authentication
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - username
            - email
            - password
          properties:
            username:
              type: string
              example: "john_doe"
            email:
              type: string
              format: email
              example: "john@example.com"
            password:
              type: string
              example: "securepassword123"
            role:
              type: string
              enum: ["CITIZEN", "PHARMACIST", "HEALTH_FACILITY", "ADMIN"]
              default: "CITIZEN"
              example: "CITIZEN"
    responses:
      201:
        description: User registered successfully
        schema:
          type: object
          properties:
            msg:
              type: string
            user:
              type: object
      400:
        description: Missing required fields
      409:
        description: User already exists
      500:
        description: Server error
    """
    data = request.get_json()
    
    # Validate required fields
    try:
        validate_required_fields(data, ['username', 'email', 'password'])
    except Exception as e:
        return jsonify({"error_code": "missing_required_fields", "message": str(e), "status": 400}), 400
    
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', UserRole.CITIZEN.value)  # Default role is CITIZEN
    
    # Validate role
    if not UserRole.is_valid(role):
        return jsonify({
            "error_code": "invalid_role",
            "message": f"Invalid role. Must be one of {UserRole.all_roles()}",
            "status": 400
        }), 400
    
    # Check if user already exists
    if User.query.filter_by(username=username).first():
        return jsonify({
            "error_code": "user_exists",
            "message": "Username already exists",
            "status": 409
        }), 409
    
    if User.query.filter_by(email=email).first():
        return jsonify({
            "error_code": "email_exists",
            "message": "Email already exists",
            "status": 409
        }), 409
    
    # Create new user
    try:
        user = User(username=username, email=email, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        # Log user registration
        try:
            log_user_registration(user.id, role)
        except Exception as log_e:
            print(f"Warning: Failed to log user registration: {log_e}")
        
        return jsonify({
            "message": "User registered successfully",
            "user": user.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error_code": "registration_error",
            "message": "Error registering user",
            "status": 500
        }), 500


@blp.route('/login', methods=['POST'])
def login():
    """
    Login with username and password.
    ---
    tags:
      - Authentication
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - username
            - password
          properties:
            username:
              type: string
              example: "john_doe"
            password:
              type: string
              example: "securepassword123"
    responses:
      200:
        description: Login successful
        schema:
          type: object
          properties:
            access_token:
              type: string
            refresh_token:
              type: string
            user:
              type: object
      400:
        description: Missing username or password
      401:
        description: Invalid credentials
      403:
        description: Account inactive
    """
    data = request.get_json()
    
    # Validate required fields
    try:
        validate_required_fields(data, ['username', 'password'])
    except Exception as e:
        return jsonify({"error_code": "missing_required_fields", "message": str(e), "status": 400}), 400
    
    username = data.get('username')
    password = data.get('password')
    
    # Query user by username
    user = User.query.filter_by(username=username).first()
    
    # Verify user exists and password is correct
    if not user or not user.check_password(password):
        return jsonify({
            "error_code": "authentication_failed",
            "message": "Invalid username or password",
            "status": 401
        }), 401
    
    # Check if user is active
    if not user.is_active:
        return jsonify({
            "error_code": "account_inactive",
            "message": "User account is inactive",
            "status": 403
        }), 403
    print("[DEBUG] JWT_SECRET_KEY at login:", current_app.config["JWT_SECRET_KEY"])
    # Create JWT tokens with role claim
    additional_claims = {"role": user.role}
    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)
    
    # Log user login
    try:
        log_user_login(user.id)
    except Exception as log_e:
        print(f"Warning: Failed to log user login: {log_e}")
    
    return jsonify({
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": user.to_dict()
    }), 200


@blp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """
    Refresh access token using a valid refresh token.
    ---
    tags:
      - Authentication
    security:
      - Bearer: []
    responses:
      200:
        description: New access token generated
        schema:
          type: object
          properties:
            access_token:
              type: string
      401:
        description: Invalid or expired refresh token
    """
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or not user.is_active:
        return jsonify({
            "error_code": "user_not_found",
            "message": "User not found or inactive",
            "status": 401
        }), 401
    
    # Create new access token with role claim
    new_access_token = create_access_token(identity=user.id)
    
    return jsonify({
        "access_token": new_access_token
    }), 200


@blp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """
    Get information about the currently authenticated user.
    ---
    tags:
      - Authentication
    security:
      - Bearer: []
    responses:
      200:
        description: Current user information
        schema:
          type: object
          properties:
            user:
              type: object
      404:
        description: User not found
      401:
        description: Missing or invalid token
    """
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({
            "error_code": "user_not_found",
            "message": "User not found",
            "status": 404
        }), 404
    
    return jsonify({
        "user": user.to_dict()
    }), 200