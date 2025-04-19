from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user
from app.models import db, User, Doctor, Patient, Prescription, FollowUp

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return render_template('index.html')

@main_bp.route('/login/<role>', methods=['GET', 'POST'])
def role_login(role):
    if role not in ['receptionist', 'doctor', 'patient']:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username, role=role).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('main.dashboard'))
        flash('Invalid username or password')
    
    template = f'{role}_login.html'
    return render_template(template)

@main_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'receptionist':
        doctors = Doctor.query.all()
        patients = Patient.query.all()
        return render_template('receptionist_dashboard.html', doctors=doctors, patients=patients)
    elif current_user.role == 'doctor':
        doctor = Doctor.query.filter_by(user_id=current_user.id).first()
        patients = Patient.query.filter_by(doctor_id=doctor.id).all() if doctor else []
        return render_template('doctor_dashboard.html', doctor=doctor, patients=patients)
    else:  # patient
        patient = Patient.query.filter_by(user_id=current_user.id).first()
        prescriptions = Prescription.query.filter_by(patient_id=patient.id).all() if patient else []
        follow_ups = FollowUp.query.filter_by(patient_id=patient.id).all() if patient else []
        return render_template('patient_dashboard.html', patient=patient, prescriptions=prescriptions, follow_ups=follow_ups)

@main_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index')) 