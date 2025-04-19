from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.models import Doctor, Patient, Prescription, FollowUp

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/analytics')
@login_required
def analytics():
    if current_user.role != 'receptionist':
        return redirect(url_for('dashboard'))
    
    # Get analytics data
    total_doctors = Doctor.query.count()
    total_patients = Patient.query.count()
    total_premium_patients = Patient.query.filter_by(is_premium=True).count()
    total_prescriptions = Prescription.query.count()
    total_follow_ups = FollowUp.query.count()
    
    # Get doctor-patient distribution
    doctor_stats = []
    for doctor in Doctor.query.all():
        doctor_stats.append({
            'name': doctor.name,
            'patient_count': Patient.query.filter_by(doctor_id=doctor.id).count()
        })
    
    # Get prescription trends by month
    prescriptions = Prescription.query.all()
    months = {}
    for p in prescriptions:
        month = p.date.strftime('%Y-%m')
        months[month] = months.get(month, 0) + 1
    
    # Get recent activity
    recent_activity = []
    for p in prescriptions[-10:]:  # Last 10 prescriptions
        recent_activity.append({
            'date': p.date.strftime('%Y-%m-%d'),
            'description': f'New prescription for {p.patient.name}',
            'user': p.doctor.name
        })
    
    for f in FollowUp.query.order_by(FollowUp.date.desc()).limit(10):
        recent_activity.append({
            'date': f.date.strftime('%Y-%m-%d'),
            'description': f'Follow-up for {f.patient.name}',
            'user': f.doctor.name
        })
    
    recent_activity.sort(key=lambda x: x['date'], reverse=True)
    
    return render_template('analytics.html',
                         stats={
                             'total_doctors': total_doctors,
                             'total_patients': total_patients,
                             'premium_patients': total_premium_patients,
                             'total_prescriptions': total_prescriptions,
                             'total_follow_ups': total_follow_ups
                         },
                         doctor_names=[d.name for d in Doctor.query.all()],
                         patient_counts=[Patient.query.filter_by(doctor_id=d.id).count() for d in Doctor.query.all()],
                         months=list(months.keys()),
                         prescription_counts=list(months.values()),
                         recent_activity=recent_activity) 