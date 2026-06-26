from datetime import datetime, date, timedelta
from flask import Blueprint, render_template
from flask_login import login_required
from sqlalchemy import func, desc
from app.models import db, Booking, Payment, Customer
from app.routes.auth import role_required

revenue_bp = Blueprint('revenue', __name__)

@revenue_bp.route('/')
@login_required
@role_required('Super Admin', 'Accounts Manager')
def index():
    """Compiles revenue analytics, including periods totals, top routes, and top customers."""
    today = date.today()
    
    # 1. Today's Revenue
    start_of_today = datetime.combine(today, datetime.min.time())
    today_revenue = db.session.query(func.sum(Payment.amount))\
        .filter(Payment.status == 'Completed', Payment.payment_date >= start_of_today)\
        .scalar() or 0.0
        
    # 2. Weekly Revenue (Last 7 Days)
    start_of_week = start_of_today - timedelta(days=7)
    weekly_revenue = db.session.query(func.sum(Payment.amount))\
        .filter(Payment.status == 'Completed', Payment.payment_date >= start_of_week)\
        .scalar() or 0.0
        
    # 3. Monthly Revenue (Current Month)
    start_of_month = date(today.year, today.month, 1)
    monthly_revenue = db.session.query(func.sum(Payment.amount))\
        .filter(Payment.status == 'Completed', Payment.payment_date >= start_of_month)\
        .scalar() or 0.0
        
    # 4. Yearly Revenue (Current Year)
    start_of_year = date(today.year, 1, 1)
    yearly_revenue = db.session.query(func.sum(Payment.amount))\
        .filter(Payment.status == 'Completed', Payment.payment_date >= start_of_year)\
        .scalar() or 0.0

    # 5. Top Routes
    top_routes = db.session.query(
        Booking.pickup_location,
        Booking.drop_location,
        func.count(Booking.id).label('trips_count'),
        func.sum(Booking.fare).label('total_earnings')
    ).filter(Booking.status == 'Completed')\
     .group_by(Booking.pickup_location, Booking.drop_location)\
     .order_by(desc('trips_count'))\
     .limit(5).all()

    # 6. Top Customers
    top_customers = db.session.query(
        Customer.name,
        Customer.phone,
        func.count(Booking.id).label('trips_count'),
        func.sum(Booking.fare).label('total_spent')
    ).join(Booking, Booking.customer_id == Customer.id)\
     .filter(Booking.status == 'Completed', Booking.payment_status == 'Paid')\
     .group_by(Customer.id)\
     .order_by(desc('total_spent'))\
     .limit(5).all()

    # Last 10 payments
    recent_transactions = Payment.query.join(Booking).join(Customer)\
        .order_by(Payment.payment_date.desc()).limit(10).all()

    return render_template(
        'revenue/view.html',
        today_revenue=today_revenue,
        weekly_revenue=weekly_revenue,
        monthly_revenue=monthly_revenue,
        yearly_revenue=yearly_revenue,
        top_routes=top_routes,
        top_customers=top_customers,
        recent_transactions=recent_transactions
    )
