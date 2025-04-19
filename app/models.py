from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'receptionist', 'doctor', 'patient'
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @property
    def is_receptionist(self):
        return self.role == 'receptionist'
    
    @property
    def is_doctor(self):
        return self.role == 'doctor'
    
    @property
    def is_patient(self):
        return self.role == 'patient'

class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    specialization = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(20), nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('doctor', uselist=False))
    assigned_patients = db.relationship('Patient', backref='assigned_doctor', lazy=True)
    follow_ups = db.relationship('FollowUp', backref='follow_up_doctor', lazy=True)

    def toggle_availability(self):
        self.is_available = not self.is_available
        db.session.commit()
        return self.is_available

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    contact = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    is_premium = db.Column(db.Boolean, default=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=True)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('patient', uselist=False))
    doctor = db.relationship('Doctor', backref=db.backref('patients', lazy=True))
    prescriptions = db.relationship('Prescription', backref='prescription_patient', lazy=True)
    follow_ups = db.relationship('FollowUp', backref='follow_up_patient', lazy=True)

class Prescription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    medication = db.Column(db.Text, nullable=False)
    dosage = db.Column(db.String(100), nullable=False)
    instructions = db.Column(db.Text, nullable=False)

class Medicine(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    follow_up_id = db.Column(db.Integer, db.ForeignKey('follow_up.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    dosage = db.Column(db.String(100), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    
    # Relationship
    follow_up = db.relationship('FollowUp', backref=db.backref('medicines', lazy=True))

class FollowUp(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    visit_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    complaints = db.Column(db.Text, nullable=True)
    examination = db.Column(db.Text, nullable=True)
    diagnosis = db.Column(db.Text, nullable=False)
    treatment = db.Column(db.Text, nullable=True)
    next_visit_date = db.Column(db.DateTime, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    
    # Relationships
    patient = db.relationship('Patient', backref=db.backref('patient_follow_ups', lazy=True))
    doctor = db.relationship('Doctor', backref=db.backref('doctor_follow_ups', lazy=True)) 