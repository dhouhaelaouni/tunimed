from db import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from utils.enums import UserRole, MedicineStatus


class MedicineReference(db.Model):
    """MedicineReference model - Reference database of medicines for linking declarations"""
    __tablename__ = "medicine_references"
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Indexed name for fast searching
    name = db.Column(db.String(200), nullable=False, index=True)
    
    # Additional medicine information
    form = db.Column(db.String(100), nullable=False)  # e.g., "Tablet", "Capsule", "Liquid"
    dosage = db.Column(db.String(100), nullable=False)  # e.g., "500mg", "10ml"
    
    # Timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships - medicines linked to this reference
    medicine_declarations = db.relationship('Medicine', back_populates='medicine_reference', foreign_keys='Medicine.medicine_reference_id')
    
    def to_dict(self):
        """Convert medicine reference to dictionary representation"""
        return {
            'id': self.id,
            'name': self.name,
            'form': self.form,
            'dosage': self.dosage,
            'created_at': self.created_at.isoformat()
        }


class Pharmacy(db.Model):
    """Pharmacy model - Represents pharmacies that verify medicine declarations"""
    __tablename__ = "pharmacies"
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Pharmacy information
    name = db.Column(db.String(200), nullable=False, unique=True)
    address = db.Column(db.String(300), nullable=False)
    city = db.Column(db.String(100), nullable=False, default='Tunis')  # City location
    
    # Relationships
    medicine_declarations = db.relationship('Medicine', back_populates='assigned_pharmacy')
    
    # Timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        """Convert pharmacy to dictionary representation"""
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'city': self.city,
            'created_at': self.created_at.isoformat()
        }


