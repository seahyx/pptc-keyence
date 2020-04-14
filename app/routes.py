from flask import render_template, jsonify, flash, redirect, url_for, request, session
from flask_login import current_user, login_user, logout_user, login_required
from flask_socketio import emit, disconnect
from app import app, db, socketio, tcpclient, plc_ser, configfile
from app.forms import LoginForm, RegistrationForm, ChangePasswordForm
from app.models import User
from app.permissions import PermissionsManager
from werkzeug.urls import url_parse
from timeit import default_timer as timer
from functools import wraps
import time


# Consts
class Laser:
	NAMESPACE   = '/laser/api'
	WORK_ORDER  = 'laser_work_order'
	PART_NUMBER = 'laser_part_number'
	INSTRUMENT  = 'laser_instrument'
	RACK_ID     = 'laser_rack_id'
	DATA        = 'laser_data'


class Cartridge:
	NAMESPACE   = '/cartridge/api'
	WORK_ORDER  = 'cartridge_work_order'
	PART_NUMBER = 'cartridge_part_number'
	INSTRUMENT  = 'cartridge_instrument'
	RACK_ID     = 'cartridge_rack_id'
	DATA        = 'cartridge_data'


permissions = PermissionsManager()
permissions.redirect_view = 'index'

# Context processor runs and adds global values
# for the template before any page is rendered
@app.context_processor
def inject_dict():
	return dict(
		program_name='2D Barcode System',
		cart_prog_name='Cartridge Assembly QC',
		laser_prog_name='Laser Etch QC')


@app.route('/')
@app.route('/home/')
@login_required
def index():
	app.logger.info('Loading index page...')
	return render_template('home.html', title='Home')


@app.route('/login/', methods=['GET', 'POST'])
def login():

	# If user is logged in and navigates to this page somehow
	if current_user.is_authenticated:
		# Redirect back to home page
		app.logger.info('User is already logged in, redirecting to index page...')
		return redirect(url_for('index'))

	form = LoginForm()

	if form.validate_on_submit():

		app.logger.info('Logging in user...')

		# Find a user by username from the User db table
		user = User.query.filter_by(username=form.username.data).first()

		if user:
			if not user.check_password(form.password.data):
				# Wrong password
				app.logger.info('Log in failed: Wrong password')
				return redirect(url_for('login'))
		else:
			# Wrong username
			app.logger.info('Log in failed: Wrong username')
			return redirect(url_for('login'))

		# Correct username and password
		flash('Logged in successfully')
		app.logger.info(f'Logged in successfully with username {user.username}')
		login_user(user, remember=form.rmb_me.data)

		next_page = request.args.get('next')
		# Netloc tests if next is pointed towards other site, which can link to malicious sites. Thus not accepting the redirect if it has value.
		if not next_page or url_parse(next_page).netloc != '':
			app.logger.info('Redirecting to index page...')
			next_page = url_for('index')

		app.logger.info(f'Redirecting to {next_page} page...')
		return redirect(next_page)

	app.logger.info('Loading login page...')
	return render_template('login.html', title='Login', form=form, no_header=True)


@app.route('/logout/')
def logout():
	app.logger.info('Logging out user')
	logout_user()
	app.logger.info('User logged out')
	app.logger.info('Redirecting to login page...')
	return redirect(url_for('login'))


@app.route('/cartridge/')
@login_required
def cartridge():
	app.logger.info('Loading cartridge page...')
	tcpclient.send('PW,1,1')
	return render_template('cartridge.html', title='Cartridge Assembly QC')


@app.route('/laser/')
@login_required
def laser():
	app.logger.info('Loading laser page...')

	# Default laser instruments available
	laser_instruments = configfile.laserEtchQC['Instrument']

	# Minimum length for part number
	part_number_min_len = 8

	return render_template(
		'laser.html',
		title='Laser Etch QC',
		instruments=laser_instruments,
		part_number_min_len=part_number_min_len)

@app.route('/laser/process/')
@login_required
def laser_process():
	app.logger.info('Loading laser-process page...')

	work_order  = session.get(Laser.WORK_ORDER)
	part_number = session.get(Laser.PART_NUMBER)
	rack_id     = session.get(Laser.RACK_ID)
	instrument  = session.get(Laser.INSTRUMENT)
	data        = session.get(Laser.DATA)

	if not work_order or not part_number or not rack_id or not data:
		app.logger.warning(f'Insufficient data received, redirecting back to laser page, work_order: {work_order}, part_number: {part_number}, rack_id: {rack_id}, instrument: {instrument}, data: {data}')
		return(redirect(url_for('laser')))

	return render_template(
		'laser-process.html',
		title            = 'Laser Etch QC - Processing',
		work_order       = work_order,
		part_number      = part_number,
		rack_id          = rack_id,
		laser_instrument = instrument,
		data             = data
		)

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
		app.logger.info(f'New user <{user.get_account_type_name()}> with username {user.username} and account_type {user.account_type} created')
		flash('{} {} has been created'.format(user.get_account_type_name(), user.username))

		next_page = request.args.get('next')
		# Netloc tests if next is pointed towards other site, which can link to malicious sites. Thus not accepting the redirect if it has value.
		if not next_page or url_parse(next_page).netloc != '':
			next_page = url_for('index')

		app.logger.info(f'Redirecting to {next_page} page...')
		return redirect(next_page)

	app.logger.info('Loading registration page...')
	return render_template('registration.html', title='Create new account', form=form)


