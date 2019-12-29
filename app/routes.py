from flask import render_template, jsonify
from app import app
import time
# TODO: remove comments when merging
# import wiringpi

# Wiring pi setup
# TODO: remove comments when merging
# wiringpi.wiringPiSetup()

# wiringpi.pinMode(4, 1)

@app.route('/')
def index():
	return render_template('home.html', title = 'Home')

@app.route('/login/')
def login():
	return render_template('login.html', title = 'Login')

@app.route('/registration/')
def registration():
	return render_template('registration.html', title = 'Registration')

@app.route('/open-door/')
def api():
	print('API request received')
	open_door()
	return jsonify(result='success')


def open_door():
	# TODO: remove comments when merging
	# wiringpi.digitalWrite(5, 1)
	# time.sleep(500)
	# wiringpi.digitalWrite(5, 0)
	return True


# If we're running this script directly, this portion executes. The Flask
#  instance runs with the given parameters. Note that the "host=0.0.0.0" part
#  is essential to telling the system that we want the app visible to the 
#  outside world.
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)