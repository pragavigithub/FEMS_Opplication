import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    
    # Database configuration - prioritize custom database URL if provided
    custom_db_url = os.environ.get("CUSTOM_DATABASE_URL")
    if custom_db_url:
        app.config["SQLALCHEMY_DATABASE_URI"] = custom_db_url
    else:
        app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///finance.db")
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    
    # Configure Flask-WTF
    from flask_wtf.csrf import CSRFProtect
    csrf = CSRFProtect(app)
    
    # Login manager configuration
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        from models import User
        return User.query.get(int(user_id))
    
    # Register blueprints
    from routes import main_bp, auth_bp, expense_bp, income_bp, loan_bp, savings_bp, budget_bp, report_bp, settings_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(expense_bp, url_prefix='/expenses')
    app.register_blueprint(income_bp, url_prefix='/income')
    app.register_blueprint(loan_bp, url_prefix='/loans')
    app.register_blueprint(savings_bp, url_prefix='/savings')
    app.register_blueprint(budget_bp, url_prefix='/budget')
    app.register_blueprint(report_bp, url_prefix='/reports')
    app.register_blueprint(settings_bp, url_prefix='/settings')
    
    with app.app_context():
        import models
        db.create_all()
        
        # Create default categories if they don't exist
        from models import ExpenseCategory
        default_categories = [
            'Groceries', 'Utilities', 'Transportation', 'Healthcare',
            'Entertainment', 'Dining Out', 'Shopping', 'Insurance',
            'Home Maintenance', 'Personal Care'
        ]
        
        existing_categories = ExpenseCategory.query.filter_by(is_default=True).all()
        if not existing_categories:
            for category_name in default_categories:
                category = ExpenseCategory(
                    name=category_name,
                    is_default=True,
                    household_id=None
                )
                db.session.add(category)
            db.session.commit()
    
    return app

app = create_app()
