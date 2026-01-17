"""
API Response Examples - Before & After Implementation

This document shows the standardized error response format used throughout
the TuniMed API after implementing all 5 prompts.
"""

# ═══════════════════════════════════════════════════════════════════════════════
# STANDARDIZED ERROR RESPONSE FORMAT
# ═══════════════════════════════════════════════════════════════════════════════

STANDARD_ERROR_FORMAT = {
    "error_code": "string - machine-readable error identifier",
    "message": "string - human-readable error description",
    "status": "integer - HTTP status code"
}

# ═══════════════════════════════════════════════════════════════════════════════
# EXAMPLE RESPONSES BY ENDPOINT
# ═══════════════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────────────
# AUTHENTICATION ENDPOINTS
# ─────────────────────────────────────────────────────────────────────────────

"""
POST /auth/register
"""

# ✓ SUCCESS (201 Created)
REGISTER_SUCCESS = {
    "message": "User registered successfully",
    "user": {
        "id": 1,
        "username": "john_doe",
        "email": "john@example.com",
        "role": "CITIZEN",
        "is_active": True,
        "created_at": "2025-01-16T10:30:00"
    }
}

# ✗ ERROR: Missing required fields (400)
REGISTER_MISSING_FIELDS = {
    "error_code": "missing_required_fields",
    "message": "Missing required fields: password",
    "status": 400
}

# ✗ ERROR: Invalid role (400)
REGISTER_INVALID_ROLE = {
    "error_code": "invalid_role",
    "message": "Invalid role. Must be one of ['CITIZEN', 'PHARMACIST', 'REGULATORY_AGENT', 'HEALTH_FACILITY', 'ADMIN']",
    "status": 400
}

# ✗ ERROR: Username exists (409)
REGISTER_DUPLICATE_USER = {
    "error_code": "user_exists",
    "message": "Username already exists",
    "status": 409
}

"""
POST /auth/login
"""

# ✓ SUCCESS (200 OK)
LOGIN_SUCCESS = {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
        "id": 1,
        "username": "john_doe",
        "email": "john@example.com",
        "role": "CITIZEN",
        "is_active": True,
        "created_at": "2025-01-16T10:30:00"
    }
}

# ✗ ERROR: Invalid credentials (401)
LOGIN_INVALID_CREDENTIALS = {
    "error_code": "authentication_failed",
    "message": "Invalid username or password",
    "status": 401
}

# ✗ ERROR: Account inactive (403)
LOGIN_ACCOUNT_INACTIVE = {
    "error_code": "account_inactive",
    "message": "User account is inactive",
    "status": 403
}

# ─────────────────────────────────────────────────────────────────────────────
# MEDICINE DECLARATION ENDPOINTS
# ─────────────────────────────────────────────────────────────────────────────

"""
POST /medicines/declarations
"""

# ✓ SUCCESS (201 Created)
DECLARE_MEDICINE_SUCCESS = {
    "message": "Medicine declared successfully",
    "medicine": {
        "id": 5,
        "name": "Aspirin",
        "amm": "AMM12345",
        "batch_number": "BATCH001",
        "expiration_date": "2025-12-31T00:00:00",
        "quantity": 10,
        "is_imported": False,
        "country_of_origin": None,
        "status": "SUBMITTED",
        "is_expired": False,
        "can_be_redistributed": False,
        "created_at": "2025-01-16T10:35:00",
        "updated_at": "2025-01-16T10:35:00"
    }
}

# ✗ ERROR: Missing required fields (400)
DECLARE_MISSING_FIELDS = {
    "error_code": "missing_required_fields",
    "message": "Missing required fields: batch_number, quantity",
    "status": 400
}

# ✗ ERROR: Invalid string length (400)
DECLARE_STRING_TOO_LONG = {
    "error_code": "string_too_long",
    "message": "name must be at most 200 character(s)",
    "status": 400
}

# ✗ ERROR: Invalid date format (400)
DECLARE_INVALID_DATE = {
    "error_code": "invalid_iso_date_format",
    "message": "expiration_date must be in ISO format (YYYY-MM-DD or ISO 8601)",
    "status": 400
}

# ✗ ERROR: Expired date (400)
DECLARE_EXPIRED_DATE = {
    "error_code": "expired_date",
    "message": "expiration_date has already passed. Cannot declare expired items.",
    "status": 400
}

# ✗ ERROR: Invalid quantity type (400)
DECLARE_INVALID_QUANTITY_TYPE = {
    "error_code": "invalid_integer_type",
    "message": "quantity must be an integer",
    "status": 400
}

# ✗ ERROR: Quantity too low (400)
DECLARE_QUANTITY_BELOW_MINIMUM = {
    "error_code": "integer_below_minimum",
    "message": "quantity must be at least 1",
    "status": 400
}

# ✗ ERROR: No authentication (401)
DECLARE_NO_AUTH = {
    "error_code": "invalid_token",
    "message": "Signature verification failed or token is missing.",
    "status": 401
}

