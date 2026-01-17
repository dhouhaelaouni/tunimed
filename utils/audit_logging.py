"""
Audit logging utility for TuniMed API.
Provides centralized audit logging for user actions and system events.
"""

from datetime import datetime
from db import db
from utils.enums import ActionType


def log_action(user_id, action_type, entity_type, entity_id=None, details=None):
    """
    Log a user action to the audit trail.
    
    Args:
        user_id (int): ID of the user performing the action
        action_type (str|ActionType): Type of action (use ActionType enum or string)
        entity_type (str): Type of entity affected (e.g., 'MEDICINE', 'USER', 'SUPPLY')
        entity_id (int, optional): ID of the entity affected
        details (dict, optional): Additional details about the action
    
    Returns:
        AuditLog: The created audit log entry
    
    Raises:
        ValueError: If user_id is invalid or entity_type is empty
    """
    # Import here to avoid circular imports
    from models.user import User, AuditLog
    
    if not user_id:
        raise ValueError("user_id is required for audit logging")
    
    if not entity_type:
        raise ValueError("entity_type is required for audit logging")
    
    # Convert ActionType enum to string if necessary
    if isinstance(action_type, ActionType):
        action_type_str = action_type.value
    else:
        action_type_str = str(action_type)
    
    try:
        # Verify user exists
        user = User.query.get(user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} does not exist")
        
        # Create audit log entry
        audit_log = AuditLog(
            user_id=user_id,
            action=action_type_str,
            entity_type=entity_type,
            entity_id=entity_id,
            details=details or {}
        )
        
        db.session.add(audit_log)
        db.session.commit()
        
        return audit_log
    
    except Exception as e:
        db.session.rollback()
        raise e


def log_user_registration(user_id, role, details=None):
    """Log a user registration action"""
    log_data = {'role': role}
    if details:
        log_data.update(details)
    
    return log_action(
        user_id=user_id,
        action_type=ActionType.REGISTERED,
        entity_type='USER',
        entity_id=user_id,
        details=log_data
    )


def log_user_login(user_id, details=None):
    """Log a user login action"""
    log_data = {'timestamp': datetime.utcnow().isoformat()}
    if details:
        log_data.update(details)
    
    return log_action(
        user_id=user_id,
        action_type=ActionType.LOGIN,
        entity_type='USER',
        entity_id=user_id,
        details=log_data
    )


def log_medicine_declaration(user_id, medicine_id, medicine_name, is_imported, details=None):
    """Log a medicine declaration"""
    log_data = {
        'medicine_name': medicine_name,
        'is_imported': is_imported
    }
    if details:
        log_data.update(details)
    
    return log_action(
        user_id=user_id,
        action_type=ActionType.MEDICINE_DECLARED,
        entity_type='MEDICINE',
        entity_id=medicine_id,
        details=log_data
    )


def log_medicine_verification(user_id, medicine_id, verified, notes=None, details=None):
    """Log a medicine verification action"""
    action = ActionType.MEDICINE_VERIFIED if verified else ActionType.MEDICINE_REJECTED
    log_data = {'verified': verified}
    
    if notes:
        log_data['notes'] = notes
    if details:
        log_data.update(details)
    
    return log_action(
        user_id=user_id,
        action_type=action,
        entity_type='MEDICINE',
        entity_id=medicine_id,
        details=log_data
    )


def log_medicine_approval(user_id, medicine_id, approved, notes=None, details=None):
    """Log a medicine regulatory approval action"""
    action = ActionType.MEDICINE_APPROVED if approved else ActionType.MEDICINE_REJECTED
    log_data = {'approved': approved}
    
    if notes:
        log_data['notes'] = notes
    if details:
        log_data.update(details)
    
    return log_action(
        user_id=user_id,
        action_type=action,
        entity_type='MEDICINE',
        entity_id=medicine_id,
        details=log_data
    )


def log_medicine_distribution(user_id, medicine_id, quantity_distributed, details=None):
    """Log a medicine distribution action"""
    log_data = {'quantity_distributed': quantity_distributed}
    if details:
        log_data.update(details)
    
    return log_action(
        user_id=user_id,
        action_type=ActionType.MEDICINE_DISTRIBUTED,
        entity_type='MEDICINE',
        entity_id=medicine_id,
        details=log_data
    )


def log_supply_listing(user_id, supply_id, supply_name, is_for_sale, details=None):
    """Log an orthopedic supply listing action"""
    log_data = {
        'supply_name': supply_name,
        'is_for_sale': is_for_sale
    }
    if details:
        log_data.update(details)
    
    return log_action(
        user_id=user_id,
        action_type=ActionType.SUPPLY_LISTED,
        entity_type='SUPPLY',
        entity_id=supply_id,
        details=log_data
    )


def get_user_audit_log(user_id, limit=100):
    """
    Get audit log entries for a specific user.
    
    Args:
        user_id (int): ID of the user
        limit (int): Maximum number of entries to return
    
    Returns:
        list: List of audit log entries
    """
    # Import here to avoid circular imports
    from models.user import AuditLog
    
    return AuditLog.query.filter_by(user_id=user_id).order_by(
        AuditLog.created_at.desc()
    ).limit(limit).all()


def get_entity_audit_log(entity_type, entity_id, limit=100):
    """
    Get audit log entries for a specific entity.
    
    Args:
        entity_type (str): Type of entity (e.g., 'MEDICINE', 'USER')
        entity_id (int): ID of the entity
        limit (int): Maximum number of entries to return
    
    Returns:
        list: List of audit log entries
    """
    # Import here to avoid circular imports
    from models.user import AuditLog
    
    return AuditLog.query.filter_by(
        entity_type=entity_type,
        entity_id=entity_id
    ).order_by(AuditLog.created_at.desc()).limit(limit).all()
