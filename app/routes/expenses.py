from datetime import datetime, date
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from sqlalchemy import func
from app.models import db, Expense, Vehicle, Driver, Booking, ActivityLog
from app.routes.auth import role_required

expenses_bp = Blueprint('expenses', __name__)

@expenses_bp.route('/')
@login_required
@role_required('Super Admin', 'Accounts Manager')
def index():
    """Renders the expense ledger lists with summaries and classification filters."""
    page = request.args.get('page', 1, type=int)
    type_filter = request.args.get('type', '').strip()
    search_query = request.args.get('search', '').strip()
    
    query = Expense.query
    
    if type_filter:
        query = query.filter_by(type=type_filter)
    if search_query:
        query = query.filter(Expense.description.like(f"%{search_query}%"))
        
    pagination = query.order_by(Expense.expense_date.desc()).paginate(page=page, per_page=10, error_out=False)
    expenses = pagination.items
    
    # Financial summaries
    total_expenses = db.session.query(func.sum(Expense.amount)).scalar() or 0.0
    fuel_expenses = db.session.query(func.sum(Expense.amount)).filter_by(type='Fuel').scalar() or 0.0
    maint_expenses = db.session.query(func.sum(Expense.amount)).filter_by(type='Maintenance').scalar() or 0.0
    salary_expenses = db.session.query(func.sum(Expense.amount)).filter_by(type='Salary').scalar() or 0.0
    misc_expenses = db.session.query(func.sum(Expense.amount)).filter_by(type='Miscellaneous').scalar() or 0.0
    
    return render_template(
        'expenses/list.html',
        expenses=expenses,
        pagination=pagination,
        type_filter=type_filter,
        search_query=search_query,
        total_expenses=total_expenses,
        fuel_expenses=fuel_expenses,
        maint_expenses=maint_expenses,
        salary_expenses=salary_expenses,
        misc_expenses=misc_expenses
    )

@expenses_bp.route('/add', methods=['GET', 'POST'])
@login_required
@role_required('Super Admin', 'Accounts Manager')
def add():
    """Logs a new expense transaction in the general ledger."""
    if request.method == 'POST':
        type_ = request.form.get('type')
        amount = request.form.get('amount', 0.0, type=float)
        expense_date_str = request.form.get('expense_date')
        description = request.form.get('description')
        vehicle_id = request.form.get('vehicle_id')
        driver_id = request.form.get('driver_id')
        
        # Validations
        if not type_ or amount <= 0 or not expense_date_str or not description:
            flash("Mandatory fields missing or invalid amount.", "danger")
            return redirect(url_for('expenses.add'))
            
        try:
            expense_date = datetime.strptime(expense_date_str, '%Y-%m-%d').date()
        except ValueError:
            flash("Invalid date format. Use YYYY-MM-DD.", "danger")
            return redirect(url_for('expenses.add'))

        v_id = int(vehicle_id) if vehicle_id and vehicle_id != 'None' else None
        d_id = int(driver_id) if driver_id and driver_id != 'None' else None

        expense = Expense(
            type=type_,
            amount=amount,
            expense_date=expense_date,
            description=description,
            vehicle_id=v_id,
            driver_id=d_id
        )
        
        db.session.add(expense)
        db.session.flush()
        
        log = ActivityLog(user_id=current_user.id, action="Create Expense", details=f"Logged {type_} expense: INR {amount:.2f}.")
        db.session.add(log)
        db.session.commit()
        
        flash("Expense transaction recorded successfully.", "success")
        return redirect(url_for('expenses.index'))
        
    vehicles = Vehicle.query.all()
    drivers = Driver.query.filter_by(status='Active').all()
    
    return render_template(
        'expenses/form.html',
        action="Add",
        vehicles=vehicles,
        drivers=drivers
    )

@expenses_bp.route('/delete/<int:expense_id>', methods=['POST'])
@login_required
@role_required('Super Admin')
def delete(expense_id):
    """Deletes an expense log permanently (Super Admin restricted)."""
    expense = Expense.query.get_or_404(expense_id)
    
    log = ActivityLog(user_id=current_user.id, action="Delete Expense", details=f"Deleted expense record ID: {expense.id} (INR {expense.amount:.2f}).")
    db.session.add(log)
    
    db.session.delete(expense)
    db.session.commit()
    
    flash("Expense transaction deleted successfully.", "success")
    return redirect(url_for('expenses.index'))

@expenses_bp.route('/report')
@login_required
@role_required('Super Admin', 'Accounts Manager')
def report():
    """Generates monthly aggregate cost dashboards."""
    today = date.today()
    current_year = request.args.get('year', today.year, type=int)
    
    monthly_aggregates = db.session.query(
        func.strftime('%m', Expense.expense_date).label('month'),
        func.sum(Expense.amount).label('total')
    ).filter(func.strftime('%Y', Expense.expense_date) == str(current_year))\
     .group_by('month')\
     .order_by('month')\
     .all()
     
    months_labels = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    months_totals = [0.0] * 12
    
    for row in monthly_aggregates:
        try:
            m_idx = int(row[0]) - 1
            months_totals[m_idx] = float(row[1])
        except (ValueError, IndexError):
            continue
            
    expense_by_type = db.session.query(
        Expense.type,
        func.sum(Expense.amount)
    ).filter(func.strftime('%Y', Expense.expense_date) == str(current_year))\
     .group_by(Expense.type)\
     .all()
     
    return render_template(
        'expenses/report.html',
        current_year=current_year,
        months_labels=months_labels,
        months_totals=months_totals,
        expense_by_type=expense_by_type
    )
