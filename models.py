from flask.ext.sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import time

db = SQLAlchemy()


class Codes(db.Model):
    __tablename__ = 'codes'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    manufacturer = db.Column(db.String(200))
    device_type = db.Column(db.String(200))
    action = db.Column(db.String(200))
    code = db.Column(db.Text())  # code is comma separated, starting with the first high pulse

    def __init__(self, man, type, action, code):
        self.manufacturer = man
        self.device_type = type
        self.action = action
        self.code = code


# A class that holds a device's settings
class DeviceSettings(db.Model):
    __tablename__ = 'device_settings'
    device_id = db.Column(db.Integer, db.ForeignKey('user_devices.device_id'), primary_key=True)
    upper_temp = db.Column(db.Float)
    lower_temp = db.Column(db.Float)

    def __init__(self, device_id):
        self.device_id = device_id
        self.upper_temp = 90.0
        self.lower_temp = 70.0

    def update(self, lower_limit=None, higher_limit=None):
        if lower_limit is not None:
            self.lower_temp = lower_limit
        if higher_limit is not None:
            self.upper_temp = higher_limit


# This is a class that relates devices to actions they have to perform
class DeviceAction(db.Model):
    __tablename__ = 'device_action'
    action_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    device_id = db.Column(db.Integer, db.ForeignKey('user_devices.device_id'))
    code_id = db.Column(db.Integer, db.ForeignKey('codes.id'))
    action = db.Column(db.String(200))
    time = db.Column(db.Integer)
    complete = db.Column(db.Boolean)

    def __init__(self, device_id, action, code):
        self.device_id = device_id
        self.action = action
        self.code_id = code
        self.time = time.time()
        self.complete = False


# class that hold the status of each device
class DeviceStatus(db.Model):
    __tablename__ = 'device_status'
    device_id = db.Column(db.Integer(), db.ForeignKey('user_devices.device_id'), primary_key=True)  # unique device ID
    temp = db.Column(db.Float)
    humidity = db.Column(db.Float)
    time = db.Column(db.Integer)

    def __init__(self, device_id, t=0, h=0):
        self.temp = t
        self.humidity = h
        self.device_id = device_id

    def update(self, temp=0, humidity=0):
        if not temp == 0:
            self.temp = temp
        if not humidity == 0:
            self.humidity = humidity


# class that relates users to their devices
class UserDevices(db.Model):
    __tablename__ = 'user_devices'
    device_id = db.Column(db.Integer(), primary_key=True)  # unique device ID
    email = db.Column(db.String(255), db.ForeignKey('user.email'))  # owner of the device
    device = db.Column(db.String(200))  # Device's Common Name

    def __init__(self, device_id, email, device):
        self.device_id = device_id
        self.email = email
        self.device = device


# class that holds user credentials
class User(db.Model):
    __tablename__ = 'user'
    email = db.Column(db.String(255), primary_key=True)  # Email Address
    password = db.Column(db.String(255))  # Hashed and salted Password
    authenticated = db.Column(db.Boolean, default=False)  # keeps track if the user is logged in or not

    def __init__(self, email, password, auth):
        self.email = email
        self.authenticated = auth
        self.set_password(password)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.pw_hash, password)

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