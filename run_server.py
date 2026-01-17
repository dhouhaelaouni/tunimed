#!/usr/bin/env python
"""Run the TuniMed Flask app directly"""
from app import app, db

if __name__ == '__main__':
    print("\n" + "="*70)
    print("  🚀 TuniMed API Server Starting")
    print("="*70)
    print("\n  Available at:")
    print("    http://localhost:5000/")
    print("    http://127.0.0.1:5000/")
    print("\n  Documentation:")
    print("    http://localhost:5000/apidocs")
    print("\n" + "="*70 + "\n")
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    # Run server
    app.run(debug=False, host='0.0.0.0', port=5000, use_reloader=False)
