#!/usr/bin/env python
"""Start the TuniMed server"""
import sys
import traceback

if __name__ == '__main__':
    try:
        print("[*] Importing Flask app...")
        from app import app, db
        
        print("[*] Setting up database...")
        with app.app_context():
            db.create_all()
            print("[OK] Database setup complete")
        
        print("[*] Starting server on http://127.0.0.1:5000")
        print("[*] Press CTRL+C to quit")
        
        # This should block
        app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
        
    except KeyboardInterrupt:
        print("\n[*] Server shutting down...")
        sys.exit(0)
    except Exception as e:
        print("[ERROR] Startup failed: {}".format(str(e)))
        traceback.print_exc()
        sys.exit(1)