class User(db.Model):
    """User model - Represents system users with different roles"""
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Role-based access control: Uses UserRole enum
    role = db.Column(db.String(20), default=UserRole.CITIZEN.value, nullable=False)
    
    # User status and metadata
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    medicine_declarations = db.relationship('Medicine', back_populates='citizen', foreign_keys='Medicine.citizen_id')
    audit_logs = db.relationship('AuditLog', back_populates='user')
    orthopedic_supplies = db.relationship('OrthopedicSupply', back_populates='donor')
    
    def set_password(self, password):
        """Hash and set the user's password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify the provided password against the stored hash"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert user to dictionary representation"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }


class Medicine(db.Model):
    """Medicine model - Represents medicine declarations in the system"""
    __tablename__ = "medicines"
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Link to medicine reference (optional - for backward compatibility)
    medicine_reference_id = db.Column(db.Integer, db.ForeignKey('medicine_references.id'), nullable=True)
    medicine_reference = db.relationship('MedicineReference', back_populates='medicine_declarations')
    
    # Basic medicine information
    name = db.Column(db.String(200), nullable=False)
    amm = db.Column(db.String(50), nullable=False)  # Autorisation de Mise sur le Marché (Market Authorization)
    batch_number = db.Column(db.String(100), nullable=False)
    expiration_date = db.Column(db.DateTime, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    
    # Medicine origin - local or imported
    is_imported = db.Column(db.Boolean, default=False, nullable=False)
    country_of_origin = db.Column(db.String(100), nullable=True)
    
    # Status workflow: Uses MedicineStatus enum
    # SUBMITTED, PHARMACY_VERIFIED, PHARMACY_REJECTED, APPROVED_FOR_REDISTRIBUTION, 
    # RESTRICTED_USE, REJECTED_REGULATORY, DISTRIBUTED
    status = db.Column(db.String(50), default=MedicineStatus.SUBMITTED.value, nullable=False)
    
    # Unique declaration code (generated on creation)
    declaration_code = db.Column(db.String(50), unique=True, nullable=True, index=True)
    
    # Pharmacy assignment for verification
    pharmacy_id = db.Column(db.Integer, db.ForeignKey('pharmacies.id'), nullable=True)
    assigned_pharmacy = db.relationship('Pharmacy', back_populates='medicine_declarations')
    
    # Citizen who declared the medicine
    citizen_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    citizen = db.relationship('User', back_populates='medicine_declarations', foreign_keys=[citizen_id])
    
    # Safety rating (internal, not shown to users)
    safety_rating = db.Column(db.Integer, default=100, nullable=False)  # 0-100 scale
    
    # Pharmacy verification
    pharmacy_verified_at = db.Column(db.DateTime, nullable=True)
    pharmacy_verified_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    pharmacy_notes = db.Column(db.Text, nullable=True)
    
    # Regulatory validation
    regulatory_validated_at = db.Column(db.DateTime, nullable=True)
    regulatory_validated_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    regulatory_notes = db.Column(db.Text, nullable=True)
    is_recalled = db.Column(db.Boolean, default=False, nullable=False)
    
    # Audit trail
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def is_expired(self):
        """Check if medicine has expired"""
        return datetime.utcnow() > self.expiration_date
    
    def can_be_redistributed(self):
        """Check if medicine is eligible for redistribution based on safety rules"""
        # Cannot redistribute if expired
        if self.is_expired():
            return False
        
        # Cannot redistribute imported medicines
        if self.is_imported:
            return False
        
        # Cannot redistribute recalled medicines
        if self.is_recalled:
            return False
        
        # Must be approved or restricted use
        if self.status not in [MedicineStatus.APPROVED_FOR_REDISTRIBUTION.value, MedicineStatus.RESTRICTED_USE.value]:
            return False
        
        return True
    
    def to_dict(self, include_sensitive=False):
        """Convert medicine to dictionary representation"""
        data = {
            'id': self.id,
            'name': self.name,
            'amm': self.amm,
            'batch_number': self.batch_number,
            'expiration_date': self.expiration_date.isoformat(),
            'quantity': self.quantity,
            'is_imported': self.is_imported,
            'country_of_origin': self.country_of_origin,
            'status': self.status,
            'is_expired': self.is_expired(),
            'can_be_redistributed': self.can_be_redistributed(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        
        # Include safety rating only if requested (internal use)
        if include_sensitive:
            data['safety_rating'] = self.safety_rating
            data['pharmacy_notes'] = self.pharmacy_notes
            data['regulatory_notes'] = self.regulatory_notes
            data['is_recalled'] = self.is_recalled
        
        return data


class MedicineProposition(db.Model):
    """MedicineProposition model - Represents verified medicines available for redistribution (public-facing)"""
    __tablename__ = "medicine_propositions"
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Reference to the verified medicine declaration
    medicine_declaration_id = db.Column(db.Integer, db.ForeignKey('medicines.id'), nullable=False)
    medicine_declaration = db.relationship('Medicine')
    
    # Status - can be AVAILABLE, DISTRIBUTED, EXPIRED
    status = db.Column(db.String(50), default='AVAILABLE', nullable=False)
    
    # Soft delete and expiration
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    expired_at = db.Column(db.DateTime, nullable=True)  # When the medicine expired
    
    # Health facility that requested the medicine
    requesting_facility_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    requesting_facility = db.relationship('User', foreign_keys=[requesting_facility_id])
    requested_at = db.Column(db.DateTime, nullable=True)  # When the request was made
    
    # Timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        """Convert medicine proposition to dictionary representation"""
        med = self.medicine_declaration
        return {
            'id': self.id,
            'proposition_id': self.id,
            'medicine': {
                'id': med.id,
                'name': med.name,
                'amm': med.amm,
                'batch_number': med.batch_number,
                'expiration_date': med.expiration_date.isoformat(),
                'quantity': med.quantity,
                'is_imported': med.is_imported,
                'country_of_origin': med.country_of_origin
            },
            'status': self.status,
            'is_active': self.is_active,
            'expired_at': self.expired_at.isoformat() if self.expired_at else None,
            'available_at': med.assigned_pharmacy.to_dict() if med.assigned_pharmacy else None,
            'requesting_facility': self.requesting_facility.username if self.requesting_facility else None,
            'requested_at': self.requested_at.isoformat() if self.requested_at else None,
            'created_at': self.created_at.isoformat()
        }


class AuditLog(db.Model):
    """AuditLog model - Immutable logging of all system actions for GDPR compliance"""
    __tablename__ = "audit_logs"
    
    id = db.Column(db.Integer, primary_key=True)
    
    # User who performed the action
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', back_populates='audit_logs')
    
    # Action details
    action = db.Column(db.String(200), nullable=False)  # e.g., "MEDICINE_DECLARED", "MEDICINE_VERIFIED"
    entity_type = db.Column(db.String(50), nullable=False)  # e.g., "MEDICINE", "USER"
    entity_id = db.Column(db.Integer, nullable=True)
    
    # Changes made (JSON format for flexibility)
    details = db.Column(db.JSON, nullable=True)
    
    # Timestamp (immutable)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        """Convert audit log to dictionary representation"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'action': self.action,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'details': self.details,
            'created_at': self.created_at.isoformat()
        }


