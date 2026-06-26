from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class BaseModel:
    """Base model logic containing standard primary keys and timestamps."""
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class User(db.Model, UserMixin, BaseModel):
    """User account model supporting custom roles and access control."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Roles: Super Admin, Operations Manager, Booking Operator, Driver Manager, Accounts Manager
    role = db.Column(db.String(30), default='Booking Operator', nullable=False)
    status = db.Column(db.String(20), default='Active', nullable=False)          # Active, Inactive
    profile_photo = db.Column(db.String(255), nullable=True)                      # Path to uploaded photo
    
    last_login = db.Column(db.DateTime, nullable=True)
    must_change_password = db.Column(db.Boolean, default=False, nullable=False)   # Force password change flag

    @property
    def name(self):
        return self.full_name

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def has_role(self, *roles):
        return self.role in roles


class Driver(db.Model, BaseModel):
    """Cabs drivers tracking availability, licenses, and status."""
    __tablename__ = 'drivers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    license_number = db.Column(db.String(50), unique=True, nullable=False)
    license_expiry = db.Column(db.Date, nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    address = db.Column(db.Text, nullable=False)
    availability = db.Column(db.String(20), default='Available', nullable=False)  # Available, Busy, Off-Duty
    status = db.Column(db.String(20), default='Active', nullable=False)            # Active, Suspended, Inactive

    # Relationships
    bookings = db.relationship('Booking', backref='driver', lazy=True)
    expenses = db.relationship('Expense', backref='driver', lazy=True)


class Vehicle(db.Model, BaseModel):
    """Company vehicles details, maintenance status, and documents."""
    __tablename__ = 'vehicles'
    
    id = db.Column(db.Integer, primary_key=True)
    model = db.Column(db.String(100), nullable=False)
    vehicle_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    fuel_type = db.Column(db.String(20), nullable=False)                          # Petrol, Diesel, CNG, Electric
    insurance_expiry = db.Column(db.Date, nullable=False)
    permit_expiry = db.Column(db.Date, nullable=False)
    maintenance_status = db.Column(db.String(20), default='Good', nullable=False) # Good, Under Maintenance, Needs Inspection
    availability = db.Column(db.String(20), default='Available', nullable=False)  # Available, Busy, Out of Service

    # Relationships
    bookings = db.relationship('Booking', backref='vehicle', lazy=True)
    maintenance_records = db.relationship('Maintenance', backref='vehicle', lazy=True, cascade="all, delete-orphan")
    expenses = db.relationship('Expense', backref='vehicle', lazy=True)


class Customer(db.Model, BaseModel):
    """Customer accounts profiles and registration details."""
    __tablename__ = 'customers'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    address = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='Active', nullable=False)            # Active, Inactive

    # Relationships
    bookings = db.relationship('Booking', backref='customer', lazy=True)


class Booking(db.Model, BaseModel):
    """Trip reservation records tracking dispatch status, pricing, and timing."""
    __tablename__ = 'bookings'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    driver_id = db.Column(db.Integer, db.ForeignKey('drivers.id'), nullable=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=True)
    
    pickup_location = db.Column(db.String(255), nullable=False)
    drop_location = db.Column(db.String(255), nullable=False)
    booking_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    trip_start_time = db.Column(db.DateTime, nullable=True)
    trip_end_time = db.Column(db.DateTime, nullable=True)
    distance = db.Column(db.Float, default=0.0, nullable=False)
    fare = db.Column(db.Float, default=0.0, nullable=False)
    status = db.Column(db.String(20), default='Pending', nullable=False)           # Pending, Dispatched, Ongoing, Completed, Cancelled
    payment_status = db.Column(db.String(20), default='Unpaid', nullable=False)     # Unpaid, Paid, Partial

    # Relationships
    payments = db.relationship('Payment', backref='booking', lazy=True, cascade="all, delete-orphan")
    expenses = db.relationship('Expense', backref='booking', lazy=True)


class Payment(db.Model, BaseModel):
    """Financial transaction logs mapping to specific customer bookings."""
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(30), nullable=False)                     # Cash, Card, UPI, Corporate Netbanking
    status = db.Column(db.String(20), default='Completed', nullable=False)         # Completed, Refunded, Failed
    payment_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


class Expense(db.Model, BaseModel):
    """Operations expenses logs tracking maintenance, fuel, and salaries."""
    __tablename__ = 'expenses'
    
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(30), nullable=False, index=True)                   # Fuel, Maintenance, Salary, Miscellaneous
    amount = db.Column(db.Float, nullable=False)
    expense_date = db.Column(db.Date, default=datetime.utcnow, nullable=False)
    description = db.Column(db.Text, nullable=False)
    
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=True)
    driver_id = db.Column(db.Integer, db.ForeignKey('drivers.id'), nullable=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=True)


class Maintenance(db.Model, BaseModel):
    """Repair logs and schedule checkups for the vehicles fleet."""
    __tablename__ = 'maintenance'
    
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicles.id'), nullable=False)
    description = db.Column(db.Text, nullable=False)
    cost = db.Column(db.Float, default=0.0, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(20), default='Scheduled', nullable=False)         # Scheduled, In Progress, Completed


class Notification(db.Model, BaseModel):
    """System-generated reminder notifications regarding compliance (insurance, permit, maintenance)."""
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='Unread', nullable=False)            # Unread, Read


class ActivityLog(db.Model):
    """Audit trails tracking administrative actions and system security."""
    __tablename__ = 'activity_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)     # Linked to users.id
    action = db.Column(db.String(100), nullable=False)
    details = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship
    user = db.relationship('User', backref=db.backref('logs', lazy=True, cascade="all, delete-orphan"))
