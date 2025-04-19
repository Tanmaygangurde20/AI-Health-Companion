from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import User, Doctor, Patient, Prescription, FollowUp

receptionist_bp = Blueprint('receptionist', __name__, url_prefix='/receptionist')

@receptionist_bp.route('/dashboard')
@login_required
def dashboard():
    if not current_user.is_receptionist:
        flash('Access denied. Only receptionists can access this page.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    doctors = Doctor.query.all()
    patients = Patient.query.all()
    return render_template('receptionist_dashboard.html', doctors=doctors, patients=patients)

@receptionist_bp.route('/add_doctor', methods=['GET', 'POST'])
@login_required
def add_doctor():
    if not current_user.is_receptionist:
        flash('Access denied. Only receptionists can perform this action.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        name = request.form.get('name')
        specialization = request.form.get('specialization')
        contact = request.form.get('contact')
        
        # Create user
        user = User(username=username, role='doctor')
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        # Create doctor
        doctor = Doctor(user_id=user.id, name=name, specialization=specialization, contact=contact)
        db.session.add(doctor)
        db.session.commit()
        
        flash('Doctor added successfully')
        return redirect(url_for('main.dashboard'))
    
    return render_template('add_doctor.html')

@receptionist_bp.route('/add_patient', methods=['GET', 'POST'])
@login_required
def add_patient():
    if current_user.role != 'receptionist':
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        name = request.form.get('name')
        age = request.form.get('age')
        gender = request.form.get('gender')
        contact = request.form.get('contact')
        address = request.form.get('address')
        is_premium = request.form.get('is_premium') == 'on'
        doctor_id = request.form.get('doctor_id')
        
        # Create user
        user = User(username=username, role='patient')
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        # Create patient
        patient = Patient(
            user_id=user.id,
            name=name,
            age=age,
            gender=gender,
            contact=contact,
            address=address,
            is_premium=is_premium,
            doctor_id=doctor_id
        )
        db.session.add(patient)
        db.session.commit()
        
        flash('Patient added successfully')
        return redirect(url_for('main.dashboard'))
    
    # Only get available doctors
    doctors = Doctor.query.filter_by(is_available=True).all()
    return render_template('add_patient.html', doctors=doctors)

@receptionist_bp.route('/edit-doctor/<int:doctor_id>', methods=['GET', 'POST'])
@login_required
def edit_doctor(doctor_id):
    if not current_user.is_receptionist:
        flash('Access denied. Only receptionists can perform this action.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    doctor = Doctor.query.get_or_404(doctor_id)
    
    if request.method == 'POST':
        doctor.name = request.form.get('name')
        doctor.specialization = request.form.get('specialization')
        doctor.contact = request.form.get('contact')
        doctor.is_available = 'is_available' in request.form
        
        db.session.commit()
        flash('Doctor updated successfully!', 'success')
        return redirect(url_for('receptionist.dashboard'))
    
    return render_template('edit_doctor.html', doctor=doctor)

@receptionist_bp.route('/delete_doctor/<int:doctor_id>', methods=['POST'])
@login_required
def delete_doctor(doctor_id):
    if not current_user.is_receptionist:
        flash('Access denied. Only receptionists can perform this action.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    doctor = Doctor.query.get_or_404(doctor_id)
    user = User.query.get(doctor.user_id)
    
    # Delete associated patients' doctor assignments
    Patient.query.filter_by(doctor_id=doctor.id).update({'doctor_id': None})
    
    db.session.delete(doctor)
    db.session.delete(user)
    db.session.commit()
    
    flash('Doctor deleted successfully')
    return redirect(url_for('main.dashboard'))

@receptionist_bp.route('/edit_patient/<int:patient_id>', methods=['GET', 'POST'])
@login_required
def edit_patient(patient_id):
    if current_user.role != 'receptionist':
        return redirect(url_for('main.dashboard'))
    
    patient = Patient.query.get_or_404(patient_id)
    user = User.query.get(patient.user_id)
    
    if request.method == 'POST':
        patient.name = request.form.get('name')
        patient.age = request.form.get('age')
        patient.gender = request.form.get('gender')
        patient.contact = request.form.get('contact')
        patient.address = request.form.get('address')
        patient.is_premium = request.form.get('is_premium') == 'on'
        patient.doctor_id = request.form.get('doctor_id')
        
        if request.form.get('password'):
            user.set_password(request.form.get('password'))
        
        db.session.commit()
        flash('Patient updated successfully')
        return redirect(url_for('main.dashboard'))
    
    # Get all available doctors plus the patient's current doctor (if any)
    available_doctors = Doctor.query.filter_by(is_available=True).all()
    current_doctor = patient.doctor
    
    # If current doctor is unavailable, add them to the list
    if current_doctor and not current_doctor.is_available and current_doctor not in available_doctors:
        available_doctors.append(current_doctor)
    
    return render_template('edit_patient.html', patient=patient, doctors=available_doctors)

@receptionist_bp.route('/delete_patient/<int:patient_id>', methods=['POST'])
@login_required
def delete_patient(patient_id):
    if not current_user.is_receptionist:
        flash('Access denied. Only receptionists can perform this action.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    patient = Patient.query.get_or_404(patient_id)
    user = User.query.get(patient.user_id)
    
    # Delete associated prescriptions and follow-ups
    Prescription.query.filter_by(patient_id=patient.id).delete()
    FollowUp.query.filter_by(patient_id=patient.id).delete()
    
    db.session.delete(patient)
    db.session.delete(user)
    db.session.commit()
    
    flash('Patient deleted successfully')
    return redirect(url_for('main.dashboard')) 