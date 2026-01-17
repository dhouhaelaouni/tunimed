from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from models.user import User, OrthopedicSupply
from db import db

# Create orthopedic supplies blueprint
blp = Blueprint('orthopedic_supplies', __name__, url_prefix='/api/orthopedic-supplies')


# ============ HELPER FUNCTIONS ============

def validate_condition(condition):
    """Validate that condition is one of the allowed values"""
    valid_conditions = ['NEW', 'VERY_GOOD', 'GOOD']
    return condition in valid_conditions


def validate_orthopedic_supply_data(data, for_creation=True):
    """Validate orthopedic supply data"""
    if not data:
        return False, "No data provided", 400
    
    # Validate required fields
    if not data.get('name') or not isinstance(data.get('name'), str):
        return False, "Name is required and must be a string", 400
    
    if not data.get('condition') or not validate_condition(data.get('condition')):
        return False, "Condition is required and must be one of: NEW, VERY_GOOD, GOOD", 400
    
    quantity = data.get('quantity')
    if not isinstance(quantity, int) or quantity <= 0:
        return False, "Quantity is required and must be a positive integer", 400
    
    is_for_sale = data.get('is_for_sale', False)
    if not isinstance(is_for_sale, bool):
        return False, "is_for_sale must be a boolean", 400
    
    # If for sale, price is required
    if is_for_sale:
        price = data.get('price')
        if price is None or (not isinstance(price, (int, float)) or price <= 0):
            return False, "Price is required for sale items and must be a positive number", 400
    
    return True, None, None


# ============ ORTHOPEDIC SUPPLIES ENDPOINTS ============

@blp.route('', methods=['POST'])
@jwt_required()
def create_orthopedic_supply():
    """
    Create a new orthopedic supply donation or sale.
    Authenticated users can donate or sell orthopedic supplies.
    No pharmacist or regulator approval required.
    ---
    tags:
      - Orthopedic Supplies
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
            - condition
            - quantity
          properties:
            name:
              type: string
              example: "Wooden Crutches"
            description:
              type: string
              example: "Pair of wooden crutches, gently used"
            condition:
              type: string
              enum: ["NEW", "VERY_GOOD", "GOOD"]
              example: "VERY_GOOD"
            quantity:
              type: integer
              example: 2
            is_for_sale:
              type: boolean
              example: false
            price:
              type: number
              example: 15.99
    responses:
      201:
        description: Orthopedic supply created successfully
        schema:
          type: object
          properties:
            msg:
              type: string
            supply:
              type: object
      400:
        description: Invalid input data
      401:
        description: Missing or invalid token
      500:
        description: Server error
    """
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    # Validate input
    is_valid, error_msg, status_code = validate_orthopedic_supply_data(data)
    if not is_valid:
        return jsonify({"msg": error_msg, "code": "invalid_input"}), status_code
    
    try:
        # Create new orthopedic supply
        supply = OrthopedicSupply(
            name=data.get('name'),
            description=data.get('description'),
            condition=data.get('condition'),
            quantity=data.get('quantity'),
            is_for_sale=data.get('is_for_sale', False),
            price=data.get('price') if data.get('is_for_sale') else None,
            donor_id=current_user_id
        )
        
        db.session.add(supply)
        db.session.commit()
        
        return jsonify({
            "msg": "Orthopedic supply created successfully",
            "supply": supply.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "msg": "Error creating orthopedic supply",
            "code": "creation_error",
            "details": str(e)
        }), 500


