"""Validation service.

Wraps lower-level validators from `utils/validation.py` to present a small,
service-focused API. This keeps validation logic in one place and makes
it easier to compose validation in unit tests.
"""
from utils.validation import validate_string_field
from utils.errors import BadRequest


class ValidationService:
    """Small wrapper for input validation used by services."""

    @staticmethod
    def validate_medicine_reference_payload(data):
        if not data:
            raise BadRequest('No data provided', 'invalid_input')

        name = data.get('name')
        form = data.get('form')
        dosage = data.get('dosage')

        try:
            name = validate_string_field(name, 'name', min_length=1, max_length=200)
            form = validate_string_field(form, 'form', min_length=1, max_length=100)
            dosage = validate_string_field(dosage, 'dosage', min_length=1, max_length=100)
        except Exception as e:
            # Re-raise as BadRequest if not already
            if isinstance(e, BadRequest):
                raise
            raise BadRequest(str(e), 'invalid_input')

        return {'name': name, 'form': form, 'dosage': dosage}
