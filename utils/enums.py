from enum import Enum

class UserRole(Enum):
    """User roles in the TuniMed system"""
    CITIZEN = 'CITIZEN'
    PHARMACIST = 'PHARMACIST'  # Changed attribute name from PHARMACY to PHARMACIST
    HEALTH_FACILITY = 'HEALTH_FACILITY'  
    ADMIN = 'ADMIN'
    
    @classmethod
    def all_roles(cls):
        """Get list of all valid roles as strings"""
        return [role.value for role in cls]
    
    @classmethod
    def is_valid(cls, role):
        """Check if a role string is valid"""
        return role in cls.all_roles()


class MedicineStatus(Enum):
    """Medicine declaration statuses in the workflow"""
    SUBMITTED = 'SUBMITTED'
    PHARMACY_VERIFIED = 'PHARMACY_VERIFIED'
    PHARMACY_REJECTED = 'PHARMACY_REJECTED'
    APPROVED_FOR_REDISTRIBUTION = 'APPROVED_FOR_REDISTRIBUTION'
    RESTRICTED_USE = 'RESTRICTED_USE'
    REJECTED_REGULATORY = 'REJECTED_REGULATORY'
    DISTRIBUTED = 'DISTRIBUTED'
    
    @classmethod
    def all_statuses(cls):
        """Get list of all valid statuses as strings"""
        return [status.value for status in cls]
    
    @classmethod
    def is_valid(cls, status):
        """Check if a status string is valid"""
        return status in cls.all_statuses()


class OrthopedicSupplyCondition(Enum):
    """Conditions for orthopedic supplies"""
    NEW = 'NEW'
    VERY_GOOD = 'VERY_GOOD'
    GOOD = 'GOOD'
    
    @classmethod
    def all_conditions(cls):
        """Get list of all valid conditions as strings"""
        return [condition.value for condition in cls]
    
    @classmethod
    def is_valid(cls, condition):
        """Check if a condition string is valid"""
        return condition in cls.all_conditions()


class ActionType(Enum):
    """Types of user actions for audit logging"""
    REGISTERED = 'REGISTERED'
    LOGIN = 'LOGIN'
    LOGOUT = 'LOGOUT'
    MEDICINE_DECLARED = 'MEDICINE_DECLARED'
    MEDICINE_VERIFIED = 'MEDICINE_VERIFIED'
    MEDICINE_REJECTED = 'MEDICINE_REJECTED'
    MEDICINE_APPROVED = 'MEDICINE_APPROVED'
    MEDICINE_DISTRIBUTED = 'MEDICINE_DISTRIBUTED'
    SUPPLY_LISTED = 'SUPPLY_LISTED'
    SUPPLY_PURCHASED = 'SUPPLY_PURCHASED'
    
    @classmethod
    def all_actions(cls):
        """Get list of all valid actions as strings"""
        return [action.value for action in cls]