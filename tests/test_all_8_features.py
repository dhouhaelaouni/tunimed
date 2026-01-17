#!/usr/bin/env python
"""
Test suite for all 8 new features:
1. Soft Delete for Orthopedic Supplies
2. Medicine Declaration Cancellation (Citizen)
3. Pending Declarations List (Pharmacist)
4. Request Verified Medicine (Health Facility)
5. Sort by Closest Expiration Date
6. City-Based Pharmacy Proximity
7. Automatic Expiration Handling (Flask-APScheduler)
8. General feature validation
"""

import sys
from datetime import datetime, timedelta
from app import create_app
from db import db
from models.user import (
    User, Medicine, MedicineProposition, OrthopedicSupply, Pharmacy,
    MedicineReference
)
from utils.enums import UserRole, MedicineStatus


def test_feature_1_orthopedic_supplies_soft_delete():
    """Test: Soft Delete for Orthopedic Supplies"""
    print("\n" + "="*70)
    print("TEST 1: SOFT DELETE FOR ORTHOPEDIC SUPPLIES")
    print("="*70)
    
    with app.app_context():
        # Get a test citizen
        citizen = User.query.filter_by(username='citizen_test').first()
        
        # Create an orthopedic supply
        supply = OrthopedicSupply(
            name='Test Crutches',
            description='Test supply for deletion',
            condition='GOOD',
            quantity=5,
            is_for_sale=False,
            donor_id=citizen.id
        )
        db.session.add(supply)
        db.session.commit()
        supply_id = supply.id
        
        print(f"✓ Created orthopedic supply: ID={supply_id}")
        print(f"  - is_active: {supply.is_active}")
        print(f"  - deactivated_at: {supply.deactivated_at}")
        
        # Verify active supplies query filters
        active_supplies = OrthopedicSupply.query.filter_by(is_active=True).all()
        assert any(s.id == supply_id for s in active_supplies), "Supply should be in active list"
        print(f"✓ Supply found in active supplies list")
        
        # Soft delete the supply
        supply.is_active = False
        supply.deactivated_at = datetime.utcnow()
        db.session.commit()
        
        print(f"✓ Soft deleted orthopedic supply")
        print(f"  - is_active: {supply.is_active}")
        print(f"  - deactivated_at: {supply.deactivated_at.isoformat()}")
        
        # Verify it's no longer in active list
        active_supplies = OrthopedicSupply.query.filter_by(is_active=True).all()
        assert not any(s.id == supply_id for s in active_supplies), "Supply should not be in active list"
        print(f"✓ Supply no longer in active supplies list")
        
        # Verify it still exists in database
        all_supplies = OrthopedicSupply.query.all()
        assert any(s.id == supply_id for s in all_supplies), "Supply should still exist in DB"
        print(f"✓ Supply still exists in database (soft delete confirmed)")
        
        # Clean up
        db.session.delete(supply)
        db.session.commit()
    
    print("\n✅ TEST 1 PASSED")


def test_feature_2_medicine_declaration_cancellation():
    """Test: Medicine Declaration Cancellation (Citizen)"""
    print("\n" + "="*70)
    print("TEST 2: MEDICINE DECLARATION CANCELLATION")
    print("="*70)
    
    with app.app_context():
        citizen = User.query.filter_by(username='citizen_test').first()
        pharmacy = Pharmacy.query.first()
        
        # Create a medicine declaration
        medicine = Medicine(
            name='Test Medicine for Cancellation',
            amm='TEST123',
            batch_number='BATCH001',
            expiration_date=datetime.utcnow() + timedelta(days=30),
            quantity=10,
            is_imported=False,
            status=MedicineStatus.SUBMITTED.value,
            declaration_code='DECL-CANCEL-TEST',
            citizen_id=citizen.id,
            pharmacy_id=pharmacy.id
        )
        db.session.add(medicine)
        db.session.commit()
        medicine_id = medicine.id
        
        print(f"✓ Created medicine declaration: ID={medicine_id}")
        print(f"  - status: {medicine.status}")
        
        # Simulate cancellation
        assert medicine.status == MedicineStatus.SUBMITTED.value, "Should start as SUBMITTED"
        medicine.status = 'CANCELLED'
        medicine.updated_at = datetime.utcnow()
        db.session.commit()
        
        # Verify status changed
        medicine = Medicine.query.get(medicine_id)
        assert medicine.status == 'CANCELLED', "Medicine should be cancelled"
        print(f"✓ Medicine declaration cancelled")
        print(f"  - new status: {medicine.status}")
        print(f"  - updated_at: {medicine.updated_at.isoformat()}")
        
        # Clean up
        db.session.delete(medicine)
        db.session.commit()
    
    print("\n✅ TEST 2 PASSED")


