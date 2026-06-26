# Jolly Cabs Operations Management Suite (JOMS)

JOMS is a premium, enterprise-grade fleet operations and business management suite custom built for **Jolly Cabs** (https://www.jollycabs.in). 

It is designed to manage day-to-day corporate taxi logistics, including driver schedules, vehicle availability, compliance, customer logs, trip scheduling, expense recording, billing transactions, and aggregate financial reports. The user interface draws inspiration from premium control dashboards used by Ola, Uber, and corporate fleet operators, built from the ground up with a responsive light/dark theme.

---

## Technical Stack
- **Backend:** Python 3, Flask, SQLAlchemy (Object-Oriented, PEP-8 compliant)
- **Database:** SQLite (Normalized SQL, easily swappable with MySQL/Postgres via SQLAlchemy URI)
- **Frontend:** HTML5, Vanilla CSS3 (Custom design system variables, glassmorphism, responsive grids), Vanilla JS (theme persistence, global search, table query filters)
- **Charts:** Chart.js (Line trends, Doughnut utilization, horizontal bar performance)
- **Security:** Password Hashing (Werkzeug PBKDF2), HTTPOnly session cookies, SQL injection protection (SQLAlchemy Parameterized Queries), and role-based access checks.

---

## Core Features
1. **Authentication:** Secure logins, logout audits, forgot-password simulation, and Role-Based Access Control (RBAC) supporting Super Admins, Managers, and Dispatchers.
2. **Operations Dashboard:** Live widgets displaying KPIs (trips count, active assets, monthly revenue) alongside interactive data graphs.
3. **Driver Management:** Profiles grid, license expirations tracking, contact details, status toggles, and total completed trips/earnings audits.
4. **Vehicle Fleet Management:** Registry monitoring, plate numbers, fuel selections, compliance expirations (insurance, permits), and health status alerts.
5. **Customer Directory:** Ride histories, registration logs, billing metrics, and active account toggles.
6. **Booking Dispatcher:** Trip scheduler with auto-allocations, route details (pick/drop), distance, fare calculations, and payment tracking.
7. **Expense Ledger:** Track costs (fuel bills, maintenance invoices, payroll salaries) mapped to drivers and cars.
8. **Revenue Analytics:** Period aggregates (daily, weekly, monthly, yearly), top route margins, and top high-value customers.
9. **Reports Exporter:** Export data sheets as CSV, Microsoft Excel (via openpyxl), or printable PDF reports (via reportlab) with running footers.
10. **System Warnings (Compliance):** Automatic daily checks on licenses, insurance policies, and permit deadlines within 30 days, raising unread dashboard notifications.

---

## Directory Structure
```
c:\Users\kalav\OneDrive\Desktop\python project
├── run.py                       # App runner entry point
├── requirements.txt             # Project package specifications
├── db_init.py                   # DB creation & seed script
├── README.md                    # System documentation
└── app/
    ├── __init__.py              # Factory pattern builder
    ├── config.py                # Server & SQL configs
    ├── models.py                # Database models
    ├── routes/
    │   ├── __init__.py          
    │   ├── auth.py              # Login & credentials views
    │   ├── dashboard.py         # Dashboard widget metrics
    │   ├── drivers.py           # Driver profiles CRUD
    │   ├── vehicles.py          # Fleet vehicles CRUD
    │   ├── customers.py         # Customer accounts CRUD
    │   ├── bookings.py          # Bookings scheduler & payments
    │   ├── expenses.py          # Expense tracking & reports
    │   ├── revenue.py           # Revenue periods summaries
    │   └── admin.py             # Roles, backups, reports & search
    ├── services/
    │   ├── __init__.py
    │   ├── backup_service.py    # SQLite database backups helper
    │   ├── notification_service.py # Expirations checks runner
    │   └── report_service.py    # CSV/PDF/Excel builders
    ├── static/
    │   ├── css/
    │   │   └── style.css        # CSS variables & dark mode styles
    │   └── js/
    │       ├── main.js          # Theme toggles & search scripts
    │       └── charts.js        # Chart.js configs
    └── templates/
        ├── base.html            # Layout framework
        ├── login.html           # Login screen
        ├── dashboard.html       # Analytics dashboard
        ├── drivers/             # Drivers views
        ├── vehicles/            # Fleet views
        ├── customers/           # Customers views
        ├── bookings/            # Trips views
        ├── expenses/            # Costs views
        ├── revenue/             # Revenue views
        ├── notifications/       # Alerts panel
        ├── admin/               # Backups & staff views
        └── reports/             # Reports exports index
```

---

## Database Design

The database schema is fully normalized. Indices have been added to highly queried columns (`username`, `vehicle_number`, `phone`, `type`, etc.) to optimize reads:

### Model Entities
- **Admin:** `id` (PK), `username` (Index), `password_hash`, `email` (Unique), `name`, `role`, `created_at`, `updated_at`
- **Driver:** `id` (PK), `name` (Index), `license_number` (Unique), `license_expiry`, `phone` (Unique), `email`, `address`, `availability`, `status`, `created_at`, `updated_at`
- **Vehicle:** `id` (PK), `model`, `vehicle_number` (Unique, Index), `fuel_type`, `insurance_expiry`, `permit_expiry`, `maintenance_status`, `availability`, `created_at`, `updated_at`
- **Customer:** `id` (PK), `name` (Index), `phone` (Unique), `email` (Unique), `address`, `status`, `created_at`, `updated_at`
- **Booking:** `id` (PK), `customer_id` (FK), `driver_id` (FK), `vehicle_id` (FK), `pickup_location`, `drop_location`, `distance`, `fare`, `status`, `payment_status`, `booking_time`, `trip_start_time`, `trip_end_time`, `created_at`, `updated_at`
- **Payment:** `id` (PK), `booking_id` (FK), `amount`, `payment_method`, `status`, `payment_date`, `created_at`, `updated_at`
- **Expense:** `id` (PK), `type` (Index), `amount`, `expense_date`, `description`, `vehicle_id` (FK), `driver_id` (FK), `booking_id` (FK), `created_at`, `updated_at`
- **Maintenance:** `id` (PK), `vehicle_id` (FK), `description`, `cost`, `start_date`, `end_date`, `status`, `created_at`, `updated_at`
- **Notification:** `id` (PK), `type`, `message`, `status`, `created_at`, `updated_at`
- **ActivityLog:** `id` (PK), `admin_id` (FK), `action`, `details`, `timestamp`

---

## Installation & Setup

Follow these steps to run JOMS locally:

### 1. Pre-requisites
Ensure you have **Python 3.8+** installed on your system.

### 2. Install Dependencies
Open your command terminal in the project workspace directory and run:
```bash
pip install -r requirements.txt
```
*Note: All packages are pure Python (including `openpyxl` and `reportlab`), ensuring compile-free installation on Windows.*

### 3. Initialize & Seed Database
Run the setup script to construct tables and load dummy data:
```bash
python db_init.py
```
This builds a local database file `app/joms.db` with sample drivers, soon-to-expire documents (to trigger active notification badges), bookings, and expenses.

### 4. Launch Application
Start the development web server:
```bash
python run.py
```
Open your browser and navigate to `http://localhost:5000`.

---

## Staff Accounts Seeding (Sign In Credentials)
Use these seeded accounts to test different roles inside JOMS:

1. **Super Admin Account**
   - **Username:** `admin`
   - **Password:** `admin123`
   - *Privilege:* Full system privileges, database backups management, role changes, and activity audit access.

2. **Manager Account**
   - **Username:** `manager`
   - **Password:** `manager123`
   - *Privilege:* Manage booking operations, register fleet, track expenses, view revenue analytics, and export reports.

3. **Dispatcher Account**
   - **Username:** `dispatcher`
   - **Password:** `dispatch123`
   - *Privilege:* Restricted dispatch dashboard. Allowed to schedule trips and assign vehicles/drivers, but cannot access financial records (revenue metrics, expenses log, or admin backup).
