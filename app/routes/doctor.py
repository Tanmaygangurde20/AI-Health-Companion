from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from flask_login import login_required, current_user
from app import db
from app.models import Doctor, Patient, Prescription, FollowUp, Medicine
from datetime import datetime, date
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from io import BytesIO

doctor_bp = Blueprint('doctor', __name__, url_prefix='/doctor')

@doctor_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'doctor':
        return redirect(url_for('main.dashboard'))
    
    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    patients = Patient.query.filter_by(doctor_id=doctor.id).all()
    return render_template('doctor_dashboard.html', doctor=doctor, patients=patients)

@doctor_bp.route('/add_follow_up/<int:patient_id>', methods=['GET', 'POST'])
@login_required
def add_follow_up(patient_id):
    if not current_user.is_doctor:
        flash('Access denied. Only doctors can perform this action.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    patient = Patient.query.get_or_404(patient_id)
    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    
    if patient.doctor_id != doctor.id:
        flash('You are not authorized to add follow-ups for this patient', 'danger')
        return redirect(url_for('doctor.dashboard'))
    
    if request.method == 'POST':
        # Follow-up data
        visit_date = datetime.strptime(request.form.get('visit_date'), '%Y-%m-%d')
        doctor_id = request.form.get('doctor_id')
        complaints = request.form.get('complaints')
        examination = request.form.get('examination')
        diagnosis = request.form.get('diagnosis')
        treatment = request.form.get('treatment')
        next_visit_date = request.form.get('next_visit_date')
        notes = request.form.get('notes')
        
        # Create follow-up record
        follow_up = FollowUp(
            patient_id=patient.id,
            doctor_id=doctor_id,
            visit_date=visit_date,
            complaints=complaints,
            examination=examination,
            diagnosis=diagnosis,
            treatment=treatment,
            next_visit_date=datetime.strptime(next_visit_date, '%Y-%m-%d') if next_visit_date else None,
            notes=notes
        )
        
        db.session.add(follow_up)
        db.session.flush()  # Get the follow_up ID
        
        # Handle medicines data
        medicines_data = []
        index = 0
        while True:
            medicine_name = request.form.get(f'medicines[{index}][name]')
            if not medicine_name:
                break
                
            # If it's a new medicine, use the new_name field
            if medicine_name == 'new':
                medicine_name = request.form.get(f'medicines[{index}][new_name]')
            
            medicine = Medicine(
                follow_up_id=follow_up.id,
                name=medicine_name,
                dosage=request.form.get(f'medicines[{index}][dosage]'),
                notes=request.form.get(f'medicines[{index}][notes]')
            )
            db.session.add(medicine)
            index += 1
        
        db.session.commit()
        
        flash('Follow-up added successfully!', 'success')
        return redirect(url_for('doctor.view_follow_ups', patient_id=patient.id))
    
    # Get all available doctors for the dropdown
    doctors = Doctor.query.filter_by(is_available=True).all()
    return render_template('add_follow_up.html', patient=patient, doctors=doctors, now=datetime.now())

@doctor_bp.route('/view_follow_ups/<int:patient_id>')
@login_required
def view_follow_ups(patient_id):
    if current_user.role != 'doctor':
        return redirect(url_for('main.dashboard'))
    
    patient = Patient.query.get_or_404(patient_id)
    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    
    if patient.doctor_id != doctor.id:
        flash('You are not authorized to view follow-ups for this patient', 'danger')
        return redirect(url_for('doctor.dashboard'))
    
    # Get all follow-ups for the patient
    follow_ups = FollowUp.query.filter_by(patient_id=patient.id).order_by(FollowUp.visit_date.desc()).all()
    
    return render_template('view_follow_ups.html', patient=patient, follow_ups=follow_ups)

@doctor_bp.route('/view_follow_up/<int:follow_up_id>')
@login_required
def view_follow_up(follow_up_id):
    if not current_user.is_doctor:
        flash('Access denied. Only doctors can perform this action.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    follow_up = FollowUp.query.get_or_404(follow_up_id)
    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    
    # Check if the doctor is authorized to view this follow-up
    if follow_up.doctor_id != doctor.id:
        flash('You are not authorized to view this follow-up', 'danger')
        return redirect(url_for('doctor.dashboard'))
    
    return render_template('view_follow_up.html', follow_up=follow_up)

@doctor_bp.route('/toggle-availability', methods=['POST'])
@login_required
def toggle_availability():
    if not current_user.is_doctor:
        flash('Access denied. Only doctors can perform this action.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    if not doctor:
        flash('Doctor profile not found.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    doctor.is_available = not doctor.is_available
    db.session.commit()
    
    flash(f'Availability set to {"Available" if doctor.is_available else "Unavailable"}', 'success')
    return redirect(url_for('doctor.dashboard'))

@doctor_bp.route('/view_patient_report/<int:patient_id>')
@login_required
def view_patient_report(patient_id):
    if not current_user.is_doctor:
        flash('Access denied. Only doctors can view patient reports.')
        return redirect(url_for('dashboard'))
    
    patient = Patient.query.get_or_404(patient_id)
    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    
    # Check if the doctor is authorized to view this patient
    if not any(f.doctor_id == doctor.id for f in patient.follow_ups):
        flash('You are not authorized to view reports for this patient.')
        return redirect(url_for('doctor.dashboard'))
    
    # Get patient data
    patient_data = {
        "name": patient.name,
        "age": patient.age,
        "gender": patient.gender,
        "contact": patient.contact,
        "username": patient.user.username,
        "address": patient.address
    }
    
    # Get follow-ups
    follow_ups = FollowUp.query.filter_by(patient_id=patient.id).order_by(FollowUp.visit_date.desc()).all()
    
    return render_template('view_patient_report.html', patient=patient, patient_data=patient_data, follow_ups=follow_ups)

@doctor_bp.route('/generate_patient_report/<int:patient_id>')
@login_required
def generate_patient_report(patient_id):
    if not current_user.is_doctor:
        flash('Access denied. Only doctors can generate patient reports.')
        return redirect(url_for('dashboard'))
    
    patient = Patient.query.get_or_404(patient_id)
    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    
    # Check if the doctor is authorized to view this patient
    if not any(f.doctor_id == doctor.id for f in patient.follow_ups):
        flash('You are not authorized to generate reports for this patient.')
        return redirect(url_for('doctor.dashboard'))
    
    # Create PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )
    styles = getSampleStyleSheet()
    elements = []
    
    # Define custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=1,  # Center alignment
        textColor=colors.HexColor('#2c3e50')  # Dark blue color
    )
    
    heading2_style = ParagraphStyle(
        'CustomHeading2',
        parent=styles['Heading2'],
        fontSize=16,
        spaceBefore=20,
        spaceAfter=10,
        textColor=colors.HexColor('#3498db')  # Blue color
    )
    
    heading3_style = ParagraphStyle(
        'CustomHeading3',
        parent=styles['Heading3'],
        fontSize=14,
        spaceBefore=15,
        spaceAfter=5,
        textColor=colors.HexColor('#2980b9')  # Darker blue
    )
    
    heading4_style = ParagraphStyle(
        'CustomHeading4',
        parent=styles['Heading4'],
        fontSize=12,
        spaceBefore=10,
        spaceAfter=5,
        textColor=colors.HexColor('#34495e')  # Dark slate
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        spaceBefore=5,
        spaceAfter=5,
        leading=14
    )
    
    # Add header with hospital name and date
    header_style = ParagraphStyle(
        'Header',
        parent=styles['Normal'],
        fontSize=10,
        alignment=1,  # Center alignment
        textColor=colors.gray
    )
    elements.append(Paragraph("AI Powered Healthcare Companion", header_style))
    elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", header_style))
    elements.append(Spacer(1, 20))
    
    # Title
    elements.append(Paragraph(f"Patient Medical Report", title_style))
    elements.append(Spacer(1, 20))
    
    # Patient Information
    elements.append(Paragraph("Patient Information", heading2_style))
    
    # Create a more visually appealing patient info table
    patient_data = [
        ["Name:", patient.name],
        ["Age:", str(patient.age)],
        ["Gender:", patient.gender],
        ["Contact:", patient.contact],
        ["Username:", patient.user.username],
        ["Address:", patient.address]
    ]
    
    patient_table = Table(patient_data, colWidths=[100, 300])
    patient_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8f9fa')),  # Light gray background for labels
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#2c3e50')),  # Dark blue for labels
    ]))
    elements.append(patient_table)
    elements.append(Spacer(1, 20))
    
    # Follow-ups
    elements.append(Paragraph("Medical History", heading2_style))
    follow_ups = FollowUp.query.filter_by(patient_id=patient.id).order_by(FollowUp.visit_date.desc()).all()
    
    for i, follow_up in enumerate(follow_ups):
        # Add a page break if this is not the first follow-up and it's a new page
        if i > 0:
            elements.append(PageBreak())
        
        # Visit Information in a box
        visit_info = [
            [Paragraph(f"Visit Date: {follow_up.visit_date.strftime('%B %d, %Y at %I:%M %p')}", normal_style)],
            [Paragraph(f"Doctor: Dr. {follow_up.doctor.name} ({follow_up.doctor.specialization})", normal_style)]
        ]
        visit_table = Table(visit_info, colWidths=[450])
        visit_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#e8f4f8')),  # Light blue background
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2c3e50')),  # Dark blue text
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#3498db')),  # Blue border
        ]))
        elements.append(visit_table)
        elements.append(Spacer(1, 10))
        
        # Medical Details in a structured format
        if follow_up.complaints:
            elements.append(Paragraph("Complaints:", heading4_style))
            elements.append(Paragraph(follow_up.complaints, normal_style))
            elements.append(Spacer(1, 5))
        
        if follow_up.examination:
            elements.append(Paragraph("Examination:", heading4_style))
            elements.append(Paragraph(follow_up.examination, normal_style))
            elements.append(Spacer(1, 5))
        
        if follow_up.diagnosis:
            elements.append(Paragraph("Diagnosis:", heading4_style))
            elements.append(Paragraph(follow_up.diagnosis, normal_style))
            elements.append(Spacer(1, 5))
        
        if follow_up.treatment:
            elements.append(Paragraph("Treatment:", heading4_style))
            elements.append(Paragraph(follow_up.treatment, normal_style))
            elements.append(Spacer(1, 5))
        
        # Prescribed Medicines in a better formatted table
        if follow_up.medicines:
            elements.append(Paragraph("Prescribed Medicines:", heading4_style))
            medicine_data = [["Medicine", "Dosage", "Notes"]]
            for medicine in follow_up.medicines:
                medicine_data.append([
                    medicine.name,
                    medicine.dosage,
                    medicine.notes
                ])
            medicine_table = Table(medicine_data, colWidths=[150, 100, 200])
            medicine_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),  # Blue header
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('TOPPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),  # Light gray for rows
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dee2e6')),  # Light gray grid
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),  # Alternating row colors
            ]))
            elements.append(medicine_table)
            elements.append(Spacer(1, 10))
        
        if follow_up.next_visit_date:
            elements.append(Paragraph(f"Next Visit: {follow_up.next_visit_date.strftime('%B %d, %Y')}", normal_style))
            elements.append(Spacer(1, 5))
        
        if follow_up.notes:
            elements.append(Paragraph("Additional Notes:", heading4_style))
            elements.append(Paragraph(follow_up.notes, normal_style))
            elements.append(Spacer(1, 5))
        
        # Add a separator between follow-ups
        elements.append(Spacer(1, 20))
    
    # Add footer with page numbers
    def add_page_number(canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica', 9)
        page_num = canvas.getPageNumber()
        text = f"Page {page_num}"
        canvas.drawRightString(doc.pagesize[0] - 72, 72, text)
        canvas.restoreState()
    
    # Build PDF with page numbers
    doc.build(elements, onFirstPage=add_page_number, onLaterPages=add_page_number)
    buffer.seek(0)
    
    return send_file(
        buffer,
        as_attachment=False,
        download_name=f"patient_report_{patient.name}_{datetime.now().strftime('%Y%m%d')}.pdf",
        mimetype='application/pdf'
    )

@doctor_bp.route('/add_prescription/<int:patient_id>', methods=['GET', 'POST'])
@login_required
def add_prescription(patient_id):
    if not current_user.is_doctor:
        flash('Access denied. Only doctors can perform this action.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    patient = Patient.query.get_or_404(patient_id)
    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    
    if patient.doctor_id != doctor.id:
        flash('You are not authorized to add prescriptions for this patient', 'danger')
        return redirect(url_for('doctor.dashboard'))
    
    if request.method == 'POST':
        medication = request.form.get('medication')
        dosage = request.form.get('dosage')
        instructions = request.form.get('instructions')
        
        prescription = Prescription(
            patient_id=patient.id,
            doctor_id=doctor.id,
            medication=medication,
            dosage=dosage,
            instructions=instructions
        )
        
        db.session.add(prescription)
        db.session.commit()
        
        flash('Prescription added successfully!', 'success')
        return redirect(url_for('doctor.view_follow_ups', patient_id=patient.id))
    
    return render_template('add_prescription.html', patient=patient) 