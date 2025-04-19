from flask import Flask
from flask_migrate import Migrate
from app import create_app, db
from app.models import User, Doctor, Patient, Prescription, FollowUp
from sqlalchemy import text, inspect

app = create_app()
migrate = Migrate(app, db)

def column_exists(table_name, column_name):
    inspector = inspect(db.engine)
    columns = [col['name'] for col in inspector.get_columns(table_name)]
    return column_name in columns

if __name__ == '__main__':
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Add is_available column to doctor table if it doesn't exist
        if not column_exists('doctor', 'is_available'):
            try:
                db.session.execute(text('ALTER TABLE doctor ADD COLUMN is_available BOOLEAN DEFAULT TRUE'))
                db.session.commit()
                print("Successfully added is_available column to doctor table")
            except Exception as e:
                print(f"Error adding is_available column: {str(e)}")
                db.session.rollback()
        
        # Add new columns to follow_up table if they don't exist
        follow_up_columns = {
            'visit_date': 'DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP',
            'complaints': 'TEXT NOT NULL',
            'examination': 'TEXT NOT NULL',
            'diagnosis': 'TEXT NOT NULL',
            'treatment': 'TEXT NOT NULL',
            'next_visit_date': 'DATETIME',
            'notes': 'TEXT'
        }
        
        for column, definition in follow_up_columns.items():
            if not column_exists('follow_up', column):
                try:
                    db.session.execute(text(f'ALTER TABLE follow_up ADD COLUMN {column} {definition}'))
                    db.session.commit()
                    print(f"Successfully added {column} column to follow_up table")
                except Exception as e:
                    print(f"Error adding {column} column: {str(e)}")
                    db.session.rollback()
        
        print("Database migration completed!") 