import json
from datetime import datetime, date, timedelta
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from sqlalchemy import func
from app.models import db, Driver, Vehicle, Customer, Booking, Payment, Expense, Notification
from app.services.notification_service import NotificationService
from app.routes.auth import role_required

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
@role_required('Super Admin', 'Operations Manager')
def index():
    """Gathers real-time statistics and aggregates charts data for corporate metrics."""
    # Automatically execute compliance checks to refresh active warnings
    NotificationService.run_compliance_checks()
    
    today = date.today()
    start_of_today = datetime.combine(today, datetime.min.time())
    start_of_month = date(today.year, today.month, 1)
    
    # --- KPI METRICS ---
    total_bookings = Booking.query.count()
    todays_trips = Booking.query.filter(Booking.booking_time >= start_of_today).count()
    
    # Monthly Revenue: Sum of payments in the current month
    monthly_revenue = db.session.query(func.sum(Payment.amount))\
        .filter(Payment.status == 'Completed', Payment.payment_date >= start_of_month)\
        .scalar() or 0.0
        
    active_drivers = Driver.query.filter(Driver.availability.in_(['Available', 'Busy']), Driver.status == 'Active').count()
    active_vehicles = Vehicle.query.filter(Vehicle.availability.in_(['Available', 'Busy'])).count()
    
    completed_trips = Booking.query.filter_by(status='Completed').count()
    cancelled_trips = Booking.query.filter_by(status='Cancelled').count()
    
    pending_payments = Booking.query.filter(Booking.payment_status.in_(['Unpaid', 'Partial'])).count()
    
    # --- CHART DATA 1: REVENUE TREND (Last 7 Days) ---
    revenue_chart_labels = []
    revenue_chart_values = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        revenue_chart_labels.append(day.strftime('%a'))
        day_start = datetime.combine(day, datetime.min.time())
        day_end = datetime.combine(day, datetime.max.time())
        
        day_rev = db.session.query(func.sum(Payment.amount))\
            .filter(Payment.status == 'Completed', Payment.payment_date >= day_start, Payment.payment_date <= day_end)\
            .scalar() or 0.0
        revenue_chart_values.append(day_rev)
        
    revenue_chart_data = {
        'labels': revenue_chart_labels,
        'values': revenue_chart_values
    }

    # --- CHART DATA 2: BOOKINGS TREND (Last 7 Days) ---
    bookings_chart_labels = []
    bookings_chart_values = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        bookings_chart_labels.append(day.strftime('%a'))
        day_start = datetime.combine(day, datetime.min.time())
        day_end = datetime.combine(day, datetime.max.time())
        
        day_count = Booking.query.filter(Booking.booking_time >= day_start, Booking.booking_time <= day_end).count()
        bookings_chart_values.append(day_count)
        
    bookings_chart_data = {
        'labels': bookings_chart_labels,
        'values': bookings_chart_values
    }

    # --- CHART DATA 3: VEHICLE UTILIZATION ---
    v_avail = Vehicle.query.filter_by(availability='Available').count()
    v_busy = Vehicle.query.filter_by(availability='Busy').count()
    v_maintenance = Vehicle.query.filter_by(availability='Out of Service').count()
    
    vehicle_chart_data = {
        'labels': ['Available', 'Busy', 'Out of Service'],
        'values': [v_avail, v_busy, v_maintenance]
    }

    # --- CHART DATA 4: DRIVER PERFORMANCE (Top 5 Drivers by Completed Trips) ---
    top_drivers = db.session.query(Driver.name, func.count(Booking.id))\
        .join(Booking, Booking.driver_id == Driver.id)\
        .filter(Booking.status == 'Completed')\
        .group_by(Driver.id)\
        .order_by(func.count(Booking.id).desc())\
        .limit(5).all()
        
    driver_performance_labels = [row[0] for row in top_drivers]
    driver_performance_values = [row[1] for row in top_drivers]
    
    driver_chart_data = {
        'labels': driver_performance_labels,
        'values': driver_performance_values
    }
    
    # Recent Bookings (limit 5)
    recent_bookings = Booking.query.order_by(Booking.booking_time.desc()).limit(5).all()

    return render_template(
        'dashboard.html',
        total_bookings=total_bookings,
        todays_trips=todays_trips,
        monthly_revenue=monthly_revenue,
        active_drivers=active_drivers,
        active_vehicles=active_vehicles,
        completed_trips=completed_trips,
        cancelled_trips=cancelled_trips,
        pending_payments=pending_payments,
        revenue_chart_data=json.dumps(revenue_chart_data),
        bookings_chart_data=json.dumps(bookings_chart_data),
        vehicle_chart_data=json.dumps(vehicle_chart_data),
        driver_chart_data=json.dumps(driver_chart_data),
        recent_bookings=recent_bookings
    )
