import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import os
from typing import List, Optional
from flask import current_app

class EmailAutomation:
    def __init__(self, smtp_server: str, smtp_port: int, sender_email: str, sender_password: str):
        """
        Initialize the EmailAutomation class with SMTP server details.
        
        Args:
            smtp_server (str): SMTP server address
            smtp_port (int): SMTP server port
            sender_email (str): Email address of the sender
            sender_password (str): Password or app-specific password for the sender's email
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password

    def send_email(
        self,
        recipient_email: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None,
        attachments: Optional[List[str]] = None
    ) -> bool:
        """
        Send an email with optional HTML content and attachments.
        
        Args:
            recipient_email (str): Email address of the recipient
            subject (str): Subject of the email
            body (str): Plain text body of the email
            html_body (str, optional): HTML version of the email body
            attachments (List[str], optional): List of file paths to attach
            
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        try:
            # Create message container
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.sender_email
            msg['To'] = recipient_email

            # Add plain text body
            msg.attach(MIMEText(body, 'plain'))

            # Add HTML body if provided
            if html_body:
                msg.attach(MIMEText(html_body, 'html'))

            # Add attachments if any
            if attachments:
                for file_path in attachments:
                    if os.path.exists(file_path):
                        with open(file_path, 'rb') as f:
                            attachment = MIMEApplication(f.read(), _subtype='pdf')
                            attachment.add_header(
                                'Content-Disposition',
                                'attachment',
                                filename=os.path.basename(file_path)
                            )
                            msg.attach(attachment)

            # Create SMTP connection
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)
            
            return True

        except Exception as e:
            current_app.logger.error(f"Error sending email: {str(e)}")
            return False

def send_medicine_expiry_alert(patient_email: str, medicine_name: str, expiry_date: str, days_until_expiry: int, alert_level: str) -> bool:
    """
    Send a medicine expiry alert email to a patient.
    
    Args:
        patient_email (str): Email address of the patient
        medicine_name (str): Name of the medicine
        expiry_date (str): Expiry date of the medicine
        days_until_expiry (int): Number of days until expiry
        alert_level (str): Alert level (danger, warning, info, success)
        
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    # Get email configuration from environment variables
    smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    sender_email = os.getenv('SENDER_EMAIL')
    sender_password = os.getenv('SENDER_PASSWORD')
    
    if not all([sender_email, sender_password]):
        current_app.logger.error("Email configuration is missing")
        return False
    
    # Create email automation instance
    email_automation = EmailAutomation(
        smtp_server=smtp_server,
        smtp_port=smtp_port,
        sender_email=sender_email,
        sender_password=sender_password
    )
    
    # Determine alert message based on alert level
    if alert_level == 'danger':
        subject = f"⚠️ URGENT: Medicine Expired - {medicine_name}"
        alert_icon = "🔴"
        alert_text = "EXPIRED"
    elif alert_level == 'warning':
        subject = f"⚠️ ALERT: Medicine Expiring Soon - {medicine_name}"
        alert_icon = "🟡"
        alert_text = "EXPIRING SOON"
    elif alert_level == 'info':
        subject = f"ℹ️ Medicine Expiry Notice - {medicine_name}"
        alert_icon = "🔵"
        alert_text = "EXPIRY NOTICE"
    else:
        subject = f"✅ Medicine Expiry Update - {medicine_name}"
        alert_icon = "🟢"
        alert_text = "VALID"
    
    # Create email content
    plain_text = f"""
Medicine Expiry Alert

Medicine: {medicine_name}
Expiry Date: {expiry_date}
Days Until Expiry: {days_until_expiry}
Status: {alert_text}

Please take necessary action based on this alert.
"""
    
    html_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #0d6efd;">Medicine Expiry Alert</h2>
                
                <div style="background-color: #f8f9fa; border-radius: 8px; padding: 15px; margin: 20px 0;">
                    <p><strong>Medicine:</strong> {medicine_name}</p>
                    <p><strong>Expiry Date:</strong> {expiry_date}</p>
                    <p><strong>Days Until Expiry:</strong> {days_until_expiry}</p>
                    <p><strong>Status:</strong> <span style="font-weight: bold;">{alert_text}</span></p>
                </div>
                
                <p>Please take necessary action based on this alert.</p>
                
                <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; font-size: 12px; color: #6c757d;">
                    <p>This is an automated alert from your healthcare provider.</p>
                </div>
            </div>
        </body>
    </html>
    """
    
    # Send the email
    return email_automation.send_email(
        recipient_email=patient_email,
        subject=subject,
        body=plain_text,
        html_body=html_content
    ) 