"""
Error Catalog for TuniMed API
Defines all standardized error codes and their meanings.
"""

# ============================================================
# AUTHENTICATION & AUTHORIZATION ERRORS (AUTH_*)
# ============================================================

AUTH_001 = {
    'code': 'AUTH_001',
    'message': 'Invalid or missing authentication token',
    'status': 401,
    'category': 'Authentication'
}

AUTH_002 = {
    'code': 'AUTH_002',
    'message': 'Token has expired',
    'status': 401,
    'category': 'Authentication'
}

AUTH_003 = {
    'code': 'AUTH_003',
    'message': 'Insufficient permissions for this operation',
    'status': 403,
    'category': 'Authorization'
}

AUTH_004 = {
    'code': 'AUTH_004',
    'message': 'Invalid credentials provided',
    'status': 401,
    'category': 'Authentication'
}

AUTH_005 = {
    'code': 'AUTH_005',
    'message': 'User account is inactive',
    'status': 403,
    'category': 'Authorization'
}

AUTH_006 = {
    'code': 'AUTH_006',
    'message': 'Required role not assigned',
    'status': 403,
    'category': 'Authorization'
}

# ============================================================
# MEDICINE REFERENCE ERRORS (MED_*)
# ============================================================

MED_001 = {
    'code': 'MED_001',
    'message': 'Medicine reference not found',
    'status': 404,
    'category': 'Medicine Reference'
}

MED_002 = {
    'code': 'MED_002',
    'message': 'Medicine with same name, form, and dosage already exists',
    'status': 409,
    'category': 'Medicine Reference'
}

MED_003 = {
    'code': 'MED_003',
    'message': 'Invalid medicine status transition',
    'status': 400,
    'category': 'Medicine Workflow'
}

MED_004 = {
    'code': 'MED_004',
    'message': 'Medicine declaration not found',
    'status': 404,
    'category': 'Medicine Declaration'
}

MED_005 = {
    'code': 'MED_005',
    'message': 'Only declaration owner can cancel',
    'status': 403,
    'category': 'Medicine Declaration'
}

MED_006 = {
    'code': 'MED_006',
    'message': 'Invalid status value for medicine',
    'status': 400,
    'category': 'Medicine Reference'
}

MED_007 = {
    'code': 'MED_007',
    'message': 'Cannot verify medicine: requires pharmacy verification first',
    'status': 400,
    'category': 'Medicine Workflow'
}

MED_008 = {
    'code': 'MED_008',
    'message': 'Medicine proposition not found',
    'status': 404,
    'category': 'Medicine Proposition'
}

# ============================================================
# ORTHOPEDIC SUPPLY ERRORS (SUP_*)
# ============================================================

SUP_001 = {
    'code': 'SUP_001',
    'message': 'Orthopedic supply not found',
    'status': 404,
    'category': 'Orthopedic Supply'
}

SUP_002 = {
    'code': 'SUP_002',
    'message': 'Only supply owner or admin can modify this supply',
    'status': 403,
    'category': 'Orthopedic Supply'
}

SUP_003 = {
    'code': 'SUP_003',
    'message': 'Invalid condition value for supply',
    'status': 400,
    'category': 'Orthopedic Supply'
}

SUP_004 = {
    'code': 'SUP_004',
    'message': 'Quantity must be positive integer',
    'status': 400,
    'category': 'Orthopedic Supply'
}

SUP_005 = {
    'code': 'SUP_005',
    'message': 'Price required when supply is marked for sale',
    'status': 400,
    'category': 'Orthopedic Supply'
}

SUP_006 = {
    'code': 'SUP_006',
    'message': 'Price must be positive when set',
    'status': 400,
    'category': 'Orthopedic Supply'
}

SUP_007 = {
    'code': 'SUP_007',
    'message': 'Supply is no longer active',
    'status': 400,
    'category': 'Orthopedic Supply'
}

# ============================================================
# VALIDATION ERRORS (VAL_*)
# ============================================================

VAL_001 = {
    'code': 'VAL_001',
    'message': 'Missing required field',
    'status': 400,
    'category': 'Validation'
}

VAL_002 = {
    'code': 'VAL_002',
    'message': 'Invalid field format or type',
    'status': 400,
    'category': 'Validation'
}

