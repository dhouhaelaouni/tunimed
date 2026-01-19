from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from models.user import User, Medicine, AuditLog
from db import db
from decorators.decorators import role_required, any_role_required
from utils.enums import UserRole, MedicineStatus

blp = Blueprint('medicines', __name__, url_prefix='/medicines')


def log_audit(user_id, action, entity_type, entity_id, details=None):
    audit_log = AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details
    )
    db.session.add(audit_log)
    db.session.commit()


# ================= CITIZEN =================

@blp.route('/declarations', methods=['POST'])
@role_required(UserRole.CITIZEN)
def declare_medicine():
    """
    CITIZEN: Declare a new medicine for reuse/redistribution.
    ---
    tags:
      - Medicine Declarations (Citizen)
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
              example: "Paracetamol"
            amm:
              type: string
              description: "Authorization code"
              example: "AMM-2023-001"
            batch_number:
              type: string
              example: "BATCH2025001"
            expiration_date:
              type: string
              format: date
              example: "2026-12-31"
            quantity:
              type: integer
              example: 10
            is_imported:
              type: boolean
              default: false
            country_of_origin:
              type: string
              example: "Tunisia"
    responses:
      201:
        description: Medicine declared successfully
      400:
        description: Invalid input or expired date
      401:
        description: Missing or invalid token
      403:
        description: Insufficient permissions (not a CITIZEN)
    """
    current_user_id = get_jwt_identity()
    data = request.get_json()

    required = ['name', 'amm', 'batch_number', 'expiration_date', 'quantity']
    if not data or not all(k in data for k in required):
        return jsonify({"msg": "Missing required fields"}), 400

    try:
        expiration_date = datetime.fromisoformat(data['expiration_date'])
        if datetime.utcnow() > expiration_date:
            log_audit(current_user_id, 'MEDICINE_DECLARATION_REJECTED', 'MEDICINE', None)
            return jsonify({"msg": "Cannot declare expired medicines"}), 400

        medicine = Medicine(
            name=data['name'],
            amm=data['amm'],
            batch_number=data['batch_number'],
            expiration_date=expiration_date,
            quantity=data['quantity'],
            is_imported=data.get('is_imported', False),
            country_of_origin=data.get('country_of_origin'),
            citizen_id=current_user_id,
            status=MedicineStatus.SUBMITTED.value
        )

        db.session.add(medicine)
        db.session.commit()

        log_audit(current_user_id, 'MEDICINE_DECLARED', 'MEDICINE', medicine.id)

        return jsonify({
            "msg": "Medicine declared successfully",
            "medicine": medicine.to_dict()
        }), 201

    except ValueError:
        return jsonify({"msg": "Invalid date format"}), 400
    except Exception:
        db.session.rollback()
        return jsonify({"msg": "Error declaring medicine"}), 500


@blp.route('/declarations/my', methods=['GET'])
@role_required(UserRole.CITIZEN)
def get_my_declarations():
    """
    CITIZEN: Get all medicine declarations submitted by the current user.
    ---
    tags:
      - Medicine Declarations (Citizen)
    security:
      - Bearer: []
    responses:
      200:
        description: List of user's medicine declarations
      401:
        description: Missing or invalid token
      403:
        description: Insufficient permissions
    """
    current_user_id = get_jwt_identity()
    medicines = Medicine.query.filter_by(citizen_id=current_user_id).all()

    return jsonify({
        "count": len(medicines),
        "medicines": [m.to_dict() for m in medicines]
    }), 200


