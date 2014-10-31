from flask.ext.sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


# This is a class that relates devices to actions they have to perform
class DeviceAction(db.Model):
    __tablename__ = 'device_action'
    id = db.Column(db.Integer, primary_key=True)
    device = db.Column(db.String(20), unique=False)
    action = db.Column(db.String(50), unique=False)
    time = db.Column(db.Integer)
    complete = db.Column(db.Boolean, unique=False)


# class that hold the status of each device
class DeviceStatus(db.Model):
    __tablename__ = 'device_status'
    device = db.Column(db.String(20), primary_key=True)
    temp = db.Column(db.Float, unique=False)
    humidity = db.Column(db.Float, unique=False)
    time = db.Column(db.Integer)


# class that relates users to their devices
class UserDevices(db.Model):
    __tablename__ = 'user_devices'
    id = db.Column(db.Integer(), primary_key=True)
    user = db.Column(db.String(80))
    device = db.Column(db.String(20))


# class that holds user credentials
class User(db.Model):
    __tablename__ = 'user'
    email = db.Column(db.String(255), primary_key=True)
    password = db.Column(db.String(255))
    authenticated = db.Column(db.Boolean, default=False)

    def __init__(self, email, password, auth):
        self.email = email
        self.authenticated = auth
        self.set_password(password)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.pw_hash, password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def is_active(self):
        """True, as all users are active."""
        return True

    def get_id(self):
        """Return the email address to satisfy Flask-Login's requirements."""
        return self.email

    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return self.authenticated

    def is_anonymous(self):
        """False, as anonymous users aren't supported."""
        return False