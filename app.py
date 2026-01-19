from flask import Flask, jsonify, request, redirect 
from flask_jwt_extended import JWTManager 
from flask_limiter import Limiter 
from flask_limiter.util import get_remote_address 
from flask_mail import Mail 
from flasgger import Swagger 
from config.config import Config 
from db import db 
from models import create_test_users 
from utils.errors import register_error_handlers 
from utils.scheduler import init_scheduler
# Initialize extensions
jwt = JWTManager()
limiter = Limiter(key_func=get_remote_address)
mail = Mail()
scheduler = None

def create_app():
    """
    Application factory for creating Flask app instance.
    """
    app = Flask(__name__)
    
    # LOAD CONFIG FIRST - BEFORE ANYTHING ELSE
    app.config.from_object(Config)
    # DEBUG: Print the keys to verify they loaded
    print(f"[DEBUG] SECRET_KEY: {app.config.get('SECRET_KEY')[:20]}...")
    print(f"[DEBUG] JWT_SECRET_KEY: {app.config.get('JWT_SECRET_KEY')[:20]}...")
    print(f"[DEBUG] JWT_ALGORITHM: {app.config.get('JWT_ALGORITHM')}")
    print(f"[DEBUG] JWT_HEADER_NAME: {app.config.get('JWT_HEADER_NAME')}")
    print(f"[DEBUG] JWT_HEADER_TYPE: {app.config.get('JWT_HEADER_TYPE')}")
    # THEN initialize JWT with config
    jwt.init_app(app)
    
    @jwt.user_identity_loader
    def user_identity_loader(user_id):
        # This converts the user object/id into a serializable format (string)
        return str(user_id)

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
    # This automatically fetches the user from the DB for every request
      from models.user import User
      identity = jwt_data["sub"]
      return User.query.filter_by(id=identity).one_or_none()
    
    # THEN other extensions
    db.init_app(app)
    limiter.init_app(app)
    mail.init_app(app)
    
    # Rest of code...
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
    
    register_error_handlers(app)
    
    @app.errorhandler(429)
    def ratelimit_handler(e):
        return jsonify({
            "error_code": "rate_limit_exceeded",
            "message": "Rate limit exceeded. Too many login attempts.",
            "status": 429
        }), 429
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            "error_code": "token_expired",
            "message": "The access token has expired. Use the refresh token.",
            "status": 401
        }), 401
    
    @jwt.invalid_token_loader
    @jwt.unauthorized_loader
    def invalid_token_callback(error):
        return jsonify({
            "error_code": "invalid_token",
            "message": "Signature verification failed or token is missing.",
            "status": 401
        }), 401
    
    from resources.auth import blp as auth_blp
    from resources.medicines import blp as medicines_blp
    from resources.info import blp as info_blp
    from resources.orthopedic_supplies import blp as orthopedic_supplies_blp
    
    app.register_blueprint(auth_blp)
    app.register_blueprint(medicines_blp)
    app.register_blueprint(info_blp)
    app.register_blueprint(orthopedic_supplies_blp)
    
    global scheduler
    scheduler = init_scheduler(app)
    
    with app.app_context():
        db.create_all()
        create_test_users()
    
    @app.route('/', methods=['GET'])
    def root():
        return redirect('/apidocs')
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)