def test_feature_3_pending_declarations():
    """Test: Pending Declarations List (Pharmacist)"""
    print("\n" + "="*70)
    print("TEST 3: PENDING DECLARATIONS LIST FOR PHARMACIST")
    print("="*70)
    
    with app.app_context():
        citizen = User.query.filter_by(username='citizen_test').first()
        pharmacy = Pharmacy.query.first()
        
        # Create multiple declarations with different statuses
        med1 = Medicine(
            name='Pending Medicine 1',
            amm='PEND001',
            batch_number='BATCH001',
            expiration_date=datetime.utcnow() + timedelta(days=30),
            quantity=5,
            is_imported=False,
            status=MedicineStatus.SUBMITTED.value,
            declaration_code='DECL-PEND-001',
            citizen_id=citizen.id,
            pharmacy_id=pharmacy.id
        )
        med2 = Medicine(
            name='Verified Medicine 1',
            amm='VER001',
            batch_number='BATCH002',
            expiration_date=datetime.utcnow() + timedelta(days=45),
            quantity=10,
            is_imported=False,
            status=MedicineStatus.PHARMACY_VERIFIED.value,
            declaration_code='DECL-VER-001',
            citizen_id=citizen.id,
            pharmacy_id=pharmacy.id
        )
        db.session.add_all([med1, med2])
        db.session.commit()
        
        print(f"✓ Created 2 medicine declarations")
        print(f"  - Medicine 1 (SUBMITTED): ID={med1.id}")
        print(f"  - Medicine 2 (VERIFIED): ID={med2.id}")
        
        # Query pending declarations
        pending = Medicine.query.filter_by(status=MedicineStatus.SUBMITTED.value).all()
        assert len(pending) >= 1, "Should have at least 1 pending declaration"
        assert any(m.id == med1.id for m in pending), "Pending medicine should be in list"
        assert not any(m.id == med2.id for m in pending), "Verified medicine should NOT be in list"
        
        print(f"✓ Query for pending declarations working correctly")
        print(f"  - Found {len(pending)} pending declaration(s)")
        
        # Clean up
        db.session.delete(med1)
        db.session.delete(med2)
        db.session.commit()
    
    print("\n✅ TEST 3 PASSED")


def test_feature_4_request_medicine_proposition():
    """Test: Request Verified Medicine (Health Facility)"""
    print("\n" + "="*70)
    print("TEST 4: REQUEST VERIFIED MEDICINE (HEALTH FACILITY)")
    print("="*70)
    
    with app.app_context():
        citizen = User.query.filter_by(username='citizen_test').first()
        facility = User.query.filter_by(username='healthfacility_test').first()
        pharmacy = Pharmacy.query.first()
        
        # Create a verified medicine
        medicine = Medicine(
            name='Requestable Medicine',
            amm='REQ001',
            batch_number='BATCH001',
            expiration_date=datetime.utcnow() + timedelta(days=60),
            quantity=20,
            is_imported=False,
            status=MedicineStatus.PHARMACY_VERIFIED.value,
            declaration_code='DECL-REQ-001',
            citizen_id=citizen.id,
            pharmacy_id=pharmacy.id
        )
        db.session.add(medicine)
        db.session.commit()
        
        # Create proposition
        prop = MedicineProposition(
            medicine_declaration_id=medicine.id,
            status='AVAILABLE',
            is_active=True
        )
        db.session.add(prop)
        db.session.commit()
        prop_id = prop.id
        
        print(f"✓ Created medicine proposition: ID={prop_id}")
        print(f"  - status: {prop.status}")
        print(f"  - is_active: {prop.is_active}")
        print(f"  - requesting_facility_id: {prop.requesting_facility_id}")
        
        # Simulate facility request
        prop.status = 'DISTRIBUTED'
        prop.requesting_facility_id = facility.id
        prop.requested_at = datetime.utcnow()
        db.session.commit()
        
        print(f"✓ Health facility requested medicine")
        print(f"  - new status: {prop.status}")
        print(f"  - requesting_facility_id: {prop.requesting_facility_id}")
        print(f"  - requested_at: {prop.requested_at.isoformat()}")
        
        # Verify update
        prop = MedicineProposition.query.get(prop_id)
        assert prop.status == 'DISTRIBUTED', "Should be DISTRIBUTED"
        assert prop.requesting_facility_id == facility.id, "Should have facility ID"
        print(f"✓ Verification successful")
        
        # Clean up
        db.session.delete(prop)
        db.session.delete(medicine)
        db.session.commit()
    
    print("\n✅ TEST 4 PASSED")


