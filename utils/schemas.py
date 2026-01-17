"""
Marshmallow validation schemas for TuniMed API
Provides request/response validation and serialization with field-level error details.
"""

from marshmallow import Schema, fields, validate, ValidationError as MarshmallowValidationError, post_load
from utils.enums import UserRole, MedicineStatus, OrthopedicSupplyCondition


# ============================================================
# CUSTOM FIELD VALIDATORS
# ============================================================

def validate_positive(value):
    """Ensure value is positive integer"""
    if value <= 0:
        raise MarshmallowValidationError("Must be a positive integer")


def validate_username(value):
    """Ensure username is alphanumeric with underscores/hyphens"""
    if not value or len(value) < 3:
        raise MarshmallowValidationError("Username must be at least 3 characters")
    if not all(c.isalnum() or c in '_-' for c in value):
        raise MarshmallowValidationError("Username can only contain letters, numbers, underscores, and hyphens")


def validate_medicine_name(value):
    """Ensure medicine name is not empty and reasonable length"""
    if not value or len(value.strip()) == 0:
        raise MarshmallowValidationError("Medicine name cannot be empty")
    if len(value) > 200:
        raise MarshmallowValidationError("Medicine name must be less than 200 characters")


def validate_user_role(value):
    """Ensure role is valid"""
    valid_roles = [role.value for role in UserRole]
    if value not in valid_roles:
        raise MarshmallowValidationError(f"Invalid role. Must be one of: {', '.join(valid_roles)}")


