from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, abort
from flask_login import login_required, current_user
from app.models import db, User, Driver, Vehicle, Customer, Booking, Payment, Expense, Notification, ActivityLog
from app.routes.auth import role_required
from app.services.report_service import ReportService
from app.services.backup_service import BackupService
from app.services.notification_service import NotificationService

admin_bp = Blueprint('admin', __name__)

# --- GLOBAL SEARCH ---
@admin_bp.route('/search')
@login_required
def global_search():
    """Routes search queries across drivers, vehicles, customers, and bookings."""
    query = request.args.get('q', '').strip()
    if not query:
        return render_template('admin/search_results.html', query=query, drivers=[], vehicles=[], customers=[], bookings=[])
        
    drivers, vehicles, customers, bookings = [], [], [], []
    
    # Check permissions before returning specific search aggregates
    if current_user.role in ['Super Admin', 'Operations Manager', 'Driver Manager']:
        drivers = Driver.query.filter(
            (Driver.name.like(f"%{query}%")) | 
            (Driver.phone.like(f"%{query}%")) |
            (Driver.license_number.like(f"%{query}%"))
        ).all()
        
        vehicles = Vehicle.query.filter(
            (Vehicle.vehicle_number.like(f"%{query}%")) | 
            (Vehicle.model.like(f"%{query}%"))
        ).all()
        
    if current_user.role in ['Super Admin', 'Operations Manager', 'Booking Operator']:
        customers = Customer.query.filter(
            (Customer.name.like(f"%{query}%")) | 
            (Customer.phone.like(f"%{query}%")) | 
            (Customer.email.like(f"%{query}%"))
        ).all()
        
        bookings = Booking.query.join(Customer).filter(
            (Customer.name.like(f"%{query}%")) |
            (Booking.pickup_location.like(f"%{query}%")) |
            (Booking.drop_location.like(f"%{query}%"))
        ).all()
        
    return render_template(
        'admin/search_results.html',
        query=query,
        drivers=drivers,
        vehicles=vehicles,
        customers=customers,
        bookings=bookings
    )

# --- NOTIFICATIONS PANEL ---
@admin_bp.route('/notifications')
@login_required
def notifications_list():
    """Displays compliance notifications list."""
    notifications = Notification.query.order_by(Notification.created_at.desc()).all()
    return render_template('notifications/list.html', notifications=notifications)

@admin_bp.route('/notifications/read-all', methods=['POST'])
@login_required
def notifications_read_all():
    """Marks all unread system notifications as read."""
    unread_alerts = Notification.query.filter_by(status='Unread').all()
    for alert in unread_alerts:
        alert.status = 'Read'
    db.session.commit()
    flash("All notifications marked as read.", "success")
    return redirect(url_for('admin.notifications_list'))

# --- SYSTEM ACTIVITY LOGS (Super Admin only as requested) ---
@admin_bp.route('/admin/logs')
@login_required
@role_required('Super Admin')
def activity_logs():
    """Renders administration audit logs with pagination."""
    page = request.args.get('page', 1, type=int)
    logs_pagination = ActivityLog.query.order_by(ActivityLog.timestamp.desc()).paginate(page=page, per_page=20, error_out=False)
    logs = logs_pagination.items
    return render_template('admin/logs.html', logs=logs, pagination=logs_pagination)

# --- DATABASE BACKUPS (Super Admin only) ---
@admin_bp.route('/admin/backup')
@login_required
@role_required('Super Admin')
def backup_index():
    """List system backups."""
    backups = BackupService.list_backups()
    return render_template('admin/backup.html', backups=backups)

@admin_bp.route('/admin/backup/create', methods=['POST'])
@login_required
@role_required('Super Admin')
def backup_create():
    """Launches automated SQLite snapshot backups."""
    try:
        filename = BackupService.create_backup()
        log = ActivityLog(user_id=current_user.id, action="Backup DB", details=f"Database backup generated: {filename}")
        db.session.add(log)
        db.session.commit()
        flash(f"Backup snapshot '{filename}' generated successfully.", "success")
    except Exception as e:
        flash(f"Failed to generate backup: {str(e)}", "danger")
    return redirect(url_for('admin.backup_index'))

@admin_bp.route('/admin/backup/delete/<string:filename>', methods=['POST'])
@login_required
@role_required('Super Admin')
def backup_delete(filename):
    """Deletes backup archive file."""
    if BackupService.delete_backup(filename):
        log = ActivityLog(user_id=current_user.id, action="Delete Backup", details=f"Deleted backup archive: {filename}")
        db.session.add(log)
        db.session.commit()
        flash("Backup archive file deleted.", "success")
    else:
        flash("Backup file not found.", "danger")
    return redirect(url_for('admin.backup_index'))

# --- USER MANAGEMENT CRUD MODULE (Super Admin only) ---
@admin_bp.route('/admin/users')
@login_required
@role_required('Super Admin')
def users_list():
    """Lists all user accounts in the JOMS system."""
    users = User.query.order_by(User.username.asc()).all()
    return render_template('admin/users.html', users=users)

