"""
Centralized error handling module for TuniMed API.
Provides standardized error responses with error codes, messages, and HTTP status codes.
"""

from flask import jsonify
from werkzeug.exceptions import HTTPException


class APIError(Exception):
    """Base exception class for API errors"""
    def __init__(self, message, error_code, status_code=500):
        super().__init__()
        self.message = message
        self.error_code = error_code
        self.status_code = status_code

    def to_dict(self):
        """Convert error to standardized JSON response"""
        return {
            'error_code': self.error_code,
            'message': self.message,
            'status': self.status_code
        }


class BadRequest(APIError):
    """400 Bad Request - Invalid input or validation failed"""
    def __init__(self, message, error_code='bad_request'):
        super().__init__(message, error_code, 400)


class Unauthorized(APIError):
    """401 Unauthorized - Authentication failed or missing"""
    def __init__(self, message, error_code='unauthorized'):
        super().__init__(message, error_code, 401)


class Forbidden(APIError):
    """403 Forbidden - User lacks permission"""
    def __init__(self, message, error_code='forbidden'):
        super().__init__(message, error_code, 403)


class NotFound(APIError):
    """404 Not Found - Resource does not exist"""
    def __init__(self, message, error_code='not_found'):
        super().__init__(message, error_code, 404)


class Conflict(APIError):
    """409 Conflict - Resource already exists or operation violates constraints"""
    def __init__(self, message, error_code='conflict'):
        super().__init__(message, error_code, 409)


class ValidationError(APIError):
    """400 Bad Request - Validation failed with field-level details"""
    def __init__(self, message, error_code='validation_error', fields=None):
        super().__init__(message, error_code, 400)
        self.fields = fields or {}

    def to_dict(self):
        """Convert validation error to standardized JSON response with field details"""
        response = {
            'error_code': self.error_code,
            'message': self.message,
            'status': self.status_code
        }
        if self.fields:
            response['field_errors'] = self.fields
        return response


class InternalServerError(APIError):
    """500 Internal Server Error - Unexpected server error"""
    def __init__(self, message, error_code='internal_error'):
        super().__init__(message, error_code, 500)


def register_error_handlers(app):
    """
    Register all error handlers with the Flask app.
    Should be called during app initialization.
    
    Args:
        app: Flask application instance
    """
    
    @app.errorhandler(APIError)
    def handle_api_error(error):
        """Handle custom API errors"""
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response
    
    @app.errorhandler(400)
    def handle_bad_request(error):
        """Handle 400 Bad Request errors"""
        return jsonify({
            'error_code': 'bad_request',
            'message': 'Invalid request or validation failed',
            'status': 400
        }), 400
    
    @app.errorhandler(401)
    def handle_unauthorized(error):
        """Handle 401 Unauthorized errors"""
        return jsonify({
            'error_code': 'unauthorized',
            'message': 'Authentication required or invalid credentials',
            'status': 401
        }), 401
    
    @app.errorhandler(403)
    def handle_forbidden(error):
        """Handle 403 Forbidden errors"""
        return jsonify({
            'error_code': 'forbidden',
            'message': 'You do not have permission to access this resource',
            'status': 403
        }), 403
    
    @app.errorhandler(404)
    def handle_not_found(error):
        """Handle 404 Not Found errors"""
        return jsonify({
            'error_code': 'not_found',
            'message': 'Resource not found',
            'status': 404
        }), 404
    
    @app.errorhandler(409)
    def handle_conflict(error):
        """Handle 409 Conflict errors"""
        return jsonify({
            'error_code': 'conflict',
            'message': 'Resource already exists or operation violates constraints',
            'status': 409
        }), 409
    
    @app.errorhandler(429)
    def handle_rate_limit(error):
        """Handle 429 Too Many Requests (rate limit exceeded)"""
        return jsonify({
            'error_code': 'SRV_003',
            'message': 'Rate limit exceeded. Please try again later.',
            'status': 429
        }), 429
    
    @app.errorhandler(500)
    def handle_internal_error(error):
        """Handle 500 Internal Server Error"""
        return jsonify({
            'error_code': 'internal_error',
            'message': 'An unexpected server error occurred',
            'status': 500
        }), 500
