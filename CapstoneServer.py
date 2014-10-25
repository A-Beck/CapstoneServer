from flask import Flask, render_template, request, redirect
from flask.ext.sqlalchemy import SQLAlchemy
import time

# setup environment stuff
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///capstone.db'
db = SQLAlchemy(app)

# TODO: Create a table that holds user credentials
# TODO: create a table that relates users to devices


# This is a class that relates devices to actions they have to perform
class DeviceAction(db.Model):
    __tablename__ = 'device_action'
    id = db.Column(db.Integer, primary_key=True)
    device = db.Column(db.Text, unique=False)
    action = db.Column(db.Text, unique=False)
    time = db.Column(db.Integer)
    complete = db.Column(db.Boolean, unique=False)

    def __init__(self, device, action):
        self.device = device
        self.action = action
        self.complete = False
        self.time = time.time()


#the homepage for our app
@app.route('/')
def index():
    return render_template('index.html')


#TODO: create route that will allow log in
@app.route('/login', methods=['POST'])
def login():
    pass


#TODO: create route that will allow registration
@app.route('/register', methods=['POST'])
def register():
    pass


#view actions that have been submitted
@app.route('/actions')
def actions():
    all_actions = DeviceAction.query.all()
    return render_template('actions.html', actions=all_actions)


# endpoint for a device - the url it hits to get it's next command
@app.route('/getcommand')
def getcommand():
    # TODO: add logic that will send responses based on info in DB
    return 1


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
@app.route('/completetask', methods=['POST'])
def completetask():
    pass


# TODO: add route that will allow mC to post temp data
@app.route('/sendtemp', methods=['POST'])
def sendtemp():
    pass
    




app.debug = True

if __name__ == '__main__':
    app.run()
