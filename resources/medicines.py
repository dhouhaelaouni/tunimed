from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from models.user import User, Medicine, AuditLog
from decorators.decorators import role_required, any_role_required
from db import db

# Create medicines blueprint
blp = Blueprint('medicines', __name__, url_prefix='/medicines')

# ============ HELPER FUNCTIONS ============

def log_audit(user_id, action, entity_type, entity_id, details=None):
    """Helper function to create audit log entries"""
    audit_log = AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details
    )
    db.session.add(audit_log)
    db.session.commit()


# ============ MEDICINE DECLARATION ENDPOINTS ============

@blp.route('/declarations', methods=['POST'])
@jwt_required()
@role_required('CITIZEN')
def declare_medicine():
    """
    CITIZEN: Declare a new medicine for reuse/redistribution.
    ---
    tags:
      - Medicine Declarations
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - name
            - amm
            - batch_number
            - expiration_date
            - quantity
          properties:
            name:
              type: string
              example: "Aspirin"
            amm:
              type: string
              example: "AMM12345"
            batch_number:
              type: string
              example: "BATCH001"
            expiration_date:
              type: string
              format: date
              example: "2024-12-31"
            quantity:
              type: integer
              example: 10
            is_imported:
              type: boolean
              example: false
            country_of_origin:
              type: string
    responses:
      201:
        description: Medicine declared successfully
      400:
        description: Invalid input or expired medicine
      401:
        description: Missing or invalid token
      403:
        description: Insufficient permissions
    """
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['name', 'amm', 'batch_number', 'expiration_date', 'quantity']
    if not data or not all(k in data for k in required_fields):
        return jsonify({"msg": "Missing required fields", "code": "invalid_input"}), 400
    
    try:
        # Parse expiration date
        expiration_date = datetime.fromisoformat(data.get('expiration_date'))
        
        # Check if medicine is already expired
        if datetime.utcnow() > expiration_date:
            log_audit(current_user_id, 'MEDICINE_DECLARATION_REJECTED', 'MEDICINE', None, 
                     {'reason': 'expired_at_submission'})
            return jsonify({
                "msg": "Cannot declare expired medicines",
                "code": "expired_medicine"
            }), 400
        
        # Create medicine declaration
        medicine = Medicine(
            name=data.get('name'),
            amm=data.get('amm'),
            batch_number=data.get('batch_number'),
            expiration_date=expiration_date,
            quantity=data.get('quantity'),
            is_imported=data.get('is_imported', False),
            country_of_origin=data.get('country_of_origin'),
            citizen_id=current_user_id,
            status='SUBMITTED'
        )
        
        db.session.add(medicine)
        db.session.commit()
        
        # Log the declaration
        log_audit(current_user_id, 'MEDICINE_DECLARED', 'MEDICINE', medicine.id,
                 {'name': medicine.name, 'is_imported': medicine.is_imported})
        
        return jsonify({
            "msg": "Medicine declared successfully",
            "medicine": medicine.to_dict()
        }), 201
    
    except ValueError as e:
        return jsonify({"msg": "Invalid date format. Use ISO format (YYYY-MM-DD)", "code": "invalid_date"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": "Error declaring medicine", "code": "declaration_error"}), 500


@blp.route('/declarations/my', methods=['GET'])
@jwt_required()
@role_required('CITIZEN')
def get_my_declarations():
    """
    CITIZEN: Get all medicine declarations submitted by the current user.
    ---
    tags:
      - Medicine Declarations
    security:
      - Bearer: []
    responses:
      200:
        description: List of user's medicine declarations
        schema:
          type: object
          properties:
            count:
              type: integer
            medicines:
              type: array
              items:
                type: object
      401:
        description: Missing or invalid token
      403:
        description: Insufficient permissions
    """
    current_user_id = get_jwt_identity()
    
    # Query all medicines declared by this citizen
    medicines = Medicine.query.filter_by(citizen_id=current_user_id).all()
    
    return jsonify({
        "medicines": [m.to_dict() for m in medicines],
        "count": len(medicines)
    }), 200


@blp.route('/declarations/<int:medicine_id>', methods=['GET'])
@jwt_required()
def get_declaration(medicine_id):
    """
    Get details of a specific medicine declaration.
    Citizens can only see their own declarations (unless admin/staff).
    """
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    medicine = Medicine.query.get(medicine_id)
    
    if not medicine:
        return jsonify({"msg": "Medicine not found", "code": "not_found"}), 404
    
    # Check access rights
    if user.role == 'CITIZEN' and medicine.citizen_id != current_user_id:
        return jsonify({"msg": "Access denied", "code": "forbidden"}), 403
    
    # Show sensitive info to staff/admin
    include_sensitive = user.role in ['PHARMACIST', 'REGULATORY_AGENT', 'ADMIN']
    
    return jsonify({
        "medicine": medicine.to_dict(include_sensitive=include_sensitive)
    }), 200


# ============ PHARMACY VERIFICATION ENDPOINTS ============

@blp.route('/pending-pharmacy-review', methods=['GET'])
@jwt_required()
@role_required('PHARMACIST')
def get_pending_pharmacy_review():
    """
    PHARMACIST: Get all medicines pending pharmacy verification.
    """
    # Get medicines with SUBMITTED status
    medicines = Medicine.query.filter_by(status='SUBMITTED').all()
    
    return jsonify({
        "medicines": [m.to_dict(include_sensitive=True) for m in medicines],
        "count": len(medicines)
    }), 200


@blp.route('/verify/<int:medicine_id>', methods=['POST'])
@jwt_required()
@role_required('PHARMACIST')
def verify_medicine(medicine_id):
    """
    PHARMACIST: Verify medicine packaging and authenticity.
    Expected JSON: { "is_valid": true/false, "notes": "..." }
    """
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    medicine = Medicine.query.get(medicine_id)
    if not medicine:
        return jsonify({"msg": "Medicine not found", "code": "not_found"}), 404
    
    # Check if already verified
    if medicine.status != 'SUBMITTED':
        return jsonify({
            "msg": f"Cannot verify medicine with status: {medicine.status}",
            "code": "invalid_status"
        }), 400
    
    is_valid = data.get('is_valid', True)
    notes = data.get('notes', '')
    
    if is_valid:
        medicine.status = 'PHARMACY_VERIFIED'
        action = 'MEDICINE_PHARMACY_VERIFIED'
    else:
        medicine.status = 'PHARMACY_REJECTED'
        action = 'MEDICINE_PHARMACY_REJECTED'
    
    medicine.pharmacy_verified_at = datetime.utcnow()
    medicine.pharmacy_verified_by = current_user_id
    medicine.pharmacy_notes = notes
    
    db.session.commit()
    
    # Log audit
    log_audit(current_user_id, action, 'MEDICINE', medicine_id, {'notes': notes})
    
    return jsonify({
        "msg": f"Medicine {'approved' if is_valid else 'rejected'} by pharmacy",
        "medicine": medicine.to_dict(include_sensitive=True)
    }), 200


# ============ REGULATORY VALIDATION ENDPOINTS ============

@blp.route('/pending-regulatory-review', methods=['GET'])
@jwt_required()
@role_required('REGULATORY_AGENT')
def get_pending_regulatory_review():
    """
    REGULATORY_AGENT: Get all medicines pending regulatory validation.
    """
    # Get medicines with PHARMACY_VERIFIED status
    medicines = Medicine.query.filter_by(status='PHARMACY_VERIFIED').all()
    
    return jsonify({
        "medicines": [m.to_dict(include_sensitive=True) for m in medicines],
        "count": len(medicines)
    }), 200


@blp.route('/validate/<int:medicine_id>', methods=['POST'])
@jwt_required()
@role_required('REGULATORY_AGENT')
def validate_medicine(medicine_id):
    """
    REGULATORY_AGENT: Validate medicine for redistribution or restrict use.
    Expected JSON: { "decision": "APPROVED|RESTRICTED|REJECTED", "notes": "..." }
    """
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    medicine = Medicine.query.get(medicine_id)
    if not medicine:
        return jsonify({"msg": "Medicine not found", "code": "not_found"}), 404
    
    # Check if ready for regulatory review
    if medicine.status != 'PHARMACY_VERIFIED':
        return jsonify({
            "msg": f"Cannot validate medicine with status: {medicine.status}",
            "code": "invalid_status"
        }), 400
    
    decision = data.get('decision', 'APPROVED').upper()
    notes = data.get('notes', '')
    
    # Validate decision
    valid_decisions = ['APPROVED', 'RESTRICTED', 'REJECTED']
    if decision not in valid_decisions:
        return jsonify({
            "msg": f"Invalid decision. Must be one of {valid_decisions}",
            "code": "invalid_decision"
        }), 400
    
    # Apply regulatory rules and update status
    if decision == 'APPROVED':
        medicine.status = 'APPROVED_FOR_REDISTRIBUTION'
        action = 'MEDICINE_REGULATORY_APPROVED'
    elif decision == 'RESTRICTED':
        medicine.status = 'RESTRICTED_USE'
        action = 'MEDICINE_REGULATORY_RESTRICTED'
    else:
        medicine.status = 'REJECTED_REGULATORY'
        action = 'MEDICINE_REGULATORY_REJECTED'
    
    medicine.regulatory_validated_at = datetime.utcnow()
    medicine.regulatory_validated_by = current_user_id
    medicine.regulatory_notes = notes
    
    db.session.commit()
    
    # Log audit
    log_audit(current_user_id, action, 'MEDICINE', medicine_id, {'decision': decision, 'notes': notes})
    
    return jsonify({
        "msg": f"Medicine regulatory validation completed: {decision}",
        "medicine": medicine.to_dict(include_sensitive=True)
    }), 200


# ============ ELIGIBILITY CHECK ENDPOINTS ============

@blp.route('/<int:medicine_id>/eligibility', methods=['GET'])
@jwt_required()
def check_eligibility(medicine_id):
    """
    Check if a medicine is eligible for redistribution.
    Returns eligibility status and reasons if not eligible.
    """
    medicine = Medicine.query.get(medicine_id)
    
    if not medicine:
        return jsonify({"msg": "Medicine not found", "code": "not_found"}), 404
    
    # Compile eligibility check
    is_eligible = medicine.can_be_redistributed()
    
    reasons = []
    if medicine.is_expired():
        reasons.append("Medicine has expired")
    if medicine.is_imported:
        reasons.append("Imported medicines cannot be redistributed")
    if medicine.is_recalled:
        reasons.append("Medicine has been recalled")
    if medicine.status not in ['APPROVED_FOR_REDISTRIBUTION', 'RESTRICTED_USE']:
        reasons.append(f"Medicine status is {medicine.status}, not approved for redistribution")
    
    return jsonify({
        "medicine_id": medicine_id,
        "is_eligible": is_eligible,
        "status": medicine.status,
        "reasons": reasons if reasons else ["Medicine is eligible for redistribution"]
    }), 200


# ============ HEALTH FACILITY REQUEST ENDPOINTS ============

@blp.route('/approved', methods=['GET'])
@jwt_required()
@role_required('HEALTH_FACILITY')
def get_approved_medicines():
    """
    HEALTH_FACILITY: Get list of medicines approved for redistribution and not yet distributed.
    """
    # Get all medicines that are approved and can be redistributed
    medicines = Medicine.query.filter(
        Medicine.status.in_(['APPROVED_FOR_REDISTRIBUTION', 'RESTRICTED_USE']),
    ).all()
    
    # Filter to only eligible medicines
    eligible_medicines = [m for m in medicines if m.can_be_redistributed()]
    
    return jsonify({
        "medicines": [m.to_dict() for m in eligible_medicines],
        "count": len(eligible_medicines)
    }), 200