VAL_003 = {
    'code': 'VAL_003',
    'message': 'Field validation failed',
    'status': 400,
    'category': 'Validation'
}

VAL_004 = {
    'code': 'VAL_004',
    'message': 'Invalid query parameter',
    'status': 400,
    'category': 'Validation'
}

VAL_005 = {
    'code': 'VAL_005',
    'message': 'Invalid enum value',
    'status': 400,
    'category': 'Validation'
}

VAL_006 = {
    'code': 'VAL_006',
    'message': 'Date parsing error',
    'status': 400,
    'category': 'Validation'
}

# ============================================================
# USER ERRORS (USR_*)
# ============================================================

USR_001 = {
    'code': 'USR_001',
    'message': 'User not found',
    'status': 404,
    'category': 'User'
}

USR_002 = {
    'code': 'USR_002',
    'message': 'Username or email already exists',
    'status': 409,
    'category': 'User'
}

USR_003 = {
    'code': 'USR_003',
    'message': 'Invalid user role',
    'status': 400,
    'category': 'User'
}

# ============================================================
# CONFLICT ERRORS (CON_*)
# ============================================================

CON_001 = {
    'code': 'CON_001',
    'message': 'Resource already exists',
    'status': 409,
    'category': 'Conflict'
}

CON_002 = {
    'code': 'CON_002',
    'message': 'Operation violates data constraints',
    'status': 409,
    'category': 'Conflict'
}

# ============================================================
# SERVER ERRORS (SRV_*)
# ============================================================

SRV_001 = {
    'code': 'SRV_001',
    'message': 'Internal server error',
    'status': 500,
    'category': 'Server'
}

SRV_002 = {
    'code': 'SRV_002',
    'message': 'Database operation failed',
    'status': 500,
    'category': 'Server'
}

SRV_003 = {
    'code': 'SRV_003',
    'message': 'Rate limit exceeded',
    'status': 429,
    'category': 'Rate Limiting'
}

# ============================================================
# CATALOG LOOKUP
# ============================================================

ERROR_CATALOG = {
    # Auth
    'AUTH_001': AUTH_001,
    'AUTH_002': AUTH_002,
    'AUTH_003': AUTH_003,
    'AUTH_004': AUTH_004,
    'AUTH_005': AUTH_005,
    'AUTH_006': AUTH_006,
    # Medicine
    'MED_001': MED_001,
    'MED_002': MED_002,
    'MED_003': MED_003,
    'MED_004': MED_004,
    'MED_005': MED_005,
    'MED_006': MED_006,
    'MED_007': MED_007,
    'MED_008': MED_008,
    # Supply
    'SUP_001': SUP_001,
    'SUP_002': SUP_002,
    'SUP_003': SUP_003,
    'SUP_004': SUP_004,
    'SUP_005': SUP_005,
    'SUP_006': SUP_006,
    'SUP_007': SUP_007,
    # Validation
    'VAL_001': VAL_001,
    'VAL_002': VAL_002,
    'VAL_003': VAL_003,
    'VAL_004': VAL_004,
    'VAL_005': VAL_005,
    'VAL_006': VAL_006,
    # User
    'USR_001': USR_001,
    'USR_002': USR_002,
    'USR_003': USR_003,
    # Conflict
    'CON_001': CON_001,
    'CON_002': CON_002,
    # Server
    'SRV_001': SRV_001,
    'SRV_002': SRV_002,
    'SRV_003': SRV_003,
}


def get_error_details(error_code):
    """
    Retrieve error details by error code.
    
    Args:
        error_code (str): Error code (e.g., 'AUTH_001')
    
    Returns:
        dict: Error details with code, message, status, category
    """
    return ERROR_CATALOG.get(error_code, {
        'code': 'UNKNOWN_ERROR',
        'message': 'Unknown error occurred',
        'status': 500,
        'category': 'Unknown'
    })


def list_all_errors():
    """
    List all available error codes organized by category.
    
    Returns:
        dict: Errors grouped by category
    """
    categories = {}
    for code, error in ERROR_CATALOG.items():
        category = error.get('category', 'Unknown')
        if category not in categories:
            categories[category] = []
        categories[category].append(error)
    return categories
