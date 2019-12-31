from flask import render_template, jsonify, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from app import app, db
from app.forms import LoginForm, RegistrationForm, ChangePasswordForm
from app.models import User
from app.permissions import PermissionsManager
from app.gate import GateManager
from werkzeug.urls import url_parse
import time

gate = GateManager()

permissions = PermissionsManager()
permissions.redirect_view = 'index'


@app.route('/')
@app.route('/home/')
@login_required
def index():
	return render_template('home.html', title='Home')


@app.route('/login/', methods=['GET', 'POST'])
def login():
	
	# If user is logged in and navigates to this page somehow
	if current_user.is_authenticated:
		# Redirect back to home page
		return redirect(url_for('index'))

	form = LoginForm()

	if form.validate_on_submit():

		# Find a user by username from the User db table
		user = User.query.filter_by(username=form.username.data).first()

		if user is None or not user.check_password(form.password.data):
			# Wrong username or password
			flash('Invalid username or password')
			return redirect(url_for('login'))

		# Correct username and password
		flash('Logged in successfully')
		login_user(user, remember=form.rmb_me.data)

		next_page = request.args.get('next')
		# Netloc tests if next is pointed towards other site, which can link to malicious sites. Thus not accepting the redirect if it has value.
		if not next_page or url_parse(next_page).netloc != '':
			next_page = url_for('index')

		return redirect(next_page)
	
	return render_template('login.html', title='Login', form=form)


@app.route('/logout/')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/registration/', methods=['GET', 'POST'])
@login_required
@permissions.admin_required
def registration():

	form = RegistrationForm()

	if form.validate_on_submit():
		user = User(username=form.username.data, account_type=form.account_type.data)
		user.set_password(form.password.data)
		db.session.add(user)
		db.session.commit()
		flash('{} {} has been created'.format(user.get_account_type_name(), user.username))

		next_page = request.args.get('next')
		# Netloc tests if next is pointed towards other site, which can link to malicious sites. Thus not accepting the redirect if it has value.
		if not next_page or url_parse(next_page).netloc != '':
			next_page = url_for('index')

		return redirect(next_page)

	return render_template('registration.html', title='Create new account', form=form)


@app.route('/dashboard/')
@login_required
@permissions.admin_required
def dashboard():
	if request.args.get('rmId') and request.args.get('rmId').isdigit():
		removal_id = int(request.args.get('rmId'))
		print('Dashboard: Account of list id {} requested'.format(removal_id))
		
		# Now check if the number is valid and that the user is safe to delete
		user = User.query.filter_by(id=removal_id).first()
		if (user):
			# The user exists
			if ((user.id != current_user.id) and user.account_type != 0):
				# The user is not the currently logged in user or root, thus can be safely deleted
				db.session.delete(user)
				db.session.commit()
				print('Success: User with username {}, id of {} is deleted'.format(user.username, removal_id))
				flash('Success: User with username {}, id of {} is deleted'.format(user.username, removal_id))
			else:
				# The user is root or current user, thus cannot be removed
				print('Error: User with username {}, id of {} cannot be deleted'.format(user.username, removal_id))
				flash('Error: User with username {}, id of {} cannot be deleted'.format(user.username, removal_id))
		else:
			# The user doesn't exist
			print('Error: User with id of {} does not exist'.format(removal_id))
			flash('Error: User with id of {} does not exist'.format(removal_id))

	return render_template('dashboard.html', title='Admin Dashboard', users=User.query.order_by(User.account_type).order_by(User.username).all())


@app.route('/dashboard/change-pass/<username>/', methods=['GET', 'POST'])
@login_required
@permissions.admin_required
def change_pass(username):
	user = User.query.filter_by(username=username).first_or_404()

	form = ChangePasswordForm()

	if form.validate_on_submit():
		user.set_password(form.password.data)
		db.session.commit()
		flash('Success: Password for {} {} has been changed'.format(user.get_account_type_name(), user.username))
		return(redirect(url_for('dashboard')))
	
	return(render_template('change-pass.html', title='Change password', form=form, user=user))

	return


@app.route('/open-door/')
@login_required
def api():
	print('Open door request received, gateFree = {}'.format(gate.gate_free()))

	isForced = request.args.get('forced');

	print(isForced)

	if not gate.gate_free() and not isForced == 'true':
		print('Gate is currently in operation, please wait {} second(s)'.format(gate.gate_time_left_to_free()))
		return jsonify(message='fail', time_left=gate.gate_time_left_to_free())
	
	if request.args.get('args') and request.args.get('args').isdigit():
		# If there another button pressed
		args = int(request.args.get('args'))
		gate.open_gate(args)
		return jsonify(message='success')
	else:
		return jsonify(message='none')
	

#  If we're running this script directly, this portion executes. The Flask
#  instance runs with the given parameters. Note that the "host=0.0.0.0" part
#  is essential to telling the system that we want the app visible to the 
#  outside world.
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)