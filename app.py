from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_mail import Mail
from flasgger import Swagger

from config.config import Config
from db import db
from models import create_test_users
from utils.errors import register_error_handlers
from utils.enums import UserRole
from utils.scheduler import init_scheduler

# Initialize extensions
jwt = JWTManager()
limiter = Limiter(key_func=get_remote_address)
mail = Mail()
scheduler = None

def create_app():
    """
    Application factory for creating Flask app instance.
    Initializes all extensions, blueprints, and error handlers.
    """
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    limiter.init_app(app)
    mail.init_app(app)
    
    # Initialize Swagger/Flasgger
    swagger = Swagger(app, template={
        "swagger": "2.0",
        "info": {
            "title": "TuniMed API",
            "description": "A complete REST API for managing medicine waste reduction and controlled redistribution in Tunisia",
            "version": "1.0.0",
            "contact": {
                "name": "TuniMed Support",
                "url": "https://github.com/yourusername/tunimed"
            }
        },
        "basePath": "/",
        "schemes": ["http", "https"],
        "securityDefinitions": {
            "Bearer": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "JWT Authorization header using the Bearer scheme. Example: 'Bearer {token}'"
            }
        }
    })
    
    # --- Register Error Handlers ---
    register_error_handlers(app)
    
    # --- JWT Error Handlers ---
    
    @app.errorhandler(429)
    def ratelimit_handler(e):
        """Handle rate limit exceeded errors"""
        return jsonify({
            "error_code": "rate_limit_exceeded",
            "message": "Rate limit exceeded. Too many login attempts.",
            "status": 429
        }), 429
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        """Handle expired JWT tokens"""
        return jsonify({
            "error_code": "token_expired",
            "message": "The access token has expired. Use the refresh token.",
            "status": 401
        }), 401
    
    @jwt.invalid_token_loader
    @jwt.unauthorized_loader
    def invalid_token_callback(error):
        """Handle invalid or missing JWT tokens"""
        return jsonify({
            "error_code": "invalid_token",
            "message": "Signature verification failed or token is missing.",
            "status": 401
        }), 401
    
    # --- Register Blueprints ---
    
    from resources.auth import blp as auth_blp
    from resources.medicines import blp as medicines_blp
    from resources.info import blp as info_blp
    from resources.orthopedic_supplies import blp as orthopedic_supplies_blp
    
    app.register_blueprint(auth_blp)
    app.register_blueprint(medicines_blp)
    app.register_blueprint(info_blp)
    app.register_blueprint(orthopedic_supplies_blp)
    
    # --- Initialize Scheduler ---
    global scheduler
    scheduler = init_scheduler(app)
    
    # --- Root Endpoint - Redirect to Swagger Documentation ---
    @app.route('/', methods=['GET'])
    def root():
        """Root endpoint - Redirect to Swagger UI"""
        from flask import redirect
        return redirect('/apidocs')
    
    return app


# Create app instance at module level
app = create_app()


if __name__ == '__main__':
    # Create database tables and test users
    with app.app_context():
        db.create_all()
        create_test_users()
    
    # Run Flask development server
    # Set debug=False in production
    app.run(debug=False, host='0.0.0.0', port=5000)