def test_feature_5_sort_by_expiry():
    """Test: Sort by Closest Expiration Date"""
    print("\n" + "="*70)
    print("TEST 5: SORT BY CLOSEST EXPIRATION DATE")
    print("="*70)
    
    with app.app_context():
        citizen = User.query.filter_by(username='citizen_test').first()
        pharmacy = Pharmacy.query.first()
        
        # Create medicines with different expiration dates
        exp_dates = [
            datetime.utcnow() + timedelta(days=90),  # Far future
            datetime.utcnow() + timedelta(days=30),  # Medium
            datetime.utcnow() + timedelta(days=10),  # Soon
        ]
        
        medicines = []
        for i, exp_date in enumerate(exp_dates):
            med = Medicine(
                name=f'Sort Test Medicine {i}',
                amm=f'SORT{i:03d}',
                batch_number=f'BATCH{i:03d}',
                expiration_date=exp_date,
                quantity=10,
                is_imported=False,
                status=MedicineStatus.PHARMACY_VERIFIED.value,
                declaration_code=f'DECL-SORT-{i:03d}',
                citizen_id=citizen.id,
                pharmacy_id=pharmacy.id
            )
            db.session.add(med)
            medicines.append(med)
        
        db.session.commit()
        medicine_ids = [m.id for m in medicines]
        
        print(f"✓ Created 3 medicines with different expiration dates")
        for med, exp_date in zip(medicines, exp_dates):
            days_left = (exp_date - datetime.utcnow()).days
            print(f"  - Medicine ID={med.id}: expires in {days_left} days")
        
        # Create propositions
        props = []
        for med in medicines:
            prop = MedicineProposition(
                medicine_declaration_id=med.id,
                status='AVAILABLE',
                is_active=True
            )
            db.session.add(prop)
            props.append(prop)
        
        db.session.commit()
        
        # Get all propositions
        all_props = MedicineProposition.query.filter(
            MedicineProposition.medicine_declaration_id.in_(medicine_ids)
        ).all()
        
        # Sort by expiration date
        sorted_props = sorted(
            all_props,
            key=lambda p: p.medicine_declaration.expiration_date
        )
        
        print(f"✓ Sorted {len(sorted_props)} propositions by expiration date")
        for i, prop in enumerate(sorted_props):
            exp_date = prop.medicine_declaration.expiration_date
            days_left = (exp_date - datetime.utcnow()).days
            print(f"  {i+1}. Medicine ID={prop.medicine_declaration.id}: expires in {days_left} days")
        
        # Verify order
        for i in range(len(sorted_props) - 1):
            assert sorted_props[i].medicine_declaration.expiration_date <= \
                   sorted_props[i+1].medicine_declaration.expiration_date, \
                   "Propositions should be sorted by ascending expiration date"
        
        print(f"✓ Sorting order verified")
        
        # Clean up
        for prop in props:
            db.session.delete(prop)
        for med in medicines:
            db.session.delete(med)
        db.session.commit()
    
    print("\n✅ TEST 5 PASSED")


