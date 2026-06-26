from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import db, Booking, Customer, Driver, Vehicle, Payment, ActivityLog
from app.routes.auth import role_required

bookings_bp = Blueprint('bookings', __name__)

@bookings_bp.route('/')
@login_required
@role_required('Super Admin', 'Operations Manager', 'Booking Operator')
def index():
    """Lists bookings with filters for status, payment, and pagination."""
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('search', '').strip()
    status_filter = request.args.get('status', '').strip()
    payment_filter = request.args.get('payment_status', '').strip()
    
    query = Booking.query.join(Customer)
    
    if search_query:
        query = query.filter(
            (Customer.name.like(f"%{search_query}%")) |
            (Booking.pickup_location.like(f"%{search_query}%")) |
            (Booking.drop_location.like(f"%{search_query}%"))
        )
    if status_filter:
        query = query.filter(Booking.status == status_filter)
    if payment_filter:
        query = query.filter(Booking.payment_status == payment_filter)
        
    pagination = query.order_by(Booking.booking_time.desc()).paginate(page=page, per_page=10, error_out=False)
    bookings = pagination.items
    
    return render_template(
        'bookings/list.html',
        bookings=bookings,
        pagination=pagination,
        search_query=search_query,
        status_filter=status_filter,
        payment_filter=payment_filter
    )

@bookings_bp.route('/add', methods=['GET', 'POST'])
@login_required
@role_required('Super Admin', 'Operations Manager', 'Booking Operator')
def add():
    """Places a new cab trip booking, matching customers, drivers, and vehicles."""
    if request.method == 'POST':
        customer_id = request.form.get('customer_id')
        driver_id = request.form.get('driver_id')
        vehicle_id = request.form.get('vehicle_id')
        pickup_location = request.form.get('pickup_location')
        drop_location = request.form.get('drop_location')
        distance = request.form.get('distance', 0.0, type=float)
        fare = request.form.get('fare', 0.0, type=float)
        status = request.form.get('status', 'Pending')
        payment_status = request.form.get('payment_status', 'Unpaid')
        
        # Validations
        if not customer_id or not pickup_location or not drop_location:
            flash("Customer and trip route locations are required.", "danger")
            return redirect(url_for('bookings.add'))

        d_id = int(driver_id) if driver_id and driver_id != 'None' else None
        v_id = int(vehicle_id) if vehicle_id and vehicle_id != 'None' else None
        
        booking = Booking(
            customer_id=customer_id,
            driver_id=d_id,
            vehicle_id=v_id,
            pickup_location=pickup_location,
            drop_location=drop_location,
            distance=distance,
            fare=fare,
            status=status,
            payment_status=payment_status
        )
        
        if status in ['Dispatched', 'Ongoing']:
            if d_id:
                driver = Driver.query.get(d_id)
                if driver: driver.availability = 'Busy'
            if v_id:
                vehicle = Vehicle.query.get(v_id)
                if vehicle: vehicle.availability = 'Busy'
                
        db.session.add(booking)
        db.session.flush()
        
        if payment_status == 'Paid' and fare > 0:
            payment = Payment(
                booking_id=booking.id,
                amount=fare,
                payment_method='Cash',
                status='Completed'
            )
            db.session.add(payment)
            
        log = ActivityLog(user_id=current_user.id, action="Booking Updates", details=f"Created booking ID: {booking.id} for Customer ID: {customer_id}.")
        db.session.add(log)
        db.session.commit()
        
        flash("Booking created successfully.", "success")
        return redirect(url_for('bookings.index'))
        
    customers = Customer.query.filter_by(status='Active').all()
    available_drivers = Driver.query.filter_by(availability='Available', status='Active').all()
    available_vehicles = Vehicle.query.filter_by(availability='Available', maintenance_status='Good').all()
    
    return render_template(
        'bookings/form.html',
        action="Add",
        customers=customers,
        drivers=available_drivers,
        vehicles=available_vehicles
    )

