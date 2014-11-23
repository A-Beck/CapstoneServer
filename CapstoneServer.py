from flask import Flask, render_template, request, redirect, url_for
from models import User, UserDevices, DeviceStatus, DeviceAction, DeviceSettings, Codes, db
from flask.ext.login import LoginManager, login_required, login_user, logout_user, current_user
import random


# TODO: Error Checking for all user generated values
# TODO: Error Checking for DB accesses
# TODO: Better return codes to send to msp
# TODO: Better user exp on site


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///capstone.db'
app.secret_key = 'Super Secret'
db.app = app
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)


# required to use flask-login package
@login_manager.user_loader
def user_loader(user_id):
    return User.query.get(user_id)


# The landing page for our app
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/login', methods=['POST'])
def login():
    """ Login a user """
    email = request.form['email']
    password = request.form['password']
    # get username and password
    user = User.query.filter_by(email=email).first()
    if user is None:  # check if the user exists
        return 'login fail'
    if user.check_password(password):  # if the user exists, check credentials
        user.authenticated = True
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect('/profile')
    else:
        return 'login fail'


# logs a user out and redirects them to the homepage
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


# TODO: Error checking
@app.route('/register', methods=['POST'])
def register():
    email = request.form['email']
    password = request.form['password']
    user_list = User.query.filter_by(email=email).all()
    if len(user_list) > 0:
        return redirect('/')
    else:
        user = User(email, password, True)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect('/profile')


# A user's home page
@app.route('/profile')
@login_required
def profile():
    user = current_user
    user_devices = UserDevices.query.filter_by(email=user.email).all()
    devices = []
    for item in user_devices:
        device_status = DeviceStatus.query.get(item.device_id)
        devices.append({'Name': item.device, 'Temp': device_status.temp, 'Humidity': device_status.humidity})
    return render_template('profile.html', user=user, devices_statuses=devices)


# view actions that have been submitted
@app.route('/actions')
@login_required
def actions():
    user = current_user
    user_devices = UserDevices.query.filter_by(email=user.email).all()
    all_actions = []
    all_possible_actions = set()
    for user_device in user_devices:
        device_id = user_device.device_id
        device_actions = DeviceAction.query.filter_by(device_id=device_id).all()
        for d_a in device_actions:
            if (d_a.complete == False):
                all_actions.append({'Name': user_device.device, 'Action': d_a.action, 'Action id': d_a.action_id,
                                    'Device_id': device_id, 'Complete': d_a.complete})
        available_actions = get_available_actions(user_device.device_type)
        for action in available_actions:
            all_possible_actions.add((action, user_device.device_type))

    return render_template('actions.html', actions=all_actions, user_devices=user_devices,
                           possible_actions=list(all_possible_actions))


@app.route('/devices')
@login_required
def devices():
    user = current_user
    users_devices = UserDevices.query.filter_by(email=user.email).all()
    device_list = []
    for device in users_devices:
        settings = DeviceSettings.query.get(device.device_id)
        device_list.append({'Name': device.device, 'id': device.device_id, 'Man': device.manufacturer,
                            'Type': device.device_type, 'Upper Temp': settings.upper_temp,
                            'Lower Temp': settings.lower_temp})
    return render_template('devices.html', device_list=device_list)


#adding a command to a device's command queue
@app.route('/addcommand', methods=['POST'])
@login_required
def addcommand():
    if request.method == 'POST':

        user = current_user
        device = request.form['device']
        action = request.form['action']

        #extra junk comes in with the form, clean it up
        def cleanup(input_str):
            ret = ''
            for c in input_str:
                if c == '(':
                    break
                ret += c
            return ret.strip(' ')
        device = cleanup(device)
        action = cleanup(action)

        device = UserDevices.query.filter_by(device=device, email=user.email).first()
        if device is not None:  # ensure such a device exists and belongs to the user
            code = Codes.query.filter_by(device_type=device.device_type, action=action).first()
            if code is not None:  # ensure it is a valid command to add
                db.session.add(DeviceAction(device.device_id, action))
                db.session.commit()
        return redirect('/actions')


