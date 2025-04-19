from flask import Flask
from app import create_app, db
from app.models import User

def create_sample_receptionist():
    app = create_app()
    with app.app_context():
        # Check if receptionist already exists
        existing_user = User.query.filter_by(username='receptionist').first()
        if existing_user:
            print("Receptionist user already exists!")
            return

        # Create user
        user = User(
            username='receptionist',
            role='receptionist'
        )
        user.set_password('receptionist123')
        
        db.session.add(user)
        db.session.commit()

        print("Sample receptionist created successfully!")
        print("Username: receptionist")
        print("Password: receptionist123")

if __name__ == '__main__':
    create_sample_receptionist() 