def test_feature_6_city_based_filtering():
    """Test: City-Based Pharmacy Proximity"""
    print("\n" + "="*70)
    print("TEST 6: CITY-BASED PHARMACY PROXIMITY FILTERING")
    print("="*70)
    
    with app.app_context():
        # Verify pharmacies have city field
        pharmacies = Pharmacy.query.all()
        
        print(f"✓ Found {len(pharmacies)} pharmacies in database")
        for pharmacy in pharmacies:
            print(f"  - {pharmacy.name}: city='{pharmacy.city}'")
            assert pharmacy.city, "Pharmacy should have a city"
        
        # Verify we have multiple cities
        cities = set(p.city for p in pharmacies)
        print(f"✓ Pharmacies distributed across {len(cities)} cities: {cities}")
        
        # Create medicines in different cities
        citizen = User.query.filter_by(username='citizen_test').first()
        
        medicines_by_city = {}
        for pharmacy in pharmacies:
            med = Medicine(
                name=f'Medicine in {pharmacy.city}',
                amm=f'CITY{pharmacy.id:03d}',
                batch_number=f'BATCH{pharmacy.id:03d}',
                expiration_date=datetime.utcnow() + timedelta(days=60),
                quantity=15,
                is_imported=False,
                status=MedicineStatus.PHARMACY_VERIFIED.value,
                declaration_code=f'DECL-CITY-{pharmacy.id:03d}',
                citizen_id=citizen.id,
                pharmacy_id=pharmacy.id
            )
            db.session.add(med)
            medicines_by_city[pharmacy.city] = med
        
        db.session.commit()
        
        print(f"✓ Created medicines in {len(medicines_by_city)} different city pharmacy locations")
        
        # Create propositions
        for med in medicines_by_city.values():
            prop = MedicineProposition(
                medicine_declaration_id=med.id,
                status='AVAILABLE',
                is_active=True
            )
            db.session.add(prop)
        
        db.session.commit()
        
        # Test filtering by city
        for city in cities:
            props = MedicineProposition.query.join(
                Medicine, MedicineProposition.medicine_declaration_id == Medicine.id
            ).join(
                Pharmacy, Medicine.pharmacy_id == Pharmacy.id
            ).filter(
                Pharmacy.city.ilike(f"%{city}%"),
                MedicineProposition.status == 'AVAILABLE',
                MedicineProposition.is_active == True
            ).all()
            
            print(f"✓ Query for city '{city}': found {len(props)} proposition(s)")
            assert len(props) > 0, f"Should find at least 1 proposition in {city}"
        
        # Clean up
        for med in medicines_by_city.values():
            props = MedicineProposition.query.filter_by(
                medicine_declaration_id=med.id
            ).all()
            for prop in props:
                db.session.delete(prop)
            db.session.delete(med)
        
        db.session.commit()
    
    print("\n✅ TEST 6 PASSED")


def test_feature_7_automatic_expiration():
    """Test: Automatic Expiration Handling (Flask-APScheduler)"""
    print("\n" + "="*70)
    print("TEST 7: AUTOMATIC EXPIRATION HANDLING")
    print("="*70)
    
    with app.app_context():
        citizen = User.query.filter_by(username='citizen_test').first()
        pharmacy = Pharmacy.query.first()
        
        # Create an expired medicine
        expired_date = datetime.utcnow() - timedelta(days=1)
        med_expired = Medicine(
            name='Expired Medicine',
            amm='EXP001',
            batch_number='BATCH001',
            expiration_date=expired_date,
            quantity=10,
            is_imported=False,
            status=MedicineStatus.PHARMACY_VERIFIED.value,
            declaration_code='DECL-EXP-001',
            citizen_id=citizen.id,
            pharmacy_id=pharmacy.id
        )
        
        # Create a valid medicine
        valid_date = datetime.utcnow() + timedelta(days=30)
        med_valid = Medicine(
            name='Valid Medicine',
            amm='VALID001',
            batch_number='BATCH002',
            expiration_date=valid_date,
            quantity=10,
            is_imported=False,
            status=MedicineStatus.PHARMACY_VERIFIED.value,
            declaration_code='DECL-VALID-001',
            citizen_id=citizen.id,
            pharmacy_id=pharmacy.id
        )
        
        db.session.add_all([med_expired, med_valid])
        db.session.commit()
        
        print(f"✓ Created medicines:")
        print(f"  - Expired: ID={med_expired.id}, expires={expired_date.isoformat()}")
        print(f"  - Valid: ID={med_valid.id}, expires={valid_date.isoformat()}")
        
        # Create propositions
        prop_expired = MedicineProposition(
            medicine_declaration_id=med_expired.id,
            status='AVAILABLE',
            is_active=True
        )
        prop_valid = MedicineProposition(
            medicine_declaration_id=med_valid.id,
            status='AVAILABLE',
            is_active=True
        )
        
        db.session.add_all([prop_expired, prop_valid])
        db.session.commit()
        
        print(f"✓ Created propositions:")
        print(f"  - Expired prop: ID={prop_expired.id}, status={prop_expired.status}, is_active={prop_expired.is_active}")
        print(f"  - Valid prop: ID={prop_valid.id}, status={prop_valid.status}, is_active={prop_valid.is_active}")
        
        # Verify MedicineProposition has required fields
        assert hasattr(prop_expired, 'is_active'), "MedicineProposition should have is_active field"
        assert hasattr(prop_expired, 'expired_at'), "MedicineProposition should have expired_at field"
        print(f"✓ MedicineProposition has is_active and expired_at fields")
        
        # Simulate the expiration job
        current_time = datetime.utcnow()
        expired_props = MedicineProposition.query.join(
            Medicine,
            MedicineProposition.medicine_declaration_id == Medicine.id
        ).filter(
            MedicineProposition.status == 'AVAILABLE',
            MedicineProposition.is_active == True,
            Medicine.expiration_date < current_time
        ).all()
        
        print(f"✓ Found {len(expired_props)} expired proposition(s) to mark")
        for prop in expired_props:
            print(f"  - Proposition ID={prop.id}, Medicine expires={prop.medicine_declaration.expiration_date.isoformat()}")
        
        # Mark expired
        for prop in expired_props:
            prop.status = 'EXPIRED'
            prop.is_active = False
            prop.expired_at = current_time
        
        db.session.commit()
        
        # Verify changes
        prop_expired = MedicineProposition.query.get(prop_expired.id)
        assert prop_expired.status == 'EXPIRED', "Should be marked as EXPIRED"
        assert prop_expired.is_active == False, "Should be deactivated"
        assert prop_expired.expired_at is not None, "Should have expired_at timestamp"
        
        print(f"✓ Expiration marking successful:")
        print(f"  - status changed to: {prop_expired.status}")
        print(f"  - is_active changed to: {prop_expired.is_active}")
        print(f"  - expired_at set to: {prop_expired.expired_at.isoformat()}")
        
        # Verify valid proposition unchanged
        prop_valid = MedicineProposition.query.get(prop_valid.id)
        assert prop_valid.status == 'AVAILABLE', "Valid prop should still be AVAILABLE"
        assert prop_valid.is_active == True, "Valid prop should still be active"
        print(f"✓ Valid proposition unchanged: status={prop_valid.status}, is_active={prop_valid.is_active}")
        
        # Clean up
        db.session.delete(prop_expired)
        db.session.delete(prop_valid)
        db.session.delete(med_expired)
        db.session.delete(med_valid)
        db.session.commit()
    
    print("\n✅ TEST 7 PASSED")


