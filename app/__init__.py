from flask import Flask, redirect, url_for, flash, request
from flask_login import LoginManager, current_user
from app.config import Config
from app.models import db, User

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'warning'

@login_manager.user_loader
def load_user(user_id):
    """Loads current user details from database session."""
    return User.query.get(int(user_id))

def create_app(config_class=Config):
    """Flask Application Factory pattern."""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize DB & logins
    db.init_app(app)
    login_manager.init_app(app)
    
    # Run configuration dir builders
    config_class.init_app(app)
    
    with app.app_context():
        # Ensure database tables exist
        db.create_all()
        
        # Check and enforce default admin account
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                full_name='Jolly Super Admin',
                email='admin@jollycabs.in',
                phone='+91 9999999999',
                role='Super Admin',
                status='Active',
                must_change_password=True  # Force password change on first login
            )
            admin.set_password('admin123')
            db.session.add(admin)
            
        # Operations Manager
        manager = User.query.filter_by(username='manager').first()
        if not manager:
            manager = User(
                username='manager',
                full_name='Rajesh Khanna (Operations)',
                email='manager@jollycabs.in',
                phone='+91 9888877777',
                role='Operations Manager',
                status='Active',
                must_change_password=False
            )
            manager.set_password('manager123')
            db.session.add(manager)
            
        # Booking Operator
        dispatcher = User.query.filter_by(username='dispatcher').first()
        if not dispatcher:
            dispatcher = User(
                username='dispatcher',
                full_name='Sanjay Sharma (Booking Desk)',
                email='dispatcher@jollycabs.in',
                phone='+91 9777766666',
                role='Booking Operator',
                status='Active',
                must_change_password=False
            )
            dispatcher.set_password('dispatch123')
            db.session.add(dispatcher)
            
        # Driver Manager
        drivermgr = User.query.filter_by(username='drivermgr').first()
        if not drivermgr:
            drivermgr = User(
                username='drivermgr',
                full_name='Gurpreet Singh (Fleet Desk)',
                email='drivermgr@jollycabs.in',
                phone='+91 9666655555',
                role='Driver Manager',
                status='Active',
                must_change_password=False
            )
            drivermgr.set_password('driver123')
            db.session.add(drivermgr)
            
        # Accounts Manager
        accounts = User.query.filter_by(username='accounts').first()
        if not accounts:
            accounts = User(
                username='accounts',
                full_name='Nisha Gupta (Accounts)',
                email='accounts@jollycabs.in',
                phone='+91 9555544444',
                role='Accounts Manager',
                status='Active',
                must_change_password=False
            )
            accounts.set_password('accounts123')
            db.session.add(accounts)
            
        db.session.commit()
        print("Default database users seeded.")
    
    # Intercept requests for forced password resets (Super Admin first login check)
    @app.before_request
    def check_forced_password_reset():
        if current_user.is_authenticated and current_user.must_change_password:
            # Allow access only to change-password, logout, and static folders
            if request.endpoint not in ['auth.change_password', 'auth.logout', 'static']:
                flash("Security policy: You must change your default password before accessing JOMS.", "warning")
                return redirect(url_for('auth.change_password'))

    # Register blueprinted controller routes
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.drivers import drivers_bp
    from app.routes.vehicles import vehicles_bp
    from app.routes.customers import customers_bp
    from app.routes.bookings import bookings_bp
    from app.routes.expenses import expenses_bp
    from app.routes.revenue import revenue_bp
    from app.routes.admin import admin_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(drivers_bp, url_prefix='/drivers')
    app.register_blueprint(vehicles_bp, url_prefix='/vehicles')
    app.register_blueprint(customers_bp, url_prefix='/customers')
    app.register_blueprint(bookings_bp, url_prefix='/bookings')
    app.register_blueprint(expenses_bp, url_prefix='/expenses')
    app.register_blueprint(revenue_bp, url_prefix='/revenue')
    app.register_blueprint(admin_bp)
    
    # Global context injection for unread alerts badge and role check
    @app.context_processor
    def inject_global_data():
        from app.services.notification_service import NotificationService
        try:
            count = NotificationService.get_unread_count()
        except Exception:
            count = 0
        return {
            'unread_notifications_count': count
        }
        
    return app