@blp.route('', methods=['GET'])
def list_orthopedic_supplies():
    """
    List all available orthopedic supplies.
    Public access - no authentication required.
    Returns both donations and items for sale.
    ---
    tags:
      - Orthopedic Supplies
    parameters:
      - in: query
        name: condition
        type: string
        enum: ["NEW", "VERY_GOOD", "GOOD"]
        description: Filter by condition
      - in: query
        name: is_for_sale
        type: boolean
        description: Filter by sale status (true for sales, false for donations)
      - in: query
        name: page
        type: integer
        default: 1
        description: Page number for pagination
      - in: query
        name: per_page
        type: integer
        default: 20
        description: Items per page
    responses:
      200:
        description: List of orthopedic supplies
        schema:
          type: object
          properties:
            total:
              type: integer
            page:
              type: integer
            per_page:
              type: integer
            supplies:
              type: array
              items:
                type: object
      400:
        description: Invalid query parameters
    """
    try:
        # Get query parameters
        condition = request.args.get('condition')
        is_for_sale = request.args.get('is_for_sale')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Validate pagination
        if page < 1 or per_page < 1:
            return jsonify({
                "msg": "Page and per_page must be positive integers",
                "code": "invalid_pagination"
            }), 400
        
        # Build query
        query = OrthopedicSupply.query
        
        # Apply filters
        if condition:
            if not validate_condition(condition):
                return jsonify({
                    "msg": f"Invalid condition. Must be one of: NEW, VERY_GOOD, GOOD",
                    "code": "invalid_filter"
                }), 400
            query = query.filter_by(condition=condition)
        
        if is_for_sale is not None:
            is_for_sale_bool = is_for_sale.lower() == 'true'
            query = query.filter_by(is_for_sale=is_for_sale_bool)
        
        # Get total count
        total = query.count()
        
        # Paginate and sort by newest first
        supplies = query.order_by(
            OrthopedicSupply.created_at.desc()
        ).paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            "total": total,
            "page": page,
            "per_page": per_page,
            "supplies": [supply.to_dict() for supply in supplies.items]
        }), 200
    
    except Exception as e:
        return jsonify({
            "msg": "Error retrieving orthopedic supplies",
            "code": "retrieval_error",
            "details": str(e)
        }), 500


@blp.route('/<int:supply_id>', methods=['GET'])
def get_orthopedic_supply(supply_id):
    """
    Get details of a specific orthopedic supply.
    Public access - no authentication required.
    ---
    tags:
      - Orthopedic Supplies
    parameters:
      - in: path
        name: supply_id
        type: integer
        required: true
        description: The ID of the orthopedic supply
    responses:
      200:
        description: Orthopedic supply details
        schema:
          type: object
          properties:
            supply:
              type: object
      404:
        description: Orthopedic supply not found
    """
    try:
        supply = OrthopedicSupply.query.get(supply_id)
        
        if not supply:
            return jsonify({
                "msg": f"Orthopedic supply with ID {supply_id} not found",
                "code": "not_found"
            }), 404
        
        return jsonify({
            "supply": supply.to_dict()
        }), 200
    
    except Exception as e:
        return jsonify({
            "msg": "Error retrieving orthopedic supply",
            "code": "retrieval_error",
            "details": str(e)
        }), 500


@blp.route('/<int:supply_id>', methods=['DELETE'])
@jwt_required()
def delete_orthopedic_supply(supply_id):
    """
    Delete an orthopedic supply.
    Only the donor who created the supply can delete it.
    ---
    tags:
      - Orthopedic Supplies
    security:
      - Bearer: []
    parameters:
      - in: path
        name: supply_id
        type: integer
        required: true
        description: The ID of the orthopedic supply to delete
    responses:
      200:
        description: Orthopedic supply deleted successfully
      401:
        description: Missing or invalid token
      403:
        description: Only the donor can delete their own supply
      404:
        description: Orthopedic supply not found
      500:
        description: Server error
    """
    current_user_id = get_jwt_identity()
    
    try:
        supply = OrthopedicSupply.query.get(supply_id)
        
        if not supply:
            return jsonify({
                "msg": f"Orthopedic supply with ID {supply_id} not found",
                "code": "not_found"
            }), 404
        
        # Check if current user is the donor
        if supply.donor_id != current_user_id:
            return jsonify({
                "msg": "Only the donor can delete their own orthopedic supply",
                "code": "forbidden"
            }), 403
        
        # Delete the supply
        db.session.delete(supply)
        db.session.commit()
        
        return jsonify({
            "msg": "Orthopedic supply deleted successfully",
            "supply_id": supply_id
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "msg": "Error deleting orthopedic supply",
            "code": "deletion_error",
            "details": str(e)
        }), 500