def validate_medicine_status(value):
    """Ensure medicine status is valid"""
    valid_statuses = [status.value for status in MedicineStatus]
    if value not in valid_statuses:
        raise MarshmallowValidationError(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")


def validate_supply_condition(value):
    """Ensure orthopedic supply condition is valid"""
    valid_conditions = [cond.value for cond in OrthopedicSupplyCondition]
    if value not in valid_conditions:
        raise MarshmallowValidationError(f"Invalid condition. Must be one of: {', '.join(valid_conditions)}")


# ============================================================
# MEDICINE REFERENCE SCHEMAS
# ============================================================

class MedicineReferenceCreateSchema(Schema):
    """Schema for creating a new medicine reference"""
    name = fields.String(
        required=True,
        validate=validate_medicine_name,
        metadata={'description': 'Medicine name (max 200 chars)'}
    )
    form = fields.String(
        required=True,
        validate=validate.Length(min=1, max=100),
        metadata={'description': 'Medicine form (e.g., Tablet, Capsule, Liquid)'}
    )
    dosage = fields.String(
        required=True,
        validate=validate.Length(min=1, max=100),
        metadata={'description': 'Medicine dosage (e.g., 500mg, 10ml)'}
    )


class MedicineReferenceUpdateSchema(Schema):
    """Schema for updating a medicine reference"""
    name = fields.String(
        required=False,
        validate=validate_medicine_name,
        metadata={'description': 'Medicine name (max 200 chars)'}
    )
    form = fields.String(
        required=False,
        validate=validate.Length(min=1, max=100),
        metadata={'description': 'Medicine form'}
    )
    dosage = fields.String(
        required=False,
        validate=validate.Length(min=1, max=100),
        metadata={'description': 'Medicine dosage'}
    )


class MedicineReferenceResponseSchema(Schema):
    """Schema for medicine reference response"""
    id = fields.Integer(dump_only=True)
    name = fields.String()
    form = fields.String()
    dosage = fields.String()
    created_at = fields.DateTime()


# ============================================================
# MEDICINE DECLARATION SCHEMAS
# ============================================================

class MedicineDeclarationCreateSchema(Schema):
    """Schema for creating a medicine declaration"""
    medicine_reference_id = fields.Integer(
        required=True,
        validate=validate_positive,
        metadata={'description': 'ID of medicine reference'}
    )
    quantity_produced = fields.Integer(
        required=True,
        validate=validate_positive,
        metadata={'description': 'Quantity produced (positive integer)'}
    )
    quantity_available = fields.Integer(
        required=True,
        validate=validate_positive,
        metadata={'description': 'Quantity available (positive integer)'}
    )
    production_date = fields.Date(
        required=False,
        metadata={'description': 'Production date (YYYY-MM-DD)'}
    )
    expiration_date = fields.Date(
        required=False,
        metadata={'description': 'Expiration date (YYYY-MM-DD)'}
    )


class MedicineDeclarationResponseSchema(Schema):
    """Schema for medicine declaration response"""
    id = fields.Integer(dump_only=True)
    citizen_id = fields.Integer(dump_only=True)
    medicine_reference_id = fields.Integer()
    status = fields.String()
    quantity_produced = fields.Integer()
    quantity_available = fields.Integer()
    created_at = fields.DateTime(dump_only=True)


# ============================================================
# ORTHOPEDIC SUPPLY SCHEMAS
# ============================================================

class OrthopedicSupplyCreateSchema(Schema):
    """Schema for creating an orthopedic supply"""
    name = fields.String(
        required=True,
        validate=validate.Length(min=1, max=200),
        metadata={'description': 'Supply name (max 200 chars)'}
    )
    description = fields.String(
        required=False,
        validate=validate.Length(max=500),
        metadata={'description': 'Supply description (max 500 chars)'}
    )
    condition = fields.String(
        required=True,
        validate=validate_supply_condition,
        metadata={'description': f'Condition: {", ".join([c.value for c in OrthopedicSupplyCondition])}'}
    )
    quantity = fields.Integer(
        required=True,
        validate=validate_positive,
        metadata={'description': 'Quantity available (positive integer)'}
    )
    is_for_sale = fields.Boolean(
        required=False,
        missing=False,
        metadata={'description': 'Whether supply is for sale (default: false)'}
    )
    price = fields.Float(
        required=False,
        validate=validate.Range(min=0),
        metadata={'description': 'Price if for_sale is true (must be >= 0)'}
    )


class OrthopedicSupplyUpdateSchema(Schema):
    """Schema for updating an orthopedic supply"""
    name = fields.String(
        required=False,
        validate=validate.Length(min=1, max=200),
        metadata={'description': 'Supply name'}
    )
    description = fields.String(
        required=False,
        validate=validate.Length(max=500),
        metadata={'description': 'Supply description'}
    )
    condition = fields.String(
        required=False,
        validate=validate_supply_condition,
        metadata={'description': 'Condition'}
    )
    quantity = fields.Integer(
        required=False,
        validate=validate_positive,
        metadata={'description': 'Quantity available'}
    )
    is_for_sale = fields.Boolean(
        required=False,
        metadata={'description': 'Whether supply is for sale'}
    )
    price = fields.Float(
        required=False,
        validate=validate.Range(min=0),
        metadata={'description': 'Price if for_sale is true'}
    )


class OrthopedicSupplyResponseSchema(Schema):
    """Schema for orthopedic supply response"""
    id = fields.Integer(dump_only=True)
    name = fields.String()
    description = fields.String()
    condition = fields.String()
    quantity = fields.Integer()
    is_for_sale = fields.Boolean()
    price = fields.Float()
    donor_id = fields.Integer()
    is_active = fields.Boolean()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()


# ============================================================
# USER SCHEMAS
# ============================================================

class UserRegistrationSchema(Schema):
    """Schema for user registration"""
    username = fields.String(
        required=True,
        validate=validate_username,
        metadata={'description': 'Username (3+ chars, alphanumeric, underscores, hyphens)'}
    )
    email = fields.Email(
        required=True,
        metadata={'description': 'Email address'}
    )
    password = fields.String(
        required=True,
        validate=validate.Length(min=8),
        metadata={'description': 'Password (min 8 characters)'}
    )
    role = fields.String(
        required=True,
        validate=validate_user_role,
        metadata={'description': f'User role: {", ".join([r.value for r in UserRole])}'}
    )


class UserLoginSchema(Schema):
    """Schema for user login"""
    username = fields.String(
        required=True,
        metadata={'description': 'Username'}
    )
    password = fields.String(
        required=True,
        metadata={'description': 'Password'}
    )


class UserResponseSchema(Schema):
    """Schema for user response"""
    id = fields.Integer(dump_only=True)
    username = fields.String()
    email = fields.String()
    role = fields.String()
    is_active = fields.Boolean()
    created_at = fields.DateTime(dump_only=True)


# ============================================================
# PAGINATION METADATA SCHEMAS
# ============================================================

class PaginationMetadataSchema(Schema):
    """Schema for pagination metadata in responses"""
    total_items = fields.Integer(metadata={'description': 'Total number of items'})
    page = fields.Integer(metadata={'description': 'Current page number'})
    limit = fields.Integer(metadata={'description': 'Items per page'})
    total_pages = fields.Integer(metadata={'description': 'Total number of pages'})


class PaginatedResponseSchema(Schema):
    """Generic paginated response schema"""
    data = fields.List(fields.Dict(), metadata={'description': 'List of items'})
    pagination = fields.Nested(PaginationMetadataSchema, metadata={'description': 'Pagination metadata'})


# ============================================================
# SCHEMA INSTANCES
# ============================================================

# Medicine References
medicine_reference_create_schema = MedicineReferenceCreateSchema()
medicine_reference_update_schema = MedicineReferenceUpdateSchema()
medicine_reference_response_schema = MedicineReferenceResponseSchema()

# Medicine Declarations
medicine_declaration_create_schema = MedicineDeclarationCreateSchema()
medicine_declaration_response_schema = MedicineDeclarationResponseSchema()

# Orthopedic Supplies
supply_create_schema = OrthopedicSupplyCreateSchema()
supply_update_schema = OrthopedicSupplyUpdateSchema()
supply_response_schema = OrthopedicSupplyResponseSchema()

# Users
user_registration_schema = UserRegistrationSchema()
user_login_schema = UserLoginSchema()
user_response_schema = UserResponseSchema()

# Pagination
pagination_metadata_schema = PaginationMetadataSchema()
paginated_response_schema = PaginatedResponseSchema()


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def validate_request_data(data, schema):
    """
    Validate request data against schema.
    
    Args:
        data (dict): Request data to validate
        schema: Marshmallow schema instance
    
    Returns:
        tuple: (validated_data, errors_dict or None)
    
    Example:
        validated, errors = validate_request_data(request.get_json(), medicine_reference_create_schema)
        if errors:
            raise ValidationError('Validation failed', fields=errors)
        medicine_ref = create_medicine_reference(validated)
    """
    try:
        validated = schema.load(data)
        return validated, None
    except MarshmallowValidationError as err:
        return None, err.messages
