"""
Scheduled tasks for TuniMed application using Flask-APScheduler.
Handles automatic expiration handling and other recurring operations.
"""

from datetime import datetime
from flask import current_app
from models.user import MedicineProposition, Medicine
from db import db


def mark_expired_propositions():
    """
    Daily scheduled job to mark expired medicine propositions as EXPIRED and deactivate them.
    
    Criteria:
    - status = 'AVAILABLE' (not yet distributed)
    - is_active = true (not already deactivated)
    - expiration_date < current datetime
    
    Updates:
    - status = 'EXPIRED'
    - is_active = false
    - expired_at = current timestamp
    
    No records are hard-deleted; all changes are soft deletes with timestamps.
    """
    try:
        with current_app.app_context():
            current_time = datetime.utcnow()
            
            # Find all active, available propositions with expired medicines
            expired_propositions = db.session.query(MedicineProposition).join(
                Medicine, 
                MedicineProposition.medicine_declaration_id == Medicine.id
            ).filter(
                MedicineProposition.status == 'AVAILABLE',
                MedicineProposition.is_active == True,
                Medicine.expiration_date < current_time
            ).all()
            
            if not expired_propositions:
                print(f"[{current_time.isoformat()}] No expired propositions found")
                return
            
            # Mark each as expired
            for proposition in expired_propositions:
                proposition.status = 'EXPIRED'
                proposition.is_active = False
                proposition.expired_at = current_time
                proposition.updated_at = current_time
            
            db.session.commit()
            print(
                f"[{current_time.isoformat()}] Successfully marked {len(expired_propositions)} "
                f"propositions as expired"
            )
            
    except Exception as e:
        print(
            f"[{datetime.utcnow().isoformat()}] Error in mark_expired_propositions: {str(e)}"
        )
        db.session.rollback()


def init_scheduler(app):
    """
    Initialize the APScheduler with the Flask app.
    
    Args:
        app: Flask application instance
    """
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.cron import CronTrigger
    
    scheduler = BackgroundScheduler()
    
    # Schedule the expiration task to run daily at midnight
    scheduler.add_job(
        func=mark_expired_propositions,
        trigger=CronTrigger(hour=0, minute=0),
        id='mark_expired_propositions',
        name='Mark expired medicine propositions',
        replace_existing=True
    )
    
    scheduler.start()
    
    print("[OK] Scheduler initialized successfully")
    print(f"[OK] Jobs scheduled: {len(scheduler.get_jobs())}")
    
    return scheduler