@blp.route('/declarations/<int:medicine_id>', methods=['GET'])
@jwt_required()
def get_declaration(medicine_id):
    """
    Get details of a specific medicine declaration.
    ---
    tags:
      - Medicine Declarations
    security:
      - Bearer: []
    parameters:
      - in: path
        name: medicine_id
        type: integer
        required: true
    responses:
      200:
        description: Medicine declaration details
      403:
        description: Access denied - only owner or pharmacist can view
      404:
        description: Medicine not found
    """
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    medicine = Medicine.query.get(medicine_id)

    if not medicine:
        return jsonify({"msg": "Medicine not found"}), 404

    # Fix: compare against Enum value string
    if user.role == UserRole.CITIZEN.value and medicine.citizen_id != current_user_id:
        return jsonify({"msg": "Access denied"}), 403

    # Fix: update role check to PHARMACIST
    include_sensitive = user.role in [UserRole.PHARMACIST.value, UserRole.ADMIN.value]

    return jsonify({
        "medicine": medicine.to_dict(include_sensitive=include_sensitive)
    }), 200


# ================= PHARMACIST =================

@blp.route('/pending-pharmacy-review', methods=['GET'])
@role_required(UserRole.PHARMACIST) # Fixed from PHARMACY
def get_pending_pharmacy_review():
    """
    PHARMACY: Get medicines pending verification.
    ---
    tags:
      - Medicine Verification (Pharmacist)
    security:
      - Bearer: []
    responses:
      200:
        description: List of medicines awaiting verification
      401:
        description: Missing or invalid token
      403:
        description: Must be PHARMACIST
    """
    medicines = Medicine.query.filter_by(status=MedicineStatus.SUBMITTED.value).all()
    return jsonify({
        "count": len(medicines),
        "medicines": [m.to_dict() for m in medicines]
    }), 200


@blp.route('/verify/<int:medicine_id>', methods=['POST'])
@role_required(UserRole.PHARMACIST) # Fixed from PHARMACY
def verify_medicine(medicine_id):
    """
    PHARMACIST: Verify medicine packaging and authenticity.
    ---
    tags:
      - Medicine Verification (Pharmacist)
    security:
      - Bearer: []
    parameters:
      - in: path
        name: medicine_id
        type: integer
        required: true
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - is_valid
          properties:
            is_valid:
              type: boolean
              description: "True to approve, false to reject"
              example: true
            notes:
              type: string
              description: "Pharmacist verification notes"
              example: "Packaging intact, authenticity verified"
    responses:
      200:
        description: Verification completed
      400:
        description: Invalid medicine or status
      401:
        description: Missing or invalid token
      403:
        description: Must be PHARMACIST
    """
    current_user_id = get_jwt_identity()
    data = request.get_json()

    if not data or 'is_valid' not in data:
        return jsonify({"error_code": "missing_required_fields", "message": "Missing 'is_valid' field", "status": 400}), 400

    medicine = Medicine.query.get(medicine_id)
    if not medicine or medicine.status != MedicineStatus.SUBMITTED.value:
        return jsonify({"error_code": "invalid_status", "message": "Medicine not found or not in SUBMITTED status", "status": 400}), 400

    is_valid = data.get('is_valid', True)
    notes = data.get('notes', '')

    if is_valid:
        medicine.status = MedicineStatus.APPROVED_FOR_REDISTRIBUTION.value
        action = 'MEDICINE_VERIFIED_AND_APPROVED'
    else:
        medicine.status = MedicineStatus.PHARMACY_REJECTED.value
        action = 'MEDICINE_REJECTED'

    medicine.pharmacy_verified_at = datetime.utcnow()
    medicine.pharmacy_verified_by = current_user_id
    medicine.pharmacy_notes = notes

    db.session.commit()

    log_audit(current_user_id, action, 'MEDICINE', medicine.id, {'notes': notes})

    return jsonify({
        "message": f"Medicine {'approved' if is_valid else 'rejected'}",
        "medicine": medicine.to_dict()
    }), 200


@blp.route('/pending-approval', methods=['GET'])
@role_required(UserRole.PHARMACIST) # Fixed from PHARMACY
def get_pending_approval():
    """
    PHARMACIST: Get medicines pending approval (for backward compatibility).
    ---
    tags:
      - Medicine Verification (Pharmacist)
    security:
      - Bearer: []
    responses:
      200:
        description: Empty list (approval happens during verification)
    """
    return jsonify({
        "count": 0,
        "message": "Approval is now combined with verification step",
        "medicines": []
    }), 200