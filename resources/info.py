from flask import Blueprint, jsonify

# Create info blueprint
blp = Blueprint('info', __name__, url_prefix='/info')


@blp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint to verify API availability.
    ---
    tags:
      - Health
    responses:
      200:
        description: API is running
        schema:
          type: object
          properties:
            status:
              type: string
            message:
              type: string
    """
    return jsonify({
        "status": "healthy",
        "message": "TuniMed API is running"
    }), 200


@blp.route('/import-rules', methods=['GET'])
def get_import_rules():
    """
    Get information about import regulations and restrictions.
    ---
    tags:
      - Information
    responses:
      200:
        description: Import regulations and restrictions
        schema:
          type: object
          properties:
            title:
              type: string
            description:
              type: string
            rules:
              type: array
              items:
                type: object
    """
    rules = {
        "title": "Import Regulations for Medicine Redistribution",
        "description": "Tunisia's medicine reuse program prioritizes locally-regulated medicines",
        "rules": [
            {
                "id": 1,
                "title": "Local Medicines Only",
                "description": "Only medicines manufactured locally or imported and approved by ANMPS can be redistributed",
                "restriction": "AUTOMATIC_BLOCK",
                "enforcement": "Checked at medicine declaration and regulatory validation stages"
            },
            {
                "id": 2,
                "title": "Valid AMM Required",
                "description": "Medicine must have a valid Autorisation de Mise sur le Marché (Market Authorization)",
                "restriction": "VALIDATION_REQUIRED",
                "enforcement": "Checked during regulatory validation"
            },
            {
                "id": 3,
                "title": "No Expiration",
                "description": "Expired medicines cannot be declared or redistributed",
                "restriction": "AUTOMATIC_BLOCK",
                "enforcement": "Checked at submission and eligibility verification"
            },
            {
                "id": 4,
                "title": "No Recalled Medicines",
                "description": "Medicines recalled by ANMPS or manufacturers cannot be redistributed",
                "restriction": "REGULATORY_BLOCK",
                "enforcement": "Checked during regulatory validation"
            }
        ]
    }
    
    return jsonify(rules), 200


@blp.route('/redistribution-options', methods=['GET'])
def get_redistribution_options():
    """
    Get information about redistribution choices and recipient types.
    ---
    tags:
      - Information
    responses:
      200:
        description: Redistribution options and recipient types
        schema:
          type: object
          properties:
            title:
              type: string
            description:
              type: string
            recipient_types:
              type: array
              items:
                type: object
            distribution_workflow:
              type: object
    """
    options = {
        "title": "Redistribution Options",
        "description": "Approved medicines can be distributed to qualified health facilities",
        "recipient_types": [
            {
                "id": 1,
                "type": "PUBLIC_HEALTH_FACILITY",
                "description": "Government-run hospitals, clinics, and health centers",
                "requirements": ["Valid health facility license", "Registered with ANMPS", "Storage compliance"]
            },
            {
                "id": 2,
                "type": "NGO_CLINIC",
                "description": "Non-governmental organization providing healthcare services",
                "requirements": ["NGO registration certificate", "Health facility license", "Storage compliance"]
            },
            {
                "id": 3,
                "type": "RESEARCH_INSTITUTION",
                "description": "Medical research and pharmaceutical development institutions",
                "requirements": ["Research authorization", "ANMPS approval", "Secure storage"]
            }
        ],
        "distribution_workflow": {
            "step_1": "Health facility requests approved medicines",
            "step_2": "Medicine owner confirms availability",
            "step_3": "Transfer documentation prepared",
            "step_4": "Delivery and receipt documented",
            "step_5": "Usage tracked for audit trail"
        }
    }
    
    return jsonify(options), 200


@blp.route('/workflow-statuses', methods=['GET'])
def get_workflow_statuses():
    """
    Get descriptions of all medicine workflow statuses.
    ---
    tags:
      - Information
    responses:
      200:
        description: Workflow statuses for medicine declarations
        schema:
          type: object
          properties:
            title:
              type: string
            statuses:
              type: array
              items:
                type: object
    """
    statuses = {
        "title": "Medicine Declaration Workflow Statuses",
        "statuses": [
            {
                "code": "SUBMITTED",
                "description": "Medicine declared by citizen, awaiting pharmacy verification",
                "role": "CITIZEN",
                "next_step": "Pharmacist verification"
            },
            {
                "code": "PHARMACY_VERIFIED",
                "description": "Pharmacist verified packaging and authenticity, awaiting regulatory validation",
                "role": "PHARMACIST",
                "next_step": "Regulatory agent validation"
            },
            {
                "code": "PHARMACY_REJECTED",
                "description": "Pharmacist rejected medicine due to packaging or authenticity issues",
                "role": "PHARMACIST",
                "next_step": "End of workflow - cannot redistribute"
            },
            {
                "code": "APPROVED_FOR_REDISTRIBUTION",
                "description": "Medicine approved by regulatory agent for safe redistribution",
                "role": "REGULATORY_AGENT",
                "next_step": "Available for health facilities to request"
            },
            {
                "code": "RESTRICTED_USE",
                "description": "Medicine approved with restrictions (specific facilities or conditions)",
                "role": "REGULATORY_AGENT",
                "next_step": "Available with usage restrictions"
            },
            {
                "code": "REJECTED_REGULATORY",
                "description": "Regulatory agent rejected medicine for safety or compliance reasons",
                "role": "REGULATORY_AGENT",
                "next_step": "End of workflow - cannot redistribute"
            },
            {
                "code": "DISTRIBUTED",
                "description": "Medicine successfully distributed to approved health facility",
                "role": "SYSTEM",
                "next_step": "Usage tracking and audit"
            }
        ]
    }
    
    return jsonify(statuses), 200


@blp.route('/error-catalog', methods=['GET'])
def get_error_catalog():
    """
    Get comprehensive error codes and messages used by the API.
    """
    errors = {
        "title": "TuniMed API Error Catalog",
        "errors": {
            "authentication": [
                {
                    "code": "authentication_failed",
                    "http_status": 401,
                    "message": "Invalid username or password",
                    "resolution": "Verify credentials and try again"
                },
                {
                    "code": "token_expired",
                    "http_status": 401,
                    "message": "The access token has expired",
                    "resolution": "Use refresh token to obtain new access token"
                },
                {
                    "code": "invalid_token",
                    "http_status": 401,
                    "message": "Signature verification failed or token is missing",
                    "resolution": "Provide valid JWT token in Authorization header"
                }
            ],
            "authorization": [
                {
                    "code": "insufficient_permissions",
                    "http_status": 403,
                    "message": "User does not have required role for this action",
                    "resolution": "Contact administrator to update user role"
                },
                {
                    "code": "account_inactive",
                    "http_status": 403,
                    "message": "User account is inactive",
                    "resolution": "Contact administrator to activate account"
                }
            ],
            "validation": [
                {
                    "code": "invalid_input",
                    "http_status": 400,
                    "message": "Request data validation failed",
                    "resolution": "Check required fields and data types"
                },
                {
                    "code": "invalid_date",
                    "http_status": 400,
                    "message": "Date format is invalid",
                    "resolution": "Use ISO format: YYYY-MM-DD"
                },
                {
                    "code": "expired_medicine",
                    "http_status": 400,
                    "message": "Cannot declare expired medicines",
                    "resolution": "Only declare medicines with future expiration dates"
                }
            ],
            "resource": [
                {
                    "code": "not_found",
                    "http_status": 404,
                    "message": "Resource not found",
                    "resolution": "Verify resource ID and try again"
                },
                {
                    "code": "user_exists",
                    "http_status": 409,
                    "message": "Username already exists",
                    "resolution": "Choose a different username"
                },
                {
                    "code": "email_exists",
                    "http_status": 409,
                    "message": "Email already exists",
                    "resolution": "Use a different email address"
                }
            ],
            "business": [
                {
                    "code": "invalid_status",
                    "http_status": 400,
                    "message": "Cannot perform this action on medicine with current status",
                    "resolution": "Check medicine status and appropriate action"
                },
                {
                    "code": "forbidden",
                    "http_status": 403,
                    "message": "Access denied to this resource",
                    "resolution": "Verify your permissions"
                }
            ]
        }
    }
    
    return jsonify(errors), 200