class OrthopedicSupply(db.Model):
    """OrthopedicSupply model - Represents orthopedic supplies (not medicines)"""
    __tablename__ = "orthopedic_supplies"
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Basic information
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    # Condition: NEW, VERY_GOOD, GOOD
    condition = db.Column(db.String(20), nullable=False)  # Enum-like: NEW, VERY_GOOD, GOOD
    quantity = db.Column(db.Integer, nullable=False)  # Must be > 0
    
    # Sale or donation
    is_for_sale = db.Column(db.Boolean, default=False, nullable=False)
    price = db.Column(db.Float, nullable=True)  # Only if is_for_sale is True
    
    # Soft delete
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    deactivated_at = db.Column(db.DateTime, nullable=True)
    
    # Donor who contributed the supply
    donor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    donor = db.relationship('User', back_populates='orthopedic_supplies')
    
    # Timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        """Convert orthopedic supply to dictionary representation"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'condition': self.condition,
            'quantity': self.quantity,
            'is_for_sale': self.is_for_sale,
            'price': self.price,
            'donor_id': self.donor_id,
            'donor_username': self.donor.username if self.donor else None,
            'is_active': self.is_active,
            'deactivated_at': self.deactivated_at.isoformat() if self.deactivated_at else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


# Utility function to create test users
def create_test_users():
    """Create default test users and pharmacies for development"""
    db.create_all()
    
    # Create test pharmacies
    if Pharmacy.query.filter_by(name='Central Pharmacy Tunis').first() is None:
        pharmacy1 = Pharmacy(
            name='Central Pharmacy Tunis',
            address='123 Avenue Habib Bourguiba, Tunis 1000',
            city='Tunis'
        )
        pharmacy2 = Pharmacy(
            name='Pharmacy Lac Tunis',
            address='456 Rue du Lac, Tunis 2000',
            city='Tunis'
        )
        pharmacy3 = Pharmacy(
            name='Pharmacy Carthage',
            address='789 Avenue Carthage, Tunis 2016',
            city='Carthage'
        )
        db.session.add_all([pharmacy1, pharmacy2, pharmacy3])
        db.session.commit()
        print("Created test pharmacies")
    
    # Test citizen
    if User.query.filter_by(username='citizen_test').first() is None:
        citizen = User(username='citizen_test', email='citizen@test.com', role=UserRole.CITIZEN.value)
        citizen.set_password('citizenpass')
        db.session.add(citizen)
        print("Created test citizen: citizen_test/citizenpass")
    
    # Test pharmacist
    if User.query.filter_by(username='pharmacist_test').first() is None:
        pharmacist = User(username='pharmacist_test', email='pharmacist@test.com', role=UserRole.PHARMACIST.value)
        pharmacist.set_password('pharmacistpass')
        db.session.add(pharmacist)
        print("Created test pharmacist: pharmacist_test/pharmacistpass")
    
    # Test regulatory agent
    if User.query.filter_by(username='regulatory_test').first() is None:
        regulatory = User(username='regulatory_test', email='regulatory@test.com', role=UserRole.REGULATORY_AGENT.value)
        regulatory.set_password('regulatorypass')
        db.session.add(regulatory)
        print("Created test regulatory agent: regulatory_test/regulatorypass")
    
    # Test health facility
    if User.query.filter_by(username='healthfacility_test').first() is None:
        health_facility = User(username='healthfacility_test', email='facility@test.com', role=UserRole.HEALTH_FACILITY.value)
        health_facility.set_password('facilitypass')
        db.session.add(health_facility)
        print("Created test health facility: healthfacility_test/facilitypass")
    
    # Test admin
    if User.query.filter_by(username='admin').first() is None:
        admin = User(username='admin', email='admin@test.com', role=UserRole.ADMIN.value)
        admin.set_password('adminpass')
        db.session.add(admin)
        print("Created test admin: admin/adminpass")
    
    db.session.commit()