@app.route('/dashboard/')
@login_required
@permissions.admin_required
def dashboard():
	if request.args.get('rmId') and request.args.get('rmId').isdigit():
		removal_id = int(request.args.get('rmId'))
		app.logger.info(f'Account removal of list id {removal_id} requested')

		# Now check if the number is valid and that the user is safe to delete
		user = User.query.filter_by(id=removal_id).first()
		if (user):
			# The user exists
			if ((user.id != current_user.id) and user.account_type != 0):
				# The user is not the currently logged in user or root, thus can be safely deleted
				db.session.delete(user)
				db.session.commit()
				app.logger.info(f'User with username {user.username}, list id of {removal_id} is successfully deleted')
				flash(f'User with username {user.username}, list id of {removal_id} is successfully deleted')
			else:
				# The user is root or current user, thus cannot be removed
				app.logger.info(f'User with username {user.username}, list id of {removal_id} cannot be deleted')
				flash(f'User with username {user.username}, list id of {removal_id} cannot be deleted')
		else:
			# The user doesn't exist
			app.logger.info(f'User with list id of {removal_id} does not exist')
			flash(f'User with list id of {removal_id} does not exist')

	app.logger.info('Loading dashboard page...')
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
		
		app.logger.info(f'Password for user {user.username} has been successfully changed')
		flash(f'Password for user {user.username} has been successfully changed')
		
		app.logger.info('Redirecting to dashboard page...')
		return(redirect(url_for('dashboard')))

	app.logger.info('Loading change password page...')
	return(render_template('change-pass.html', title='Change password', form=form, user=user))


# SocketIO login checker

def authenticated_only(f):
	@wraps(f)
	def wrapped(*args, **kwargs):
		if not current_user.is_authenticated:
			disconnect()
		else:
			return f(*args, **kwargs)
	return wrapped

# SocketIO interfaces

# Laser Etch QC

@socketio.on('connect', namespace=Laser.NAMESPACE)
def laser_connect():
	app.logger.info('Connected to Laser Etch QC client interface')
	emit('response', 'Connected to Laser Etch QC api')

@socketio.on('disconnect', namespace=Laser.NAMESPACE)
def laser_disconnect():
	app.logger.info('Disconnected from Laser Etch QC client interface')

@socketio.on('start', namespace=Laser.NAMESPACE)
def laser_start(work_order, part_number):
	app.logger.info(f'Laser Etch QC start, work order: {work_order}, part number: {part_number}')
	# TODO: Validate work order/part number

@socketio.on('confirm', namespace=Laser.NAMESPACE)
def laser_confirm(work_order, part_number, laser_instrument):
	app.logger.info(f'Laser Etch QC confirm, work order: {work_order}, part number: {part_number}, laser instrument: {laser_instrument}')

	# Save variables
	session[Laser.WORK_ORDER] = work_order
	session[Laser.PART_NUMBER] = part_number
	session[Laser.INSTRUMENT] = laser_instrument

	plc_ser.send_data("R")
	time.sleep(0.1)
	plc_ser.send_data("S")
	start = timer()
	
	while True:
		if plc_ser.data_ready:
			sdata = plc_ser.get()
			if sdata[:2] == "G2": # Reach the scan location
				break
		else:
			end = timer()
			if end - start > 2.0:
				app.logger.warning('Timeout, going to scan position')
				break
			else:
				time.sleep(0.1)

	# Get Rack ID
	sdata = 'MSG - 433 - SG' # for testing. To be replaced
	session[Laser.RACK_ID] = sdata
	app.logger.info('Laser Etch QC received ' + sdata)

	# Get barcodes
	tcpclient.send('PW,1,3')
	data = tcpclient.send('T1')
	session[Laser.DATA] = data

	app.logger.info('Redirecting page to laser_process')

	emit('redirect', url_for('laser_process'))

@socketio.on('process-loaded', namespace=Laser.NAMESPACE)
def laser_process_init():
	data = session.get(Laser.DATA)
	emit('process-init', data)