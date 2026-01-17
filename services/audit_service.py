"""Audit service wrapper.

Provides a non-blocking integration point for audit logging. Audit writes
are best-effort: failures are swallowed to avoid impacting API latency or
user flows. For strict compliance scenarios, consider making audit writes
transactional or using an async queue.
"""
from utils import audit_logging


class AuditService:
    """Lightweight wrapper around `utils.audit_logging` that ensures audit
    failures do not block API responses."""

    @staticmethod
    def log_user_registration(user_id, role, details=None):
        try:
            return audit_logging.log_user_registration(user_id, role, details=details)
        except Exception:
            # Do not raise — audit must not affect API behavior
            return None

    @staticmethod
    def log_user_login(user_id, details=None):
        try:
            return audit_logging.log_user_login(user_id, details=details)
        except Exception:
            return None

    @staticmethod
    def log_medicine_declaration(user_id, medicine_id, medicine_name, is_imported, details=None):
        try:
            return audit_logging.log_medicine_declaration(user_id, medicine_id, medicine_name, is_imported, details=details)
        except Exception:
            return None

    @staticmethod
    def log_medicine_verification(user_id, medicine_id, verified, notes=None, details=None):
        try:
            return audit_logging.log_medicine_verification(user_id, medicine_id, verified, notes=notes, details=details)
        except Exception:
            return None

    @staticmethod
    def log_medicine_approval(user_id, medicine_id, approved, notes=None, details=None):
        try:
            return audit_logging.log_medicine_approval(user_id, medicine_id, approved, notes=notes, details=details)
        except Exception:
            return None
