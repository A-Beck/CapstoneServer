from flask import Flask, render_template, request, redirect
from models import User, UserDevices, DeviceStatus, DeviceAction, db
from flask.ext.login import LoginManager, login_required, login_user, logout_user, current_user
import time
import random

# TODO: Error Checking for all user generated values
# TODO: Error Checking for DB accesses
# TODO: Better return codes to send to msp
# TODO: Better user exp on site (logout on every page, clean easy interface)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///capstone.db'
app.secret_key = 'Super Secret'
db.app = app
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def user_loader(user_id):
    return User.query.get(user_id)


# the homepage for our app
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/profile')
@login_required
def profile():
    user = current_user
    return render_template('profile.html', user=user)


@app.route("/logout", methods=["GET"])
@login_required
def logout():
    """Logout the current user."""
    user = current_user
    user.authenticated = False
    db.session.add(user)
    db.session.commit()
    logout_user()
    return redirect('/')


@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    user = User.query.filter_by(email=email).first()
    if user.check_password(password):
        user.authenticated = True
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect('/profile')
    else:
        return 'login fail'


# TODO: Error checking
@app.route('/register', methods=['POST'])
def register():
    email = request.form['email']
    password = request.form['password']
    user = User(email, password, True)
    db.session.add(user)
    db.session.commit()
    login_user(user)
    return redirect('/profile')


#view actions that have been submitted
#TODO: only see actions for that user's devices
@app.route('/actions')
@login_required
def actions():
    all_actions = DeviceAction.query.all()
    return render_template('actions.html', actions=all_actions)


#adding a command to a device's command queue
# Todo: only show users devices in dropdown instead of text input
@app.route('/addcommand', methods=['POST', 'GET'])
@login_required
def addcommand():
    if request.method == 'POST':
        device = request.form['device']
        action = request.form['action']
        db.session.add(DeviceAction(device, action))
        db.session.commit()
        return redirect('/actions')
    else:
        return render_template('addcommand.html')


# endpoint for a device - the url it hits to get it's next command
@app.route('/getcommand/<device>')
def getcommand(device):
    # TODO: add logic that will send responses based on info in DB
    # This line gets all uncompleted actions for the specified device
    command = DeviceAction.query.filter_by(device=device, complete=False).first()
    formated_string = str(command.action) + ' ' + str(command.id)
    print formated_string
    number = random.randint(0, 1)
    return str(number)


@app.route('/completetask/device=<device>&task=<taskid>')
def completetask(taskid, device):
    try:
        device_action = DeviceAction.query.get(taskid)
        if device_action.device == device:
            device_action.complete = True
            db.session.commit()
            return '1'
        else:
            return '0'
    except Exception as e:
        print e
        return '0'


@app.route('/sendtemp/device=<device>&temp=<temp>')
def sendtemp(device, temp):
    try:
        device = DeviceStatus.query.get(device)
        device.temp = float(temp)
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
