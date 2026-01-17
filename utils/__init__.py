"""
Utils package for TuniMed API.
Contains utility modules for error handling, enums, and audit logging.
"""

from utils.errors import (
    APIError,
    BadRequest,
    Unauthorized,
    Forbidden,
    NotFound,
    InternalServerError,
    register_error_handlers
)

from utils.enums import UserRole, MedicineStatus, OrthopedicSupplyCondition, ActionType

from utils.audit_logging import (
    log_action,
    log_user_registration,
    log_user_login,
    log_medicine_declaration,
    log_medicine_verification,
    log_medicine_approval,
    log_medicine_distribution,
    log_supply_listing,
    get_user_audit_log,
    get_entity_audit_log
)

__all__ = [
    # Error handling
    'APIError',
    'BadRequest',
    'Unauthorized',
    'Forbidden',
    'NotFound',
    'InternalServerError',
    'register_error_handlers',
    # Enums
    'UserRole',
    'MedicineStatus',
    'OrthopedicSupplyCondition',
    'ActionType',
    # Audit logging
    'log_action',
    'log_user_registration',
    'log_user_login',
    'log_medicine_declaration',
    'log_medicine_verification',
    'log_medicine_approval',
    'log_medicine_distribution',
    'log_supply_listing',
    'get_user_audit_log',
    'get_entity_audit_log'
]
