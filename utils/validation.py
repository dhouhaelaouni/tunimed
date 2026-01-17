"""
Input validation utilities for TuniMed API.
Provides validation functions for common data types and business rules.
"""

from datetime import datetime
from utils.errors import BadRequest
from utils.enums import MedicineStatus, OrthopedicSupplyCondition


def validate_required_fields(data, required_fields):
    """
    Validate that all required fields are present in the data.
    
    Args:
        data (dict): Input data
        required_fields (list): List of required field names
    
    Returns:
        None
    
    Raises:
        BadRequest: If any required field is missing
    """
    if not data:
        raise BadRequest('Request body is required', 'empty_request')
    
    missing_fields = [field for field in required_fields if field not in data or data[field] is None]
    if missing_fields:
        raise BadRequest(
            f'Missing required fields: {", ".join(missing_fields)}',
            'missing_required_fields'
        )


def validate_string_field(value, field_name, min_length=1, max_length=None, allow_empty=False):
    """
    Validate a string field.
    
    Args:
        value: The value to validate
        field_name (str): Name of the field (for error messages)
        min_length (int): Minimum string length
        max_length (int): Maximum string length
        allow_empty (bool): Whether empty strings are allowed
    
    Returns:
        str: The validated string
    
    Raises:
        BadRequest: If validation fails
    """
    if not isinstance(value, str):
        raise BadRequest(f'{field_name} must be a string', 'invalid_string_type')
    
    if not allow_empty and len(value.strip()) < min_length:
        raise BadRequest(f'{field_name} must be at least {min_length} character(s)', 'string_too_short')
    
    if max_length and len(value) > max_length:
        raise BadRequest(f'{field_name} must be at most {max_length} character(s)', 'string_too_long')
    
    return value.strip()


def validate_integer_field(value, field_name, min_value=None, max_value=None):
    """
    Validate an integer field.
    
    Args:
        value: The value to validate
        field_name (str): Name of the field (for error messages)
        min_value (int): Minimum allowed value
        max_value (int): Maximum allowed value
    
    Returns:
        int: The validated integer
    
    Raises:
        BadRequest: If validation fails
    """
    try:
        int_value = int(value)
    except (TypeError, ValueError):
        raise BadRequest(f'{field_name} must be an integer', 'invalid_integer_type')
    
    if min_value is not None and int_value < min_value:
        raise BadRequest(f'{field_name} must be at least {min_value}', 'integer_below_minimum')
    
    if max_value is not None and int_value > max_value:
        raise BadRequest(f'{field_name} must be at most {max_value}', 'integer_above_maximum')
    
    return int_value


def validate_float_field(value, field_name, min_value=None, max_value=None):
    """
    Validate a float field.
    
    Args:
        value: The value to validate
        field_name (str): Name of the field (for error messages)
        min_value (float): Minimum allowed value
        max_value (float): Maximum allowed value
    
    Returns:
        float: The validated float
    
    Raises:
        BadRequest: If validation fails
    """
    try:
        float_value = float(value)
    except (TypeError, ValueError):
        raise BadRequest(f'{field_name} must be a number', 'invalid_float_type')
    
    if min_value is not None and float_value < min_value:
        raise BadRequest(f'{field_name} must be at least {min_value}', 'float_below_minimum')
    
    if max_value is not None and float_value > max_value:
        raise BadRequest(f'{field_name} must be at most {max_value}', 'float_above_maximum')
    
    return float_value


def validate_boolean_field(value, field_name):
    """
    Validate a boolean field.
    
    Args:
        value: The value to validate
        field_name (str): Name of the field (for error messages)
    
    Returns:
        bool: The validated boolean
    
    Raises:
        BadRequest: If validation fails
    """
    if isinstance(value, bool):
        return value
    
    if isinstance(value, str):
        if value.lower() in ['true', '1', 'yes']:
            return True
        elif value.lower() in ['false', '0', 'no']:
            return False
    
    raise BadRequest(f'{field_name} must be a boolean (true/false)', 'invalid_boolean_type')


def validate_date_field(value, field_name):
    """
    Validate a date field in ISO format (YYYY-MM-DD or ISO 8601 full format).
    
    Args:
        value (str): The date string to validate
        field_name (str): Name of the field (for error messages)
    
    Returns:
        datetime: The validated datetime object
    
    Raises:
        BadRequest: If validation fails
    """
    if not isinstance(value, str):
        raise BadRequest(f'{field_name} must be a string in ISO format', 'invalid_date_format')
    
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        raise BadRequest(
            f'{field_name} must be in ISO format (YYYY-MM-DD or ISO 8601)',
            'invalid_iso_date_format'
        )


