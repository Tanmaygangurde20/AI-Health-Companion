import os
import sys

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import Patient

app = create_app()

with app.app_context():
    # Create all tables
    db.create_all()
    print("Database schema updated successfully!")
    
    # Check if the email column exists
    try:
        # Try to access the email column to see if it exists
        Patient.email
        print("Email field is already present in the Patient model")
    except Exception as e:
        print(f"Error: {str(e)}")
        print("Please make sure you've added the email field to the Patient model in app/models.py") 