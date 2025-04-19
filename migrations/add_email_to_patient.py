import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models import Patient
from sqlalchemy import text

def upgrade():
    """Add email field to Patient model"""
    # Add email column
    db.session.execute(text('ALTER TABLE patient ADD COLUMN email VARCHAR(120)'))
    db.session.commit()
    print("Added email field to Patient model")

def downgrade():
    """Remove email field from Patient model"""
    # Remove email column
    db.session.execute(text('ALTER TABLE patient DROP COLUMN email'))
    db.session.commit()
    print("Removed email field from Patient model")

if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        upgrade()
        print("Successfully added email column to patient table") 