from datetime import datetime, date, timedelta
from app.models import db, Driver, Vehicle, Notification

class NotificationService:
    """Automates compliance scans and issues alerts for licensing and expirations."""
    
    @staticmethod
    def run_compliance_checks():
        """Scans database records for compliance deadlines and updates system notifications."""
        today = date.today()
        warning_window = today + timedelta(days=30)
        
        # 1. Check Driver License Expirations
        expiring_drivers = Driver.query.filter(
            Driver.license_expiry <= warning_window,
            Driver.status == 'Active'
        ).all()
        
        for driver in expiring_drivers:
            days_left = (driver.license_expiry - today).days
            msg = f"Driver {driver.name}'s driver's license (No: {driver.license_number}) "
            if days_left < 0:
                msg += f"expired on {driver.license_expiry.strftime('%Y-%m-%d')}!"
            else:
                msg += f"expires in {days_left} days on {driver.license_expiry.strftime('%Y-%m-%d')}."
            
            # Avoid duplicate warnings
            existing = Notification.query.filter_by(
                type='License Expiry',
                message=msg,
                status='Unread'
            ).first()
            if not existing:
                alert = Notification(type='License Expiry', message=msg, status='Unread')
                db.session.add(alert)
        
        # 2. Check Vehicle Insurance Expirations
        expiring_insurance = Vehicle.query.filter(
            Vehicle.insurance_expiry <= warning_window,
            Vehicle.availability != 'Out of Service'
        ).all()
        
        for vehicle in expiring_insurance:
            days_left = (vehicle.insurance_expiry - today).days
            msg = f"Vehicle {vehicle.vehicle_number} ({vehicle.model}) insurance "
            if days_left < 0:
                msg += f"expired on {vehicle.insurance_expiry.strftime('%Y-%m-%d')}!"
            else:
                msg += f"expires in {days_left} days on {vehicle.insurance_expiry.strftime('%Y-%m-%d')}."
                
            existing = Notification.query.filter_by(
                type='Insurance Expiry',
                message=msg,
                status='Unread'
            ).first()
            if not existing:
                alert = Notification(type='Insurance Expiry', message=msg, status='Unread')
                db.session.add(alert)
                
        # 3. Check Vehicle Permit Expirations
        expiring_permits = Vehicle.query.filter(
            Vehicle.permit_expiry <= warning_window,
            Vehicle.availability != 'Out of Service'
        ).all()
        
        for vehicle in expiring_permits:
            days_left = (vehicle.permit_expiry - today).days
            msg = f"Vehicle {vehicle.vehicle_number} ({vehicle.model}) commercial permit "
            if days_left < 0:
                msg += f"expired on {vehicle.permit_expiry.strftime('%Y-%m-%d')}!"
            else:
                msg += f"expires in {days_left} days on {vehicle.permit_expiry.strftime('%Y-%m-%d')}."
                
            existing = Notification.query.filter_by(
                type='Permit Expiry',
                message=msg,
                status='Unread'
            ).first()
            if not existing:
                alert = Notification(type='Permit Expiry', message=msg, status='Unread')
                db.session.add(alert)

        # 4. Check vehicles needing maintenance
        maintenance_vehicles = Vehicle.query.filter_by(
            maintenance_status='Needs Inspection'
        ).all()
        
        for vehicle in maintenance_vehicles:
            msg = f"Vehicle {vehicle.vehicle_number} ({vehicle.model}) is flagged as: Needs Inspection."
            existing = Notification.query.filter_by(
                type='Maintenance Due',
                message=msg,
                status='Unread'
            ).first()
            if not existing:
                alert = Notification(type='Maintenance Due', message=msg, status='Unread')
                db.session.add(alert)
                
        db.session.commit()

    @staticmethod
    def get_unread_count():
        """Returns the number of unread alerts."""
        return Notification.query.filter_by(status='Unread').count()

    @staticmethod
    def get_latest_notifications(limit=5):
        """Fetches latest notifications."""
        return Notification.query.order_by(Notification.created_at.desc()).limit(limit).all()
