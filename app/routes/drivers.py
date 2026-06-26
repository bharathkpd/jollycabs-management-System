from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import db, Driver, Booking, ActivityLog
from app.routes.auth import role_required

drivers_bp = Blueprint('drivers', __name__)

@drivers_bp.route('/')
@login_required
@role_required('Super Admin', 'Operations Manager', 'Driver Manager')
def index():
    """Renders the drivers list with search query and availability filtering."""
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('search', '').strip()
    status_filter = request.args.get('status', '').strip()
    availability_filter = request.args.get('availability', '').strip()
    
    query = Driver.query
    
    if search_query:
        query = query.filter(
            (Driver.name.like(f"%{search_query}%")) | 
            (Driver.phone.like(f"%{search_query}%")) |
            (Driver.license_number.like(f"%{search_query}%"))
        )
    if status_filter:
        query = query.filter_by(status=status_filter)
    if availability_filter:
        query = query.filter_by(availability=availability_filter)
        
    pagination = query.order_by(Driver.name.asc()).paginate(page=page, per_page=10, error_out=False)
    drivers = pagination.items
    
    return render_template(
        'drivers/list.html',
        drivers=drivers,
        pagination=pagination,
        search_query=search_query,
        status_filter=status_filter,
        availability_filter=availability_filter
    )

@drivers_bp.route('/add', methods=['GET', 'POST'])
@login_required
@role_required('Super Admin', 'Operations Manager', 'Driver Manager')
def add():
    """Creates a new driver record in the system."""
    if request.method == 'POST':
        name = request.form.get('name')
        license_number = request.form.get('license_number')
        license_expiry_str = request.form.get('license_expiry')
        phone = request.form.get('phone')
        email = request.form.get('email')
        address = request.form.get('address')
        availability = request.form.get('availability', 'Available')
        status = request.form.get('status', 'Active')
        
        # Validations
        if not name or not license_number or not license_expiry_str or not phone or not email:
            flash("All mandatory fields must be filled.", "danger")
            return redirect(url_for('drivers.add'))
            
        try:
            license_expiry = datetime.strptime(license_expiry_str, '%Y-%m-%d').date()
        except ValueError:
            flash("Invalid date format. Use YYYY-MM-DD.", "danger")
            return redirect(url_for('drivers.add'))
            
        # Check duplicate licensing/phone
        existing_lic = Driver.query.filter_by(license_number=license_number).first()
        if existing_lic:
            flash("License number already registered.", "danger")
            return redirect(url_for('drivers.add'))
            
        existing_phone = Driver.query.filter_by(phone=phone).first()
        if existing_phone:
            flash("Phone number already registered.", "danger")
            return redirect(url_for('drivers.add'))

        driver = Driver(
            name=name,
            license_number=license_number,
            license_expiry=license_expiry,
            phone=phone,
            email=email,
            address=address,
            availability=availability,
            status=status
        )
        
        db.session.add(driver)
        db.session.flush()
        
        # Log action
        log = ActivityLog(user_id=current_user.id, action="Driver Updates", details=f"Registered driver {name} (License: {license_number}).")
        db.session.add(log)
        db.session.commit()
        
        flash("Driver registered successfully.", "success")
        return redirect(url_for('drivers.index'))
        
    return render_template('drivers/form.html', action="Add")

@drivers_bp.route('/edit/<int:driver_id>', methods=['GET', 'POST'])
@login_required
@role_required('Super Admin', 'Operations Manager', 'Driver Manager')
def edit(driver_id):
    """Updates an existing driver details."""
    driver = Driver.query.get_or_404(driver_id)
    
    if request.method == 'POST':
        driver.name = request.form.get('name')
        driver.phone = request.form.get('phone')
        driver.email = request.form.get('email')
        driver.address = request.form.get('address')
        driver.availability = request.form.get('availability')
        driver.status = request.form.get('status')
        
        license_expiry_str = request.form.get('license_expiry')
        try:
            driver.license_expiry = datetime.strptime(license_expiry_str, '%Y-%m-%d').date()
        except ValueError:
            flash("Invalid date format. Use YYYY-MM-DD.", "danger")
            return redirect(url_for('drivers.edit', driver_id=driver.id))
            
        log = ActivityLog(user_id=current_user.id, action="Driver Updates", details=f"Updated details for driver {driver.name} (ID: {driver.id}).")
        db.session.add(log)
        db.session.commit()
        
        flash("Driver details updated successfully.", "success")
        return redirect(url_for('drivers.index'))
        
    return render_template('drivers/form.html', action="Edit", driver=driver)

@drivers_bp.route('/profile/<int:driver_id>')
@login_required
@role_required('Super Admin', 'Operations Manager', 'Driver Manager')
def profile(driver_id):
    """Displays profile details for a driver including history."""
    driver = Driver.query.get_or_404(driver_id)
    bookings = Booking.query.filter_by(driver_id=driver.id).order_by(Booking.booking_time.desc()).all()
    completed_bookings = [b for b in bookings if b.status == 'Completed']
    total_trips = len(completed_bookings)
    total_earnings = sum(b.fare for b in completed_bookings)
    
    return render_template(
        'drivers/profile.html',
        driver=driver,
        bookings=bookings,
        total_trips=total_trips,
        total_earnings=total_earnings
    )

@drivers_bp.route('/delete/<int:driver_id>', methods=['POST'])
@login_required
@role_required('Super Admin')
def delete(driver_id):
    """Deletes a driver profile permanently (restricted to Super Admins)."""
    driver = Driver.query.get_or_404(driver_id)
    
    # Check if there are active bookings
    active_booking = Booking.query.filter(Booking.driver_id == driver.id, Booking.status.in_(['Ongoing', 'Dispatched'])).first()
    if active_booking:
        flash(f"Cannot delete driver {driver.name} because they are currently assigned to an active trip (ID: {active_booking.id}).", "danger")
        return redirect(url_for('drivers.index'))
        
    log = ActivityLog(user_id=current_user.id, action="Driver Updates", details=f"Deleted driver {driver.name} (ID: {driver.id}) permanently.")
    db.session.add(log)
    
    db.session.delete(driver)
    db.session.commit()
    
    flash("Driver deleted successfully.", "success")
    return redirect(url_for('drivers.index'))
