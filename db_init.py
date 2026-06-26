from datetime import datetime, date, timedelta
from app import create_app
from app.models import db, User, Driver, Vehicle, Customer, Booking, Payment, Expense, Maintenance, Notification, ActivityLog

def seed_database():
    app = create_app()
    with app.app_context():
        print("Initializing database schema...")
        db.drop_all()
        db.create_all()
        print("Database schema generated successfully.")
        
        # 1. SEED STAFF USERS WITH ENTERPRISE ROLES
        print("Seeding Staff Users...")
        # Super Admin - must change password on login
        super_admin = User(
            username="admin",
            full_name="Jolly Super Admin",
            email="admin@jollycabs.in",
            phone="+91 9999999999",
            role="Super Admin",
            status="Active",
            must_change_password=True
        )
        super_admin.set_password("admin123")
        
        # Operations Manager
        ops_manager = User(
            username="manager",
            full_name="Rajesh Khanna (Operations)",
            email="manager@jollycabs.in",
            phone="+91 9888877777",
            role="Operations Manager",
            status="Active",
            must_change_password=False
        )
        ops_manager.set_password("manager123")
        
        # Booking Operator
        booking_op = User(
            username="dispatcher",
            full_name="Sanjay Sharma (Booking Desk)",
            email="dispatcher@jollycabs.in",
            phone="+91 9777766666",
            role="Booking Operator",
            status="Active",
            must_change_password=False
        )
        booking_op.set_password("dispatch123")
        
        # Driver Manager
        driver_mgr = User(
            username="drivermgr",
            full_name="Gurpreet Singh (Fleet Desk)",
            email="drivermgr@jollycabs.in",
            phone="+91 9666655555",
            role="Driver Manager",
            status="Active",
            must_change_password=False
        )
        driver_mgr.set_password("driver123")

        # Accounts Manager
        accts_mgr = User(
            username="accounts",
            full_name="Nisha Gupta (Accounts)",
            email="accounts@jollycabs.in",
            phone="+91 9555544444",
            role="Accounts Manager",
            status="Active",
            must_change_password=False
        )
        accts_mgr.set_password("accounts123")

        db.session.add_all([super_admin, ops_manager, booking_op, driver_mgr, accts_mgr])
        db.session.flush() # Secure IDs
        
        # 2. SEED DRIVERS
        print("Seeding Drivers...")
        today = date.today()
        
        driver1 = Driver(
            name="Rajesh Kumar",
            license_number="DL-1420180054321",
            license_expiry=today + timedelta(days=120),
            phone="+91 9876543210",
            email="rajesh.kumar@jollycabs.in",
            address="H-12, Sector 15, Rohini, New Delhi",
            availability="Available",
            status="Active"
        )
        driver2 = Driver(
            name="Suresh Pal",
            license_number="HR-2620150098765",
            license_expiry=today + timedelta(days=15),
            phone="+91 9811223344",
            email="suresh.pal@jollycabs.in",
            address="Flat 204, Sector 4, Dwarka, New Delhi",
            availability="Available",
            status="Active"
        )
        driver3 = Driver(
            name="Manpreet Singh",
            license_number="PB-0220190011223",
            license_expiry=today + timedelta(days=365),
            phone="+91 9540332211",
            email="manpreet.singh@jollycabs.in",
            address="15/4, Tilak Nagar, New Delhi",
            availability="Busy",
            status="Active"
        )
        driver4 = Driver(
            name="Vikram Rathore",
            license_number="UP-1620120044556",
            license_expiry=today + timedelta(days=200),
            phone="+91 9999887766",
            email="vikram.rathore@jollycabs.in",
            address="C-42, Sector 62, Noida, Uttar Pradesh",
            availability="Off-Duty",
            status="Active"
        )
        
        db.session.add_all([driver1, driver2, driver3, driver4])
        db.session.flush()

        # 3. SEED VEHICLES
        print("Seeding Vehicles Fleet...")
        vehicle1 = Vehicle(
            model="Maruti Suzuki Dzire",
            vehicle_number="DL-1YC-1234",
            fuel_type="CNG",
            insurance_expiry=today + timedelta(days=90),
            permit_expiry=today + timedelta(days=180),
            maintenance_status="Good",
            availability="Available"
        )
        vehicle2 = Vehicle(
            model="Toyota Etios",
            vehicle_number="DL-1YD-5678",
            fuel_type="Diesel",
            insurance_expiry=today + timedelta(days=10),
            permit_expiry=today + timedelta(days=120),
            maintenance_status="Good",
            availability="Available"
        )
        vehicle3 = Vehicle(
            model="Toyota Innova Crysta",
            vehicle_number="HR-55AT-9988",
            fuel_type="Diesel",
            insurance_expiry=today + timedelta(days=240),
            permit_expiry=today + timedelta(days=20),
            maintenance_status="Good",
            availability="Busy"
        )
        vehicle4 = Vehicle(
            model="Tata Nexon EV",
            vehicle_number="DL-1YE-0011",
            fuel_type="Electric",
            insurance_expiry=today + timedelta(days=300),
            permit_expiry=today + timedelta(days=320),
            maintenance_status="Under Maintenance",
            availability="Out of Service"
        )
        vehicle5 = Vehicle(
            model="Hyundai Aura",
            vehicle_number="UP-16ZT-4321",
            fuel_type="Petrol",
            insurance_expiry=today + timedelta(days=150),
            permit_expiry=today + timedelta(days=150),
            maintenance_status="Needs Inspection",
            availability="Available"
        )
        
        db.session.add_all([vehicle1, vehicle2, vehicle3, vehicle4, vehicle5])
        db.session.flush()

        # 4. SEED CUSTOMERS
        print("Seeding Customers Directory...")
        cust1 = Customer(name="Amit Sharma", phone="+91 9711223344", email="amit.sharma@gmail.com", address="B-3, Greater Kailash 1, New Delhi", status="Active")
        cust2 = Customer(name="Priya Nair", phone="+91 9650443322", email="priya.nair@yahoo.com", address="Flat 502, DLF Phase 3, Gurugram, Haryana", status="Active")
        cust3 = Customer(name="Rohan Das", phone="+91 9582110099", email="rohan.das@gmail.com", address="House 24, Gitanjali Enclave, New Delhi", status="Active")
        cust4 = Customer(name="Karan Malhotra", phone="+91 9899110022", email="karan.m@outlook.com", address="Sec 15, Noida, Uttar Pradesh", status="Active")
        
        db.session.add_all([cust1, cust2, cust3, cust4])
        db.session.flush()

        # 5. SEED BOOKINGS, PAYMENTS & EXPENSES
        print("Seeding Bookings & Finances...")
        b1 = Booking(
            customer_id=cust1.id,
            driver_id=driver1.id,
            vehicle_id=vehicle1.id,
            pickup_location="Terminal 3, IGI Airport, Delhi",
            drop_location="Connaught Place, New Delhi",
            booking_time=datetime.now() - timedelta(days=5, hours=4),
            trip_start_time=datetime.now() - timedelta(days=5, hours=3, minutes=45),
            trip_end_time=datetime.now() - timedelta(days=5, hours=3, minutes=10),
            distance=22.4,
            fare=680.0,
            status="Completed",
            payment_status="Paid"
        )
        db.session.add(b1)
        db.session.flush()
        
        p1 = Payment(booking_id=b1.id, amount=680.0, payment_method="UPI", status="Completed", payment_date=b1.trip_end_time)
        db.session.add(p1)
        
        b2 = Booking(
            customer_id=cust2.id,
            driver_id=driver2.id,
            vehicle_id=vehicle2.id,
            pickup_location="DLF Cyber City, Gurugram",
            drop_location="Saket District Center, New Delhi",
            booking_time=datetime.now() - timedelta(days=4, hours=2),
            trip_start_time=datetime.now() - timedelta(days=4, hours=1, minutes=50),
            trip_end_time=datetime.now() - timedelta(days=4, hours=1, minutes=10),
            distance=18.6,
            fare=540.0,
            status="Completed",
            payment_status="Paid"
        )
        db.session.add(b2)
        db.session.flush()
        
        p2 = Payment(booking_id=b2.id, amount=540.0, payment_method="Card", status="Completed", payment_date=b2.trip_end_time)
        db.session.add(p2)
        
        b3 = Booking(
            customer_id=cust3.id,
            driver_id=driver3.id,
            vehicle_id=vehicle3.id,
            pickup_location="Noida Sector 62, Noida",
            drop_location="Vasant Kunj, New Delhi",
            booking_time=datetime.now() - timedelta(hours=1),
            trip_start_time=datetime.now() - timedelta(minutes=45),
            distance=34.2,
            fare=1150.0,
            status="Ongoing",
            payment_status="Unpaid"
        )
        db.session.add(b3)
        
        b4 = Booking(
            customer_id=cust4.id,
            pickup_location="Rajouri Garden, New Delhi",
            drop_location="Karol Bagh, New Delhi",
            booking_time=datetime.now() - timedelta(days=2),
            distance=6.5,
            fare=220.0,
            status="Cancelled",
            payment_status="Unpaid"
        )
        db.session.add(b4)

        b5 = Booking(
            customer_id=cust1.id,
            driver_id=driver1.id,
            vehicle_id=vehicle1.id,
            pickup_location="Defence Colony, New Delhi",
            drop_location="IGI Airport, New Delhi",
            booking_time=datetime.now() - timedelta(days=1, hours=3),
            trip_start_time=datetime.now() - timedelta(days=1, hours=2, minutes=45),
            trip_end_time=datetime.now() - timedelta(days=1, hours=2),
            distance=15.0,
            fare=450.0,
            status="Completed",
            payment_status="Paid"
        )
        db.session.add(b5)
        db.session.flush()
        
        p5 = Payment(booking_id=b5.id, amount=450.0, payment_method="Cash", status="Completed", payment_date=b5.trip_end_time)
        db.session.add(p5)
        
        b6 = Booking(
            customer_id=cust3.id,
            driver_id=driver2.id,
            vehicle_id=vehicle2.id,
            pickup_location="Dwarka Mor, New Delhi",
            drop_location="Rajiv Chowk, New Delhi",
            booking_time=datetime.now() - timedelta(hours=5),
            trip_start_time=datetime.now() - timedelta(hours=4, minutes=45),
            trip_end_time=datetime.now() - timedelta(hours=4),
            distance=25.0,
            fare=780.0,
            status="Completed",
            payment_status="Paid"
        )
        db.session.add(b6)
        db.session.flush()
        
        p6 = Payment(booking_id=b6.id, amount=780.0, payment_method="UPI", status="Completed", payment_date=b6.trip_end_time)
        db.session.add(p6)

        # 6. SEED EXPENSES
        print("Seeding Expenses Ledger...")
        exp1 = Expense(type="Fuel", amount=1200.0, expense_date=today - timedelta(days=4), description="CNG refuel for vehicle DL-1YC-1234", vehicle_id=vehicle1.id)
        exp2 = Expense(type="Fuel", amount=2500.0, expense_date=today - timedelta(days=3), description="Diesel fill for vehicle DL-1YD-5678", vehicle_id=vehicle2.id)
        exp3 = Expense(type="Maintenance", amount=4800.0, expense_date=today - timedelta(days=2), description="Brake pad replacement and engine checkup", vehicle_id=vehicle4.id)
        exp4 = Expense(type="Salary", amount=15000.0, expense_date=today - timedelta(days=1), description="Weekly salary payout for driver Rajesh Kumar", driver_id=driver1.id)
        exp5 = Expense(type="Miscellaneous", amount=450.0, expense_date=today, description="Office refreshments / tea pantry items")
        
        db.session.add_all([exp1, exp2, exp3, exp4, exp5])

        # 7. SEED MAINTENANCE SCHEDULES
        print("Seeding Maintenance Logs...")
        m1 = Maintenance(vehicle_id=vehicle4.id, description="Battery diagnostic check & coolant flush", cost=4800.0, start_date=today - timedelta(days=2), status="In Progress")
        m2 = Maintenance(vehicle_id=vehicle1.id, description="AC servicing and air filters cleaning", cost=1500.0, start_date=today - timedelta(days=10), end_date=today - timedelta(days=10), status="Completed")
        
        db.session.add_all([m1, m2])

        # 8. SEED SYSTEM ACTION LOGS
        print("Seeding Activity Logs...")
        log1 = ActivityLog(user_id=super_admin.id, action="DB Seeding", details="Initial database schema generated and dummy corporate logs seeded.")
        db.session.add(log1)
        
        db.session.commit()
        print("Database setup and seeding completed successfully.")

if __name__ == '__main__':
    seed_database()
