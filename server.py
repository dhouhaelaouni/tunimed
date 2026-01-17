#!/usr/bin/env python
"""Simple server startup"""
import sys
import traceback

try:
    print("\n[*] Importing app...")
    from app import app, db
    
    print("[*] Creating database tables...")
    with app.app_context():
        db.create_all()
        print("[OK] Database tables created")
    
    print("[*] Starting Flask server on http://127.0.0.1:5000")
    print("[*] Documentation available at http://127.0.0.1:5000/apidocs")
    print("[*] Press CTRL+C to quit\n")
    
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
    
except Exception as e:
    print("[ERROR] {}".format(e))
    traceback.print_exc()
    sys.exit(1)


