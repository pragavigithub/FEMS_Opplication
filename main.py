from app import app, db
from models import User, Household
from werkzeug.security import generate_password_hash

# Create default admin user on startup
with app.app_context():
    # Create default household if it doesn't exist
    default_household = Household.query.filter_by(name='Default Household').first()
    if not default_household:
        default_household = Household(name='Default Household')
        db.session.add(default_household)
        db.session.commit()
    
    # Create default admin user if it doesn't exist
    admin_user = User.query.filter_by(email='admin@household.local').first()
    if not admin_user:
        admin_user = User(
            household_id=default_household.id,
            display_name='admin',
            email='admin@household.local',
            password_hash=generate_password_hash('admin123'),
            is_admin=True
        )
        db.session.add(admin_user)
        db.session.commit()
        print("Default admin user created: admin@household.local / admin123")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
