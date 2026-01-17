"""Email utilities for TuniMed"""
from flask_mail import Message
from flask import current_app


def send_declaration_email(user_email, user_name, declaration_code, pharmacy_name, pharmacy_address):
    """
    Send declaration confirmation email to the user.
    
    Args:
        user_email: Email address of the declarer
        user_name: Name of the declarer
        declaration_code: Unique code for the declaration
        pharmacy_name: Name of assigned pharmacy
        pharmacy_address: Address of assigned pharmacy
    """
    try:
        subject = "TuniMed: Medicine Declaration Confirmation"
        
        body = """
Hello {user_name},

Thank you for declaring your medicine with TuniMed!

DECLARATION DETAILS:
- Declaration Code: {declaration_code}
- Status: Awaiting Pharmacy Verification

YOUR ASSIGNED PHARMACY:
- Name: {pharmacy_name}
- Address: {pharmacy_address}

Please contact the pharmacy with your declaration code to arrange physical verification.

IMPORTANT: TuniMed does not provide medical advice. Verification is performed by qualified pharmacists.

For more information, visit: https://tunimed.tn

Best regards,
TuniMed Team
""".format(
            user_name=user_name,
            declaration_code=declaration_code,
            pharmacy_name=pharmacy_name,
            pharmacy_address=pharmacy_address
        )
        
        msg = Message(
            subject=subject,
            recipients=[user_email],
            body=body,
            sender=current_app.config.get('MAIL_DEFAULT_SENDER', 'noreply@tunimed.tn')
        )
        
        from app import mail
        mail.send(msg)
        return True, "Email sent successfully"
        
    except Exception as e:
        error_msg = str(e)
        print(f"[WARNING] Failed to send email to {user_email}: {error_msg}")
        return False, error_msg


def send_verification_complete_email(user_email, user_name, declaration_code, status):
    """
    Send verification completion email to the declarer.
    
    Args:
        user_email: Email address of the declarer
        user_name: Name of the declarer
        declaration_code: Declaration code
        status: Verification status (VERIFIED or REJECTED)
    """
    try:
        if status == "VERIFIED":
            subject = "TuniMed: Medicine Verification Approved"
            body_text = """
Hello {user_name},

Great news! Your medicine has been verified by a pharmacist.

DECLARATION CODE: {declaration_code}
STATUS: PHARMACY VERIFIED

Your medicine is now available for redistribution to eligible health facilities.

Thank you for contributing to TuniMed!

Best regards,
TuniMed Team
"""
        else:
            subject = "TuniMed: Medicine Verification Update"
            body_text = """
Hello {user_name},

Your medicine declaration has been reviewed by a pharmacist.

DECLARATION CODE: {declaration_code}
STATUS: PHARMACY VERIFICATION UNSUCCESSFUL

Please contact the pharmacy for more information about the verification result.

Best regards,
TuniMed Team
"""
        
        body = body_text.format(
            user_name=user_name,
            declaration_code=declaration_code
        )
        
        msg = Message(
            subject=subject,
            recipients=[user_email],
            body=body,
            sender=current_app.config.get('MAIL_DEFAULT_SENDER', 'noreply@tunimed.tn')
        )
        
        from app import mail
        mail.send(msg)
        return True, "Email sent successfully"
        
    except Exception as e:
        error_msg = str(e)
        print(f"[WARNING] Failed to send verification email to {user_email}: {error_msg}")
        return False, error_msg