@app.route('/removecommand', methods=['POST'])
@login_required
def removecommand():
    if request.method == 'POST':
        id = request.form['id']
        action = DeviceAction.query.get(id)
        if action is not None:
            db.session.delete(action)
            db.session.commit()
    return redirect('/actions')


@app.route('/adddevice', methods=['POST'])
@login_required
def adddevice():
    print 'entered fn'
    user = current_user
    device = request.form['device']
    device_id = int(request.form['device_id'])
    man = request.form['man']
    device_type = request.form['type']
    print 'read data'
    # Check to see if there any devices under the same name
    possible_devices = UserDevices.query.filter_by(device=device, email=user.email).all()
    device_with_same_id = UserDevices.query.get(device_id)
    # Do not allow duplicate names for same user, unique id's
    print 'checked registry'
    if len(possible_devices) == 0 and device_with_same_id is None:
        # Relate user to device
        user_device = UserDevices(device_id, user.email, device, man, device_type)
        db.session.add(user_device)
        db.session.commit()
        # Update the status for the device
        db.session.add(DeviceStatus(user_device.device_id))
        db.session.add(DeviceSettings(user_device.device_id))
        db.session.commit()

    return redirect('/profile')


@app.route('/changesettings', methods=['POST'])
@login_required
def change_settings():
    device_id = int(request.form['id'])
    if request.form['type'] == 'get':
        settings = DeviceSettings.query.get(device_id)
        return render_template('changesettings.html', settings=settings)
    else:
        device_settings = DeviceSettings.query.get(device_id)
        upper_limit = float(request.form['Upper_limit'])
        lower_limit = float(request.form['Lower_limit'])
        device_settings.update(higher_limit=upper_limit, lower_limit=lower_limit)
        db.session.commit()
    return redirect('/profile')



@app.route('/removedevice', methods=['POST'])
@login_required
def remove_device():
    device_id = int(request.form['id'])
    device_status = DeviceStatus.query.get(device_id)
    device_settings = DeviceSettings.query.get(device_id)
    device_actions = DeviceAction.query.filter_by(device_id=device_id).all()
    db.session.delete(device_settings)
    db.session.delete(device_status)
    for action in device_actions:
        db.session.delete(action)
    users_device = UserDevices.query.get(device_id)
    db.session.delete(users_device)
    db.session.commit()
    return redirect('/profile')


# the url it hits to get it's next command
@app.route('/getcommand/<device_id>')
def getcommand(device_id):
    command = DeviceAction.query.filter_by(device_id=device_id, complete=False).first()
    device = UserDevices.query.get(device_id)
    code = Codes.query.filter_by(manufacturer=device.manufacturer, device_type=device.device_type,
                                 action=command.action).first()
    print code
    if code is not None and command is not None:
        num_elements = get_pulse_numbers(code.code)
        formated_string = str(command.action_id) + '-' + str(num_elements) + '-' + code.code + '|'
        print formated_string
        return formated_string
    else:
      return str(0)


@app.route('/completetask/device=<device_id>&task=<taskid>')
def completetask(taskid, device_id):
    try:
        device_action = DeviceAction.query.get(taskid)
        device_action.complete = True
        db.session.commit()
        return '1'
    except Exception as e:
        print e
        return '0'


@app.route('/sendtemp/device=<device_id>&temp=<temp>')
def sendtemp(device_id, temp):
    try:
        device = DeviceStatus.query.get(device_id=device_id)
        device.update(temp=temp)
        db.session.commit()
        return '1'
    except Exception as e:
        print e
        return '0'


@app.route('/test')
def test():
    return redirect(url_for('static', filename='test.xml'))


### For a particular device type, get all possible actions
def get_available_actions(device_type):
    codes = Codes.query.filter_by(device_type=device_type)
    possible_actions = []
    for code in codes:
        action = code.action
        possible_actions.append(action)
    return possible_actions


### return the code in MSP readable formatting
def get_pulse_numbers(code):
    comma_count = 1  # first pulse is not preceeded by a comma
    for c in code:
        if c == ',':
            comma_count += 1
    return comma_count


app.debug = True


if __name__ == '__main__':
    db.create_all()
    app.run()