@bookings_bp.route('/edit/<int:booking_id>', methods=['GET', 'POST'])
@login_required
@role_required('Super Admin', 'Operations Manager', 'Booking Operator')
def edit(booking_id):
    """Modifies trip status, route details, and driver/vehicle assignments."""
    booking = Booking.query.get_or_404(booking_id)
    old_status = booking.status
    old_driver_id = booking.driver_id
    old_vehicle_id = booking.vehicle_id
    
    if request.method == 'POST':
        booking.pickup_location = request.form.get('pickup_location')
        booking.drop_location = request.form.get('drop_location')
        booking.distance = request.form.get('distance', 0.0, type=float)
        booking.fare = request.form.get('fare', 0.0, type=float)
        
        new_status = request.form.get('status')
        new_payment_status = request.form.get('payment_status')
        
        driver_id = request.form.get('driver_id')
        vehicle_id = request.form.get('vehicle_id')
        
        new_d_id = int(driver_id) if driver_id and driver_id != 'None' else None
        new_v_id = int(vehicle_id) if vehicle_id and vehicle_id != 'None' else None
        
        # Release old assets if changed
        if old_driver_id and old_driver_id != new_d_id:
            old_driver = Driver.query.get(old_driver_id)
            if old_driver: old_driver.availability = 'Available'
            
        if old_vehicle_id and old_vehicle_id != new_v_id:
            old_vehicle = Vehicle.query.get(old_vehicle_id)
            if old_vehicle: old_vehicle.availability = 'Available'
            
        booking.driver_id = new_d_id
        booking.vehicle_id = new_v_id
        booking.status = new_status
        booking.payment_status = new_payment_status
        
        if new_status in ['Completed', 'Cancelled']:
            if new_d_id:
                d = Driver.query.get(new_d_id)
                if d: d.availability = 'Available'
            if new_v_id:
                v = Vehicle.query.get(new_v_id)
                if v: v.availability = 'Available'
                
            if new_status == 'Completed' and not booking.trip_end_time:
                booking.trip_end_time = datetime.utcnow()
        else:
            if new_d_id:
                d = Driver.query.get(new_d_id)
                if d: d.availability = 'Busy'
            if new_v_id:
                v = Vehicle.query.get(new_v_id)
                if v: v.availability = 'Busy'
                
            if new_status == 'Ongoing' and not booking.trip_start_time:
                booking.trip_start_time = datetime.utcnow()
                
        if new_payment_status == 'Paid' and booking.fare > 0:
            existing_payment = Payment.query.filter_by(booking_id=booking.id, status='Completed').first()
            if not existing_payment:
                payment = Payment(
                    booking_id=booking.id,
                    amount=booking.fare,
                    payment_method=request.form.get('payment_method', 'Cash'),
                    status='Completed'
                )
                db.session.add(payment)
                
        log = ActivityLog(user_id=current_user.id, action="Booking Updates", details=f"Updated booking ID: {booking.id} status from {old_status} to {new_status}.")
        db.session.add(log)
        db.session.commit()
        
        flash("Booking updated successfully.", "success")
        return redirect(url_for('bookings.index'))
        
    customers = Customer.query.all()
    drivers = Driver.query.filter(
        (Driver.availability == 'Available') | (Driver.id == booking.driver_id),
        Driver.status == 'Active'
    ).all()
    vehicles = Vehicle.query.filter(
        (Vehicle.availability == 'Available') | (Vehicle.id == booking.vehicle_id),
        Vehicle.maintenance_status == 'Good'
    ).all()
    
    return render_template(
        'bookings/form.html',
        action="Edit",
        booking=booking,
        customers=customers,
        drivers=drivers,
        vehicles=vehicles
    )

@bookings_bp.route('/detail/<int:booking_id>')
@login_required
@role_required('Super Admin', 'Operations Manager', 'Booking Operator')
def detail(booking_id):
    """View details of a booking, including payment transactions."""
    booking = Booking.query.get_or_404(booking_id)
    payments = Payment.query.filter_by(booking_id=booking.id).all()
    return render_template('bookings/detail.html', booking=booking, payments=payments)

@bookings_bp.route('/payment/<int:booking_id>', methods=['POST'])
@login_required
@role_required('Super Admin', 'Operations Manager', 'Booking Operator')
def process_payment(booking_id):
    """Creates a payment transaction for a booking."""
    booking = Booking.query.get_or_404(booking_id)
    amount = request.form.get('amount', 0.0, type=float)
    method = request.form.get('payment_method', 'Cash')
    
    if amount <= 0:
        flash("Payment amount must be greater than zero.", "danger")
        return redirect(url_for('bookings.detail', booking_id=booking.id))
        
    payment = Payment(
        booking_id=booking.id,
        amount=amount,
        payment_method=method,
        status='Completed'
    )
    db.session.add(payment)
    
    # Update payment status
    total_paid = sum(p.amount for p in Payment.query.filter_by(booking_id=booking.id, status='Completed').all()) + amount
    if total_paid >= booking.fare:
        booking.payment_status = 'Paid'
    elif total_paid > 0:
        booking.payment_status = 'Partial'
        
    log = ActivityLog(user_id=current_user.id, action="Booking Updates", details=f"Recorded Payment of INR {amount} via {method} for Booking {booking.id}.")
    db.session.add(log)
    db.session.commit()
    
    flash(f"Payment of INR {amount:.2f} processed successfully.", "success")
    return redirect(url_for('bookings.detail', booking_id=booking.id))
