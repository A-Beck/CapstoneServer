from flask import Flask, render_template, request, redirect
from flask.ext.sqlalchemy import SQLAlchemy
import time
import random

# setup environment stuff
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///capstone.db'
db = SQLAlchemy(app)


# TODO: Create a table that holds user credentials
# TODO: create a table that relates users to devices
# TODO: Error Checking for all user generated values
# TODO: Error Checking for DB accesses
# TODO: Better return codes
# TODO: Make Everything Pretty
# TODO: User sessions


# This is a class that relates devices to actions they have to perform
class DeviceAction(db.Model):
    __tablename__ = 'device_action'
    id = db.Column(db.Integer, primary_key=True)
    device = db.Column(db.String(20), unique=False)
    action = db.Column(db.String(50), unique=False)
    time = db.Column(db.Integer)
    complete = db.Column(db.Boolean, unique=False)

    def __init__(self, device, action):
        self.device = device
        self.action = action
        self.complete = False
        self.time = time.time()


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
class Users(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))

    def __init__(self, email, password):
        self.email = email
        self.password = password


#######################################################################################################################


#the homepage for our app
@app.route('/')
def index():
    return render_template('index.html')


#TODO: create route that will allow log in
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = Users.query.filter_by(email=email).first()
        if user.password == password:
            return 'login success'
        else:
            return 'login fail'
    else:
        return render_template('login.html')


#TODO: Error checking
#TODO: add encryption and stuff
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        db.session.add(Users(email, password))
        db.session.commit()
        return redirect('/')
    else:
        return render_template('register.html')


#view actions that have been submitted
@app.route('/actions')
def actions():
    all_actions = DeviceAction.query.all()
    return render_template('actions.html', actions=all_actions)


# endpoint for a device - the url it hits to get it's next command
@app.route('/getcommand/<device>')
def getcommand(device):
    # # TODO: add logic that will send responses based on info in DB
    # formated_string = ''
    # # This line gets all uncompleted actions for the specified device
    # commands = DeviceAction.query.filter_by(device=device, complete=False)
    # for command in commands:
    #     formated_string += ' ' + str(command.action) + ' ' + str(command.id)
    number = random.randint(0, 1)
    return str(number)


#adding a command to a device's command queue
@app.route('/addcommand', methods=['POST', 'GET'])
def addcommand():
    if request.method == 'POST':
        device = request.form['device']
        action = request.form['action']
        db.session.add(DeviceAction(device, action))
        db.session.commit()
        return redirect('/actions')
    else:
        return render_template('addcommand.html')
    
    
# TODO: add route that allows mC to mark task as done
@app.route('/completetask/<taskid>')
def completetask(taskid):
    try:
        device_action = DeviceAction.query.get(taskid)
        device_action.complete = True
        db.session.commit()
        return '1'
    except Exception as e:
        print e
        return '0'


# TODO: add route that will allow mC to post temp data
@app.route('/sendtemp/device=<device>&temp=<temp>')
def sendtemp(device, temp):
    try:
        device = DeviceStatus.query.get(device)
        device.temp = temp
        device.time = time.time()
        db.session.commit()
        return '1'
    except Exception as e:
        print e
        return '0'
    

app.debug = True

if __name__ == '__main__':
    db.create_all()
    app.run()
