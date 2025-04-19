from flask import Flask
from flask_login import LoginManager
from app.config import Config
from app.models import db, User

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Import and register blueprints
    from app.routes.main import main_bp
    from app.routes.receptionist import receptionist_bp
    from app.routes.doctor import doctor_bp
    from app.routes.patient import patient_bp
    from app.routes.analytics import analytics_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(receptionist_bp)
    app.register_blueprint(doctor_bp)
    app.register_blueprint(patient_bp)
    app.register_blueprint(analytics_bp)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app 