def validate_date_not_expired(expiration_date, field_name='expiration_date'):
    """
    Validate that a date is not in the past.
    
    Args:
        expiration_date (datetime): The expiration date to validate
        field_name (str): Name of the field (for error messages)
    
    Returns:
        datetime: The validated datetime
    
    Raises:
        BadRequest: If the date is in the past
    """
    if expiration_date <= datetime.utcnow():
        raise BadRequest(
            f'{field_name} has already passed. Cannot declare expired items.',
            'expired_date'
        )
    
    return expiration_date


def validate_enum_field(value, enum_class, field_name):
    """
    Validate that a value is a valid enum member.
    
    Args:
        value (str): The value to validate
        enum_class: The enum class to validate against
        field_name (str): Name of the field (for error messages)
    
    Returns:
        str: The validated value
    
    Raises:
        BadRequest: If the value is not a valid enum member
    """
    valid_values = [e.value for e in enum_class]
    
    if value not in valid_values:
        raise BadRequest(
            f'{field_name} must be one of: {", ".join(valid_values)}',
            'invalid_enum_value'
        )
    
    return value


def validate_medicine_declaration(data):
    """
    Validate complete medicine declaration input.
    
    Args:
        data (dict): The medicine declaration data
    
    Returns:
        dict: Validated and cleaned data
    
    Raises:
        BadRequest: If validation fails
    """
    # Validate required fields
    required_fields = ['name', 'amm', 'batch_number', 'expiration_date', 'quantity']
    validate_required_fields(data, required_fields)
    
    validated = {}
    
    # Validate and clean name
    validated['name'] = validate_string_field(
        data['name'],
        'name',
        min_length=1,
        max_length=200
    )
    
    # Validate and clean amm
    validated['amm'] = validate_string_field(
        data['amm'],
        'amm',
        min_length=1,
        max_length=50
    )
    
    # Validate and clean batch_number
    validated['batch_number'] = validate_string_field(
        data['batch_number'],
        'batch_number',
        min_length=1,
        max_length=100
    )
    
    # Validate and clean expiration_date
    expiration_date = validate_date_field(data['expiration_date'], 'expiration_date')
    validated['expiration_date'] = validate_date_not_expired(expiration_date)
    
    # Validate and clean quantity
    validated['quantity'] = validate_integer_field(
        data['quantity'],
        'quantity',
        min_value=1
    )
    
    # Validate optional is_imported
    if 'is_imported' in data:
        validated['is_imported'] = validate_boolean_field(data['is_imported'], 'is_imported')
    else:
        validated['is_imported'] = False
    
    # Validate optional country_of_origin (only if imported)
    if 'country_of_origin' in data and data['country_of_origin']:
        validated['country_of_origin'] = validate_string_field(
            data['country_of_origin'],
            'country_of_origin',
            min_length=1,
            max_length=100
        )
    else:
        validated['country_of_origin'] = None
    
    return validated


def validate_orthopedic_supply_listing(data):
    """
    Validate complete orthopedic supply listing input.
    
    Args:
        data (dict): The supply listing data
    
    Returns:
        dict: Validated and cleaned data
    
    Raises:
        BadRequest: If validation fails
    """
    # Validate required fields
    required_fields = ['name', 'condition', 'quantity']
    validate_required_fields(data, required_fields)
    
    validated = {}
    
    # Validate and clean name
    validated['name'] = validate_string_field(
        data['name'],
        'name',
        min_length=1,
        max_length=200
    )
    
    # Validate condition
    validated['condition'] = validate_enum_field(
        data['condition'],
        OrthopedicSupplyCondition,
        'condition'
    )
    
    # Validate and clean quantity
    validated['quantity'] = validate_integer_field(
        data['quantity'],
        'quantity',
        min_value=1
    )
    
    # Validate optional description
    if 'description' in data and data['description']:
        validated['description'] = validate_string_field(
            data['description'],
            'description',
            max_length=1000,
            allow_empty=True
        )
    else:
        validated['description'] = None
    
    # Validate optional is_for_sale
    if 'is_for_sale' in data:
        validated['is_for_sale'] = validate_boolean_field(data['is_for_sale'], 'is_for_sale')
    else:
        validated['is_for_sale'] = False
    
    # Validate optional price (only if is_for_sale)
    if validated['is_for_sale']:
        if 'price' not in data or data['price'] is None:
            raise BadRequest('price is required when is_for_sale is true', 'missing_price')
        validated['price'] = validate_float_field(
            data['price'],
            'price',
            min_value=0
        )
    else:
        validated['price'] = None
    
    return validated
