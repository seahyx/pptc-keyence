from flask import render_template, jsonify, flash, redirect, url_for
from app import app
from app.forms import LoginForm
from flask_login import current_user, login_user
from app.models import User
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

@app.route('/login/', methods = ['GET', 'POST'])
def login():

	# If user is logged in and navigates to this page somehow
	if current_user.is_authenticated:
		# Redirect back to home page
		return redirect(url_for('index'))

	form = LoginForm()

	if form.validate_on_submit():

		# Find a user by username from the User db table
		user = User.query.filter_by(username = form.username.data).first()

		if user is None or not user.check_password(form.password.data):
			# Wrong username or password
			flash('Invalid username or password')
			return redirect(url_for('login'))

		# Correct username and password
		flash('Logged in successfully')
		login_user(user, remember = form.rmb_me.data)

		return redirect(url_for('index'))
	
	return render_template('login.html', title = 'Login', form = form)

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