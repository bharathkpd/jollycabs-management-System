from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import db, Vehicle, Booking, ActivityLog
from app.routes.auth import role_required

vehicles_bp = Blueprint('vehicles', __name__)

@vehicles_bp.route('/')
@login_required
@role_required('Super Admin', 'Operations Manager', 'Driver Manager')
def index():
    """Renders the fleet inventory list with search parameters and filter options."""
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('search', '').strip()
    availability_filter = request.args.get('availability', '').strip()
    maintenance_filter = request.args.get('maintenance_status', '').strip()
    
    query = Vehicle.query
    
    if search_query:
        query = query.filter(
            (Vehicle.vehicle_number.like(f"%{search_query}%")) | 
            (Vehicle.model.like(f"%{search_query}%"))
        )
    if availability_filter:
        query = query.filter_by(availability=availability_filter)
    if maintenance_filter:
        query = query.filter_by(maintenance_status=maintenance_filter)
        
    pagination = query.order_by(Vehicle.vehicle_number.asc()).paginate(page=page, per_page=10, error_out=False)
    vehicles = pagination.items
    
    return render_template(
        'vehicles/list.html',
        vehicles=vehicles,
        pagination=pagination,
        search_query=search_query,
        availability_filter=availability_filter,
        maintenance_filter=maintenance_filter
    )

@vehicles_bp.route('/add', methods=['GET', 'POST'])
@login_required
@role_required('Super Admin', 'Operations Manager', 'Driver Manager')
def add():
    """Registers a new vehicle in the company registry."""
    if request.method == 'POST':
        model = request.form.get('model')
        vehicle_number = request.form.get('vehicle_number')
        fuel_type = request.form.get('fuel_type')
        insurance_expiry_str = request.form.get('insurance_expiry')
        permit_expiry_str = request.form.get('permit_expiry')
        maintenance_status = request.form.get('maintenance_status', 'Good')
        availability = request.form.get('availability', 'Available')
        
        # Validations
        if not model or not vehicle_number or not fuel_type or not insurance_expiry_str or not permit_expiry_str:
            flash("All fields are mandatory.", "danger")
            return redirect(url_for('vehicles.add'))
            
        try:
            insurance_expiry = datetime.strptime(insurance_expiry_str, '%Y-%m-%d').date()
            permit_expiry = datetime.strptime(permit_expiry_str, '%Y-%m-%d').date()
        except ValueError:
            flash("Invalid date format. Use YYYY-MM-DD.", "danger")
            return redirect(url_for('vehicles.add'))
            
        existing_vehicle = Vehicle.query.filter_by(vehicle_number=vehicle_number).first()
        if existing_vehicle:
            flash("Vehicle plate number is already registered.", "danger")
            return redirect(url_for('vehicles.add'))

        vehicle = Vehicle(
            model=model,
            vehicle_number=vehicle_number,
            fuel_type=fuel_type,
            insurance_expiry=insurance_expiry,
            permit_expiry=permit_expiry,
            maintenance_status=maintenance_status,
            availability=availability
        )
        
        db.session.add(vehicle)
        db.session.flush()
        
        log = ActivityLog(user_id=current_user.id, action="Vehicle Updates", details=f"Registered vehicle {vehicle_number} ({model}).")
        db.session.add(log)
        db.session.commit()
        
        flash("Vehicle registered successfully.", "success")
        return redirect(url_for('vehicles.index'))
        
    return render_template('vehicles/form.html', action="Add")

@vehicles_bp.route('/edit/<int:vehicle_id>', methods=['GET', 'POST'])
@login_required
@role_required('Super Admin', 'Operations Manager', 'Driver Manager')
def edit(vehicle_id):
    """Edits an existing vehicle registration record."""
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    
    if request.method == 'POST':
        vehicle.model = request.form.get('model')
        vehicle.fuel_type = request.form.get('fuel_type')
        vehicle.maintenance_status = request.form.get('maintenance_status')
        vehicle.availability = request.form.get('availability')
        
        insurance_expiry_str = request.form.get('insurance_expiry')
        permit_expiry_str = request.form.get('permit_expiry')
        
        try:
            vehicle.insurance_expiry = datetime.strptime(insurance_expiry_str, '%Y-%m-%d').date()
            vehicle.permit_expiry = datetime.strptime(permit_expiry_str, '%Y-%m-%d').date()
        except ValueError:
            flash("Invalid date format. Use YYYY-MM-DD.", "danger")
            return redirect(url_for('vehicles.edit', vehicle_id=vehicle.id))
            
        log = ActivityLog(user_id=current_user.id, action="Vehicle Updates", details=f"Updated details for vehicle {vehicle.vehicle_number} (ID: {vehicle.id}).")
        db.session.add(log)
        db.session.commit()
        
        flash("Vehicle details updated successfully.", "success")
        return redirect(url_for('vehicles.index'))
        
    return render_template('vehicles/form.html', action="Edit", vehicle=vehicle)

@vehicles_bp.route('/delete/<int:vehicle_id>', methods=['POST'])
@login_required
@role_required('Super Admin')
def delete(vehicle_id):
    """Deletes a vehicle record permanently (restricted to Super Admins)."""
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    
    # Check if there are active bookings
    active_booking = Booking.query.filter(Booking.vehicle_id == vehicle.id, Booking.status.in_(['Ongoing', 'Dispatched'])).first()
    if active_booking:
        flash(f"Cannot delete vehicle {vehicle.vehicle_number} because it is currently assigned to an active trip (ID: {active_booking.id}).", "danger")
        return redirect(url_for('vehicles.index'))
        
    log = ActivityLog(user_id=current_user.id, action="Vehicle Updates", details=f"Deleted vehicle {vehicle.vehicle_number} (ID: {vehicle.id}) permanently.")
    db.session.add(log)
    
    db.session.delete(vehicle)
    db.session.commit()
    
    flash("Vehicle deleted successfully.", "success")
    return redirect(url_for('vehicles.index'))