# ✗ ERROR: Wrong role (403)
DECLARE_WRONG_ROLE = {
    "error_code": "insufficient_permissions",
    "message": "Access denied: CITIZEN role required",
    "status": 403
}

"""
GET /medicines/declarations/my
"""

# ✓ SUCCESS (200 OK)
GET_MY_DECLARATIONS = {
    "medicines": [
        {
            "id": 1,
            "name": "Aspirin",
            "amm": "AMM12345",
            "batch_number": "BATCH001",
            "expiration_date": "2025-12-31T00:00:00",
            "quantity": 10,
            "is_imported": False,
            "country_of_origin": None,
            "status": "SUBMITTED",
            "is_expired": False,
            "can_be_redistributed": False,
            "created_at": "2025-01-16T10:35:00",
            "updated_at": "2025-01-16T10:35:00"
        },
        {
            "id": 2,
            "name": "Ibuprofen",
            "amm": "AMM54321",
            "batch_number": "BATCH002",
            "expiration_date": "2025-06-30T00:00:00",
            "quantity": 20,
            "is_imported": False,
            "country_of_origin": None,
            "status": "PHARMACY_VERIFIED",
            "is_expired": False,
            "can_be_redistributed": False,
            "created_at": "2025-01-15T14:20:00",
            "updated_at": "2025-01-16T09:15:00"
        }
    ],
    "count": 2
}

# ─────────────────────────────────────────────────────────────────────────────
# PHARMACY VERIFICATION ENDPOINTS
# ─────────────────────────────────────────────────────────────────────────────

"""
POST /medicines/verify/<medicine_id>
"""

# ✓ SUCCESS: Medicine approved (200 OK)
VERIFY_MEDICINE_APPROVED = {
    "message": "Medicine approved by pharmacy",
    "medicine": {
        "id": 5,
        "name": "Aspirin",
        "amm": "AMM12345",
        "batch_number": "BATCH001",
        "expiration_date": "2025-12-31T00:00:00",
        "quantity": 10,
        "is_imported": False,
        "country_of_origin": None,
        "status": "PHARMACY_VERIFIED",
        "is_expired": False,
        "can_be_redistributed": False,
        "created_at": "2025-01-16T10:35:00",
        "updated_at": "2025-01-16T10:35:00",
        "safety_rating": 95,
        "pharmacy_notes": "Packaging intact, authenticity verified",
        "regulatory_notes": None,
        "is_recalled": False
    }
}

# ✓ SUCCESS: Medicine rejected (200 OK)
VERIFY_MEDICINE_REJECTED = {
    "message": "Medicine rejected by pharmacy",
    "medicine": {
        "id": 5,
        "name": "Aspirin",
        "status": "PHARMACY_REJECTED",
        "pharmacy_notes": "Damaged packaging detected"
    }
}

# ✗ ERROR: Medicine not found (404)
VERIFY_MEDICINE_NOT_FOUND = {
    "error_code": "not_found",
    "message": "Medicine not found",
    "status": 404
}

# ✗ ERROR: Invalid medicine status (400)
VERIFY_INVALID_STATUS = {
    "error_code": "invalid_status",
    "message": "Cannot verify medicine with status: PHARMACY_VERIFIED",
    "status": 400
}

# ─────────────────────────────────────────────────────────────────────────────
# REGULATORY VALIDATION ENDPOINTS
# ─────────────────────────────────────────────────────────────────────────────

"""
POST /medicines/validate/<medicine_id>
"""

# ✓ SUCCESS: Medicine approved (200 OK)
VALIDATE_MEDICINE_APPROVED = {
    "message": "Medicine regulatory validation completed: APPROVED",
    "medicine": {
        "id": 5,
        "name": "Aspirin",
        "status": "APPROVED_FOR_REDISTRIBUTION",
        "regulatory_notes": "All safety checks passed. Approved for redistribution.",
        "regulatory_validated_at": "2025-01-16T11:00:00",
        "regulatory_validated_by": 3
    }
}

# ✓ SUCCESS: Medicine restricted (200 OK)
VALIDATE_MEDICINE_RESTRICTED = {
    "message": "Medicine regulatory validation completed: RESTRICTED",
    "medicine": {
        "id": 5,
        "name": "Aspirin",
        "status": "RESTRICTED_USE",
        "regulatory_notes": "Can only be used in clinical settings with supervision."
    }
}

# ✗ ERROR: Invalid decision (400)
VALIDATE_INVALID_DECISION = {
    "error_code": "invalid_decision",
    "message": "Invalid decision. Must be one of ['APPROVED', 'RESTRICTED', 'REJECTED']",
    "status": 400
}

# ─────────────────────────────────────────────────────────────────────────────
# ERROR HANDLING EXAMPLES
# ─────────────────────────────────────────────────────────────────────────────

"""
HTTP Status Code 400 - Bad Request
"""
ERROR_400_INVALID_INPUT = {
    "error_code": "invalid_integer_type",
    "message": "quantity must be an integer",
    "status": 400
}

