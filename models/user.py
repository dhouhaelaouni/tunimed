from db import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from utils.enums import UserRole, MedicineStatus

class MedicineReference(db.Model):
    __tablename__ = "medicine_references"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    form = db.Column(db.String(100), nullable=False)
    dosage = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    medicine_declarations = db.relationship('Medicine', back_populates='medicine_reference', foreign_keys='Medicine.medicine_reference_id')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'form': self.form,
            'dosage': self.dosage,
            'created_at': self.created_at.isoformat()
        }

class Pharmacy(db.Model):
    __tablename__ = "pharmacies"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, unique=True)
    address = db.Column(db.String(300), nullable=False)
    city = db.Column(db.String(100), nullable=False, default='Tunis')
    medicine_declarations = db.relationship('Medicine', back_populates='assigned_pharmacy')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'city': self.city,
            'created_at': self.created_at.isoformat()
        }

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default=UserRole.CITIZEN.value, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    medicine_declarations = db.relationship('Medicine', back_populates='citizen', foreign_keys='Medicine.citizen_id')
    audit_logs = db.relationship('AuditLog', back_populates='user')
    orthopedic_supplies = db.relationship('OrthopedicSupply', back_populates='donor')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }

class Medicine(db.Model):
    __tablename__ = "medicines"
    id = db.Column(db.Integer, primary_key=True)
    medicine_reference_id = db.Column(db.Integer, db.ForeignKey('medicine_references.id'), nullable=True)
    medicine_reference = db.relationship('MedicineReference', back_populates='medicine_declarations')
    name = db.Column(db.String(200), nullable=False)
    amm = db.Column(db.String(50), nullable=False)
    batch_number = db.Column(db.String(100), nullable=False)
    expiration_date = db.Column(db.DateTime, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    is_imported = db.Column(db.Boolean, default=False, nullable=False)
    country_of_origin = db.Column(db.String(100), nullable=True)
    is_recalled = db.Column(db.Boolean, default=False, nullable=False)
    status = db.Column(db.String(50), default=MedicineStatus.SUBMITTED.value, nullable=False)
    citizen_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    citizen = db.relationship('User', back_populates='medicine_declarations', foreign_keys=[citizen_id])
    pharmacy_id = db.Column(db.Integer, db.ForeignKey('pharmacies.id'), nullable=True)
    assigned_pharmacy = db.relationship('Pharmacy', back_populates='medicine_declarations')
    pharmacy_verified_at = db.Column(db.DateTime, nullable=True)
    pharmacy_notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def is_expired(self):
        return datetime.utcnow() > self.expiration_date
    
    def to_dict(self, include_sensitive=False):
        data = {
            'id': self.id,
            'name': self.name,
            'expiration_date': self.expiration_date.isoformat() if self.expiration_date else None,
            'quantity': self.quantity,
            'status': self.status,
            'is_expired': self.is_expired(),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        if include_sensitive:
            data.update({
                "amm": self.amm,
                "batch_number": self.batch_number,
                "citizen_id": self.citizen_id,
                "pharmacy_notes": self.pharmacy_notes,
                "pharmacy_verified_at": self.pharmacy_verified_at.isoformat() if self.pharmacy_verified_at else None
            })
        return data

class MedicineProposition(db.Model):
    __tablename__ = "medicine_propositions"
    id = db.Column(db.Integer, primary_key=True)
    medicine_declaration_id = db.Column(db.Integer, db.ForeignKey('medicines.id'), nullable=False)
    medicine_declaration = db.relationship('Medicine')
    status = db.Column(db.String(50), default='AVAILABLE', nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    requesting_facility_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    requesting_facility = db.relationship('User', foreign_keys=[requesting_facility_id])
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        med = self.medicine_declaration
        return {
            'id': self.id,
            'medicine': med.to_dict() if med else None,
            'status': self.status,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }

class AuditLog(db.Model):
    __tablename__ = "audit_logs"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', back_populates='audit_logs')
    action = db.Column(db.String(200), nullable=False)
    entity_type = db.Column(db.String(50), nullable=False)
    entity_id = db.Column(db.Integer, nullable=True)
    details = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

class OrthopedicSupply(db.Model):
    __tablename__ = "orthopedic_supplies"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    condition = db.Column(db.String(20), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    is_for_sale = db.Column(db.Boolean, default=False, nullable=False)
    price = db.Column(db.Float, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False) # ✅ Default added
    donor_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    donor = db.relationship('User', back_populates='orthopedic_supplies')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "condition": self.condition,
            "quantity": self.quantity,
            "is_for_sale": self.is_for_sale,
            "price": self.price,
            "donor_id": self.donor_id,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

def create_test_users():
    db.create_all()
    if Pharmacy.query.filter_by(name='Central Pharmacy Tunis').first() is None:
        p1 = Pharmacy(name='Central Pharmacy Tunis', address='123 Avenue Habib Bourguiba', city='Tunis')
        db.session.add(p1)
    
    if User.query.filter_by(username='citizen_test').first() is None:
        citizen = User(username='citizen_test', email='citizen@test.com', role=UserRole.CITIZEN.value)
        citizen.set_password('citizenpass')
        db.session.add(citizen)
    
    if User.query.filter_by(username='pharmacist_test').first() is None:
        pharmacist = User(username='pharmacist_test', email='pharmacist@test.com', role=UserRole.PHARMACIST.value)
        pharmacist.set_password('pharmacistpass')
        db.session.add(pharmacist)
        
    db.session.commit()
    print("Database seeded.")