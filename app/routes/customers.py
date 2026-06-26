from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import db, Customer, Booking, ActivityLog
from app.routes.auth import role_required

customers_bp = Blueprint('customers', __name__)

@customers_bp.route('/')
@login_required
@role_required('Super Admin', 'Operations Manager', 'Booking Operator')
def index():
    """Renders the customers registry list with pagination and contact search parameters."""
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('search', '').strip()
    status_filter = request.args.get('status', '').strip()
    
    query = Customer.query
    
    if search_query:
        query = query.filter(
            (Customer.name.like(f"%{search_query}%")) | 
            (Customer.phone.like(f"%{search_query}%")) | 
            (Customer.email.like(f"%{search_query}%"))
        )
    if status_filter:
        query = query.filter_by(status=status_filter)
        
    pagination = query.order_by(Customer.name.asc()).paginate(page=page, per_page=10, error_out=False)
    customers = pagination.items
    
    return render_template(
        'customers/list.html',
        customers=customers,
        pagination=pagination,
        search_query=search_query,
        status_filter=status_filter
    )

@customers_bp.route('/add', methods=['GET', 'POST'])
@login_required
@role_required('Super Admin', 'Operations Manager', 'Booking Operator')
def add():
    """Adds a new customer account to the suite registry."""
    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        email = request.form.get('email')
        address = request.form.get('address')
        status = request.form.get('status', 'Active')
        
        # Validations
        if not name or not phone or not email or not address:
            flash("All fields are required.", "danger")
            return redirect(url_for('customers.add'))
            
        existing_phone = Customer.query.filter_by(phone=phone).first()
        if existing_phone:
            flash("Phone number is already associated with an account.", "danger")
            return redirect(url_for('customers.add'))
            
        existing_email = Customer.query.filter_by(email=email).first()
        if existing_email:
            flash("Email address is already associated with an account.", "danger")
            return redirect(url_for('customers.add'))

        customer = Customer(
            name=name,
            phone=phone,
            email=email,
            address=address,
            status=status
        )
        
        db.session.add(customer)
        db.session.flush()
        
        log = ActivityLog(user_id=current_user.id, action="Customer Update", details=f"Registered customer {name} (Phone: {phone}).")
        db.session.add(log)
        db.session.commit()
        
        flash("Customer account registered successfully.", "success")
        return redirect(url_for('customers.index'))
        
    return render_template('customers/form.html', action="Add")

@customers_bp.route('/edit/<int:customer_id>', methods=['GET', 'POST'])
@login_required
@role_required('Super Admin', 'Operations Manager', 'Booking Operator')
def edit(customer_id):
    """Edits customer registration details."""
    customer = Customer.query.get_or_404(customer_id)
    
    if request.method == 'POST':
        customer.name = request.form.get('name')
        customer.phone = request.form.get('phone')
        customer.email = request.form.get('email')
        customer.address = request.form.get('address')
        customer.status = request.form.get('status')
        
        log = ActivityLog(user_id=current_user.id, action="Customer Update", details=f"Updated details for customer {customer.name} (ID: {customer.id}).")
        db.session.add(log)
        db.session.commit()
        
        flash("Customer profile updated successfully.", "success")
        return redirect(url_for('customers.index'))
        
    return render_template('customers/form.html', action="Edit", customer=customer)

@customers_bp.route('/profile/<int:customer_id>')
@login_required
@role_required('Super Admin', 'Operations Manager', 'Booking Operator')
def profile(customer_id):
    """View customer profiles and booking history logs."""
    customer = Customer.query.get_or_404(customer_id)
    bookings = Booking.query.filter_by(customer_id=customer.id).order_by(Booking.booking_time.desc()).all()
    completed_bookings = [b for b in bookings if b.status == 'Completed']
    total_trips = len(completed_bookings)
    total_spend = sum(b.fare for b in completed_bookings)
    
    return render_template(
        'customers/profile.html',
        customer=customer,
        bookings=bookings,
        total_trips=total_trips,
        total_spend=total_spend
    )

@customers_bp.route('/delete/<int:customer_id>', methods=['POST'])
@login_required
@role_required('Super Admin')
def delete(customer_id):
    """Deletes a customer profile permanently (Super Admin restricted)."""
    customer = Customer.query.get_or_404(customer_id)
    
    # Check for active bookings
    active_booking = Booking.query.filter(Booking.customer_id == customer.id, Booking.status.in_(['Ongoing', 'Dispatched'])).first()
    if active_booking:
        flash(f"Cannot delete customer {customer.name} because they have an active booking (ID: {active_booking.id}).", "danger")
        return redirect(url_for('customers.index'))
        
    log = ActivityLog(user_id=current_user.id, action="Customer Update", details=f"Deleted customer {customer.name} (ID: {customer.id}) permanently.")
    db.session.add(log)
    
    db.session.delete(customer)
    db.session.commit()
    
    flash("Customer profile deleted successfully.", "success")
    return redirect(url_for('customers.index'))