@admin_bp.route('/admin/users/add', methods=['GET', 'POST'])
@login_required
@role_required('Super Admin')
def user_create():
    """Registers a new staff user and flags password reset as required."""
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        username = request.form.get('username')
        email = request.form.get('email')
        phone = request.form.get('phone')
        role = request.form.get('role')
        status = request.form.get('status', 'Active')
        password = request.form.get('password')
        
        # Validations
        if not full_name or not username or not email or not phone or not role or not password:
            flash("All fields are mandatory to create a user.", "danger")
            return redirect(url_for('admin.user_create'))
            
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists.", "danger")
            return redirect(url_for('admin.user_create'))
            
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            flash("Email already exists.", "danger")
            return redirect(url_for('admin.user_create'))

        user = User(
            full_name=full_name,
            username=username,
            email=email,
            phone=phone,
            role=role,
            status=status,
            must_change_password=True  # Force change on first login
        )
        user.set_password(password)
        db.session.add(user)
        
        # Log action
        log = ActivityLog(user_id=current_user.id, action="Create User", details=f"Created user account {username} with role {role}.")
        db.session.add(log)
        db.session.commit()
        
        flash(f"User account '{username}' registered successfully.", "success")
        return redirect(url_for('admin.users_list'))
        
    return render_template('admin/user_form.html', action="Add")

@admin_bp.route('/admin/users/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
@role_required('Super Admin')
def user_edit(user_id):
    """Edits an existing user details (excluding password resets)."""
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        user.full_name = request.form.get('full_name')
        user.email = request.form.get('email')
        user.phone = request.form.get('phone')
        user.role = request.form.get('role')
        user.status = request.form.get('status')
        
        # Super admin safety check: prevent deactivating own profile
        if user.id == current_user.id and user.status == 'Inactive':
            flash("Security check: You cannot mark your own account as inactive.", "danger")
            return redirect(url_for('admin.user_edit', user_id=user.id))
            
        log = ActivityLog(user_id=current_user.id, action="Edit User", details=f"Edited details for user {user.username}.")
        db.session.add(log)
        db.session.commit()
        
        flash(f"User details for '{user.username}' updated successfully.", "success")
        return redirect(url_for('admin.users_list'))
        
    return render_template('admin/user_form.html', action="Edit", user=user)

@admin_bp.route('/admin/users/reset-password/<int:user_id>', methods=['GET', 'POST'])
@login_required
@role_required('Super Admin')
def user_reset_password(user_id):
    """Forces administrative password reset on a user account."""
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        new_password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not new_password or new_password != confirm_password:
            flash("Passwords do not match or are invalid.", "danger")
            return redirect(url_for('admin.user_reset_password', user_id=user.id))
            
        user.set_password(new_password)
        user.must_change_password = True  # Force reset flag
        
        log = ActivityLog(user_id=current_user.id, action="Password Reset", details=f"Forced password reset on user {user.username}.")
        db.session.add(log)
        db.session.commit()
        
        flash(f"Password reset triggered successfully for '{user.username}'.", "success")
        return redirect(url_for('admin.users_list'))
        
    return render_template('admin/reset_password_admin.html', user=user)

@admin_bp.route('/admin/users/delete/<int:user_id>', methods=['POST'])
@login_required
@role_required('Super Admin')
def user_delete(user_id):
    """Deletes a user account permanently (Super Admin restricted)."""
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        flash("You cannot delete your own profile.", "danger")
        return redirect(url_for('admin.users_list'))
        
    log = ActivityLog(user_id=current_user.id, action="Delete User", details=f"Deleted user account: {user.username}.")
    db.session.add(log)
    
    db.session.delete(user)
    db.session.commit()
    
    flash(f"User account '{user.username}' deleted permanently.", "success")
    return redirect(url_for('admin.users_list'))

# --- REPORTS MODULE (Super Admin & Accounts Manager only) ---
@admin_bp.route('/reports')
@login_required
@role_required('Super Admin', 'Accounts Manager')
def reports_dashboard():
    """Renders the reports generator panel."""
    return render_template('reports/index.html')

@admin_bp.route('/reports/export/<string:report_type>/<string:format_type>')
@login_required
@role_required('Super Admin', 'Accounts Manager')
def reports_export(report_type, format_type):
    """Generates and downloads reports dynamically based on format (CSV, PDF, Excel)."""
    if report_type not in ['revenue', 'driver', 'vehicle', 'customer', 'bookings']:
        abort(404)
        
    if format_type == 'csv':
        buffer = ReportService.generate_csv(report_type)
        filename = f"joms_{report_type}_report_{datetime.now().strftime('%Y%m%d')}.csv"
        mimetype = 'text/csv'
    elif format_type == 'xlsx':
        buffer = ReportService.generate_excel(report_type)
        filename = f"joms_{report_type}_report_{datetime.now().strftime('%Y%m%d')}.xlsx"
        mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    elif format_type == 'pdf':
        buffer = ReportService.generate_pdf(report_type)
        filename = f"joms_{report_type}_report_{datetime.now().strftime('%Y%m%d')}.pdf"
        mimetype = 'application/pdf'
    else:
        abort(400)
        
    # Log report generation
    log = ActivityLog(user_id=current_user.id, action="Export Report", details=f"Generated {format_type.upper()} report for {report_type.capitalize()}.")
    db.session.add(log)
    db.session.commit()
    
    return send_file(
        buffer,
        as_attachment=True,
        download_name=filename,
        mimetype=mimetype
    )