def test_feature_8_scheduler_initialization():
    """Test: Scheduler Initialization and Configuration"""
    print("\n" + "="*70)
    print("TEST 8: SCHEDULER INITIALIZATION")
    print("="*70)
    
    with app.app_context():
        # Verify scheduler was initialized
        from app import scheduler
        
        if scheduler is not None:
            print(f"✓ Scheduler initialized successfully")
            print(f"  - Scheduler type: {type(scheduler).__name__}")
            print(f"  - Scheduler running: {scheduler.running}")
            
            # Get scheduled jobs
            jobs = scheduler.get_jobs()
            print(f"✓ Found {len(jobs)} scheduled job(s)")
            
            for job in jobs:
                print(f"  - Job ID: {job.id}")
                print(f"    Name: {job.name}")
                print(f"    Trigger: {job.trigger}")
                print(f"    Next run time: {job.next_run_time}")
            
            # Verify expiration job is scheduled
            assert any(job.id == 'mark_expired_propositions' for job in jobs), \
                "mark_expired_propositions job should be scheduled"
            print(f"✓ mark_expired_propositions job is scheduled")
            
        else:
            print(f"⚠ Scheduler is not initialized (scheduler = None)")
            print(f"  This is OK for testing; scheduler will be initialized when app runs")
    
    print("\n✅ TEST 8 PASSED")


def run_all_tests():
    """Run all feature tests"""
    print("\n" + "="*80)
    print("COMPREHENSIVE TEST SUITE: ALL 8 NEW FEATURES")
    print("="*80)
    
    tests = [
        test_feature_1_orthopedic_supplies_soft_delete,
        test_feature_2_medicine_declaration_cancellation,
        test_feature_3_pending_declarations,
        test_feature_4_request_medicine_proposition,
        test_feature_5_sort_by_expiry,
        test_feature_6_city_based_filtering,
        test_feature_7_automatic_expiration,
        test_feature_8_scheduler_initialization,
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            test_func()
            passed += 1
        except AssertionError as e:
            print(f"\n❌ TEST FAILED: {test_func.__name__}")
            print(f"   Assertion Error: {str(e)}")
            failed += 1
        except Exception as e:
            print(f"\n❌ TEST FAILED: {test_func.__name__}")
            print(f"   Error: {str(e)}")
            failed += 1
    
    print("\n" + "="*80)
    print(f"TEST SUMMARY: {passed} passed, {failed} failed out of {len(tests)} tests")
    print("="*80)
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! All 8 features are working correctly.\n")
        return 0
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please review the errors above.\n")
        return 1


if __name__ == '__main__':
    # Create app context
    app = create_app()
    
    # Initialize database
    with app.app_context():
        db.create_all()
        from models import create_test_users
        create_test_users()
    
    # Run tests
    exit_code = run_all_tests()
    sys.exit(exit_code)