"""
HTTP Status Code 401 - Unauthorized
"""
ERROR_401_MISSING_TOKEN = {
    "error_code": "invalid_token",
    "message": "Signature verification failed or token is missing.",
    "status": 401
}

ERROR_401_EXPIRED_TOKEN = {
    "error_code": "token_expired",
    "message": "The access token has expired. Use the refresh token.",
    "status": 401
}

"""
HTTP Status Code 403 - Forbidden
"""
ERROR_403_INSUFFICIENT_PERMISSIONS = {
    "error_code": "insufficient_permissions",
    "message": "Access denied: PHARMACIST role required",
    "status": 403
}

"""
HTTP Status Code 404 - Not Found
"""
ERROR_404_NOT_FOUND = {
    "error_code": "not_found",
    "message": "Resource not found",
    "status": 404
}

"""
HTTP Status Code 500 - Internal Server Error
"""
ERROR_500_INTERNAL_ERROR = {
    "error_code": "internal_error",
    "message": "An unexpected server error occurred",
    "status": 500
}

# ═══════════════════════════════════════════════════════════════════════════════
# AUDIT LOG EXAMPLES
# ═══════════════════════════════════════════════════════════════════════════════

AUDIT_LOG_ENTRY = {
    "id": 1,
    "user_id": 5,
    "action": "MEDICINE_DECLARED",
    "entity_type": "MEDICINE",
    "entity_id": 10,
    "details": {
        "medicine_name": "Aspirin",
        "is_imported": False
    },
    "created_at": "2025-01-16T10:35:00"
}

AUDIT_LOG_USER_LOGIN = {
    "id": 2,
    "user_id": 5,
    "action": "LOGIN",
    "entity_type": "USER",
    "entity_id": 5,
    "details": {
        "timestamp": "2025-01-16T10:35:00"
    },
    "created_at": "2025-01-16T10:35:00"
}

AUDIT_LOG_MEDICINE_VERIFICATION = {
    "id": 3,
    "user_id": 3,
    "action": "MEDICINE_VERIFIED",
    "entity_type": "MEDICINE",
    "entity_id": 10,
    "details": {
        "verified": True,
        "notes": "Packaging intact, authenticity verified"
    },
    "created_at": "2025-01-16T10:40:00"
}

AUDIT_LOG_MEDICINE_APPROVAL = {
    "id": 4,
    "user_id": 2,
    "action": "MEDICINE_APPROVED",
    "entity_type": "MEDICINE",
    "entity_id": 10,
    "details": {
        "approved": True,
        "decision": "APPROVED",
        "notes": "All safety checks passed. Approved for redistribution."
    },
    "created_at": "2025-01-16T10:45:00"
}

# ═══════════════════════════════════════════════════════════════════════════════
# TESTING WITH CURL EXAMPLES
# ═══════════════════════════════════════════════════════════════════════════════

"""
# Test successful registration
curl -X POST http://localhost:5000/auth/register \\
  -H "Content-Type: application/json" \\
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "securepass123",
    "role": "CITIZEN"
  }'

# Test missing required field (will return 400)
curl -X POST http://localhost:5000/auth/register \\
  -H "Content-Type: application/json" \\
  -d '{
    "username": "john_doe",
    "email": "john@example.com"
  }'

# Test login
curl -X POST http://localhost:5000/auth/login \\
  -H "Content-Type: application/json" \\
  -d '{
    "username": "john_doe",
    "password": "securepass123"
  }'

# Test medicine declaration (requires valid token)
TOKEN="<your_access_token_here>"
curl -X POST http://localhost:5000/medicines/declarations \\
  -H "Authorization: Bearer $TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{
    "name": "Aspirin",
    "amm": "AMM12345",
    "batch_number": "BATCH001",
    "expiration_date": "2025-12-31T00:00:00",
    "quantity": 10,
    "is_imported": false
  }'

# Test with invalid quantity (will return 400)
curl -X POST http://localhost:5000/medicines/declarations \\
  -H "Authorization: Bearer $TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{
    "name": "Aspirin",
    "amm": "AMM12345",
    "batch_number": "BATCH001",
    "expiration_date": "2025-12-31T00:00:00",
    "quantity": "not_a_number"
  }'
"""

# ═══════════════════════════════════════════════════════════════════════════════
# KEY CHANGES FROM OLD RESPONSE FORMAT
# ═══════════════════════════════════════════════════════════════════════════════

"""
BEFORE:
  {
    "msg": "Invalid role",
    "code": "invalid_role"
  }

AFTER:
  {
    "error_code": "invalid_role",
    "message": "Invalid role. Must be one of [...]",
    "status": 400
  }

BENEFITS:
✓ Consistent field names (error_code, message, status)
✓ HTTP status code included in response
✓ More descriptive error messages
✓ Machine-readable error codes for client-side handling
✓ Human-readable messages for debugging
✓ Consistent across all endpoints
"""
