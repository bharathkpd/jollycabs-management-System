from datetime import datetime
from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_user, logout_user, login_required, current_user
from app.models import db, User, ActivityLog

auth_bp = Blueprint('auth', __name__)

def role_required(*roles):
    """Decorator to enforce role-based access control (RBAC)."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login'))
            if not current_user.has_role(*roles):
                # Deny access with a 403 Forbidden error
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def redirect_dest_by_role(user):
    """Determines landing page destination based on active staff role."""
    if user.role in ['Super Admin', 'Operations Manager']:
        return url_for('dashboard.index')
    elif user.role == 'Booking Operator':
        return url_for('bookings.index')
    elif user.role == 'Driver Manager':
        return url_for('drivers.index')
    elif user.role == 'Accounts Manager':
        return url_for('revenue.index')
    return url_for('dashboard.index')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handles user sign-in sessions with status checks and timestamp audits."""
    if current_user.is_authenticated:
        if current_user.must_change_password:
            return redirect(url_for('auth.change_password'))
        return redirect(redirect_dest_by_role(current_user))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            if user.status != 'Active':
                flash("Access Denied: Your account is marked as Inactive. Please contact the Super Admin.", "danger")
                return redirect(url_for('auth.login'))
                
            login_user(user)
            
            # Record last login time
            user.last_login = datetime.utcnow()
            
            # Log action
            log = ActivityLog(user_id=user.id, action="Login", details=f"User {user.username} signed in successfully.")
            db.session.add(log)
            db.session.commit()
            
            flash(f"Welcome back, {user.full_name}!", "success")
            
            # Check if forced password change is required
            if user.must_change_password:
                flash("Security alert: You must change your default password to secure your account.", "warning")
                return redirect(url_for('auth.change_password'))
                
            return redirect(redirect_dest_by_role(user))
        else:
            flash("Invalid username or password.", "danger")
            
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """Destroys current session and logs action."""
    log = ActivityLog(user_id=current_user.id, action="Logout", details=f"User {current_user.username} signed out.")
    db.session.add(log)
    db.session.commit()
    
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for('auth.login'))

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Simulated password recovery flow."""
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            flash("Password reset instructions have been sent to your registered email address.", "success")
            return redirect(url_for('auth.login'))
        else:
            flash("No user account found with that email address.", "danger")
    return render_template('login.html', forgot=True)

@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Forced password modification page on first login or password resets."""
    if request.method == 'POST':
        new_password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not new_password or new_password != confirm_password:
            flash("Passwords do not match or are invalid.", "danger")
            return redirect(url_for('auth.change_password'))
            
        if len(new_password) < 6:
            flash("Password must be at least 6 characters long.", "danger")
            return redirect(url_for('auth.change_password'))
            
        current_user.set_password(new_password)
        current_user.must_change_password = False
        
        log = ActivityLog(user_id=current_user.id, action="Password Reset", details="User updated their password.")
        db.session.add(log)
        db.session.commit()
        
        flash("Password updated successfully. Access granted.", "success")
        return redirect(redirect_dest_by_role(current_user))
        
    return render_template('admin/change_password.html')

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """View and update current staff credentials, supporting profile picture upload."""
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        new_password = request.form.get('password')
        
        # Check profile picture upload
        file = request.files.get('profile_photo')
        if file and file.filename != '':
            # Validate extension
            ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
            if ext in ['png', 'jpg', 'jpeg']:
                import os
                from flask import current_app
                # Rename file to user_id.ext
                filename = f"user_{current_user.id}.{ext}"
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                # Store relative static path in DB
                current_user.profile_photo = f"uploads/profile_photos/{filename}"
            else:
                flash("Invalid image format. Use PNG, JPG, or JPEG.", "danger")
                return redirect(url_for('auth.profile'))
        
        current_user.full_name = full_name
        current_user.email = email
        current_user.phone = phone
        if new_password:
            current_user.set_password(new_password)
            
        log = ActivityLog(user_id=current_user.id, action="Update Profile", details=f"User {current_user.username} updated profile details.")
        db.session.add(log)
        db.session.commit()
        
        flash("Profile updated successfully.", "success")
        return redirect(url_for('auth.profile'))
        
    logs = ActivityLog.query.filter_by(user_id=current_user.id).order_by(ActivityLog.timestamp.desc()).limit(10).all()
    return render_template('admin/profile.html', logs=logs)
