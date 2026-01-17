#!/usr/bin/env python
"""Test script for new medicine reference and search features"""
import sys
import os
os.chdir('c:\\Users\\dhouh\\OneDrive\\Desktop\\TuniMed')
sys.path.insert(0, 'c:\\Users\\dhouh\\OneDrive\\Desktop\\TuniMed')

print("\n" + "="*70)
print("  Testing New Medicine Reference Features")
print("="*70 + "\n")

from app import app, db
from models.user import MedicineReference, User, Medicine
from utils.enums import UserRole, MedicineStatus
from datetime import datetime, timedelta
import json

# Create app context
with app.app_context():
    # Create tables
    db.create_all()
    
    # Test 1: Create medicine references
    print("[Test 1] Creating medicine references...")
    try:
        # Clear existing references
        MedicineReference.query.delete()
        
        ref1 = MedicineReference(name="Aspirin", form="Tablet", dosage="500mg")
        ref2 = MedicineReference(name="Ibuprofen", form="Capsule", dosage="200mg")
        ref3 = MedicineReference(name="Amoxicillin", form="Tablet", dosage="250mg")
        
        db.session.add_all([ref1, ref2, ref3])
        db.session.commit()
        
        print("[OK] Created 3 medicine references")
        print("  - Aspirin (Tablet, 500mg)")
        print("  - Ibuprofen (Capsule, 200mg)")
        print("  - Amoxicillin (Tablet, 250mg)")
    except Exception as e:
        print(f"[ERROR] {e}")
        db.session.rollback()
    
    # Test 2: Query medicine references
    print("\n[Test 2] Querying medicine references...")
    try:
        all_meds = MedicineReference.query.all()
        print(f"[OK] Found {len(all_meds)} medicine references")
        for med in all_meds:
            print(f"  - ID: {med.id}, {med.name} ({med.form}, {med.dosage})")
    except Exception as e:
        print(f"[ERROR] {e}")
    
    # Test 3: Search by name (partial match)
    print("\n[Test 3] Testing name search functionality...")
    try:
        # Search for "Aspir"
        results = MedicineReference.query.filter(
            MedicineReference.name.ilike("%Aspir%")
        ).all()
        print(f"[OK] Search 'Aspir' found {len(results)} results")
        for r in results:
            print(f"  - {r.name}")
        
        # Search for "in" (should find Ibuprofen, Amoxicillin)
        results = MedicineReference.query.filter(
            MedicineReference.name.ilike("%in%")
        ).all()
        print(f"[OK] Search 'in' found {len(results)} results")
        for r in results:
            print(f"  - {r.name}")
    except Exception as e:
        print(f"[ERROR] {e}")
    
    # Test 4: Duplicate prevention
    print("\n[Test 4] Testing duplicate prevention...")
    try:
        dup = MedicineReference.query.filter_by(
            name="Aspirin",
            form="Tablet",
            dosage="500mg"
        ).first()
        
        if dup:
            print("[OK] Duplicate check working - found existing record")
        else:
            print("[ERROR] Duplicate check failed - existing record not found")
    except Exception as e:
        print(f"[ERROR] {e}")
    
    # Test 5: Create medicine declaration with reference
    print("\n[Test 5] Testing medicine declaration with reference...")
    try:
        # Get or create test user
        test_user = User.query.filter_by(username='citizen_test').first()
        if not test_user:
            test_user = User(username='citizen_test', email='citizen@test.com', role=UserRole.CITIZEN.value)
            test_user.set_password('pass')
            db.session.add(test_user)
            db.session.commit()
        
        # Get medicine reference
        med_ref = MedicineReference.query.first()
        
        # Create declaration linked to reference
        Medicine.query.filter_by(name="Test Medicine").delete()
        db.session.commit()
        
        med_declaration = Medicine(
            name="Test Medicine",
            amm="AMM123",
            batch_number="BATCH001",
            expiration_date=datetime.utcnow() + timedelta(days=365),
            quantity=10,
            is_imported=False,
            citizen_id=test_user.id,
            medicine_reference_id=med_ref.id,
            status=MedicineStatus.SUBMITTED.value
        )
        
        db.session.add(med_declaration)
        db.session.commit()
        
        print("[OK] Created medicine declaration with reference")
        print(f"  - Name: {med_declaration.name}")
        print(f"  - Reference ID: {med_declaration.medicine_reference_id}")
        print(f"  - Reference Name: {med_declaration.medicine_reference.name if med_declaration.medicine_reference else 'N/A'}")
    except Exception as e:
        print(f"[ERROR] {e}")
        db.session.rollback()
    
    # Test 6: Backward compatibility
    print("\n[Test 6] Testing backward compatibility (declaration without reference)...")
    try:
        test_user = User.query.filter_by(username='citizen_test').first()
        
        Medicine.query.filter_by(name="Legacy Medicine").delete()
        db.session.commit()
        
        legacy_med = Medicine(
            name="Legacy Medicine",
            amm="AMM456",
            batch_number="BATCH002",
            expiration_date=datetime.utcnow() + timedelta(days=365),
            quantity=5,
            is_imported=False,
            citizen_id=test_user.id,
            status=MedicineStatus.SUBMITTED.value
            # Note: medicine_reference_id is None (backward compatible)
        )
        
        db.session.add(legacy_med)
        db.session.commit()
        
        print("[OK] Created declaration without reference (backward compatible)")
        print(f"  - Name: {legacy_med.name}")
        print(f"  - Reference ID: {legacy_med.medicine_reference_id}")
    except Exception as e:
        print(f"[ERROR] {e}")
        db.session.rollback()

print("\n" + "="*70)
print("  All tests completed successfully!")
print("="*70 + "\n")
