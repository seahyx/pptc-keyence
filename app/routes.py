from flask import render_template, jsonify, flash, redirect, url_for, request, session, send_from_directory
from flask_login import current_user, login_user, logout_user, login_required
from flask_socketio import emit, disconnect
from app import app, db, socketio, tcpclient, plc_ser, barcode_ser, configfile, csvreader
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
	ERRORCODE	= 0
	class RACK_TYPE:
		TUBE   = 1
		TROUGH = 2

class Cartridge:
	NAMESPACE   = '/cartridge/api'
	WORK_ORDER  = 'cartridge_work_order'
	PART_NUMBER = 'cartridge_part_number'
	INSTRUMENT  = 'cartridge_instrument'
	RACK_ID     = 'cartridge_rack_id'
	DATA        = 'cartridge_data'
	ERRORCODE	= 0


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
	laser_instruments = configfile.laser_etch_QC['Instrument']

	# Minimum length for part number and work order
	part_number_min_len = configfile.laser_etch_QC['PNLength']
	work_order_len = configfile.laser_etch_QC['WOLength']

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
	rack_type   = session.get(Laser.RACK_TYPE)
	instrument  = session.get(Laser.INSTRUMENT)
	data        = session.get(Laser.DATA)
	errorcode  	= session.get(Laser.ERRORCODE)

	# rack_type   = Laser.RACK_TYPE.TUBE

	if not work_order or not part_number or not rack_id or not data:
		app.logger.warning(f'Insufficient data received, redirecting back to laser page, work_order: {work_order}, part_number: {part_number}, rack_id: {rack_id}, instrument: {instrument}, data: {data}')
		return(redirect(url_for('laser')))
	
	if not rack_type:
		rack_type = 0

	return render_template(
		'laser-process.html',
		title            = 'Laser Etch QC - Processing',
		work_order       = work_order,
		part_number      = part_number,
		rack_id          = rack_id,
		laser_instrument = instrument,
		data             = data,
		rack_type        = rack_type,
		errorcode        = errorcode
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


# Image loader - uses codename
@app.route('/img/<int:cam>/<string:image>')
def load_image(cam, image):

	# Get the associated filename from the config
	filename = configfile.VISION_IMAGE[f'CAM{cam}'][image.upper()]

	app.logger.info(f'Filename selected: {filename}')
	app.logger.info(f'Vision Image Dir: {configfile.VISION_IMAGE_DIR}')

	return send_from_directory('.\\test\\xg\\hist', filename, as_attachment=True)


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

	errorcode = 0 # Default no error

	# Save variables
	session[Laser.WORK_ORDER] = work_order
	session[Laser.PART_NUMBER] = part_number
	session[Laser.INSTRUMENT] = laser_instrument

	mask, racktype = csvreader.search(part_number)
	if (mask == None):
		print ('Invalid Part Number')
		errorcode = 1
	else:
		if (racktype == 'Tube'):
			session[Laser.RACK_TYPE] = Laser.RACK_TYPE.TUBE
			tcpclient.send('PW,1,3')
		else:
			session[Laser.RACK_TYPE] = Laser.RACK_TYPE.TROUGH
			tcpclient.send('PW,1,2')

	plc_ser.send_data("G2")
	time.sleep(0.1)
	plc_ser.send_data("R")
	time.sleep(0.1)
	plc_ser.purge()
	plc_ser.send_data("S")
	start = timer()
	
	while True:
		if plc_ser.data_ready:
			sdata = plc_ser.get()
			if sdata[:2] == "G2": # Reach the scan location
				break
		else:
			end = timer()
			if end - start > 7.0:
				app.logger.warning('Timeout, going to scan position')
				break
			else:
				time.sleep(0.1)

	# Get Rack ID
	barcode_ser.purge()
	barcode_ser.send_data("LON")
	start = timer()

	sdata = None
	
	while True:
		if barcode_ser.data_ready:
			sdata = barcode_ser.get()
			break
		else:
			end = timer()
			if end - start > 3.0:
				app.logger.warning('Timeout getting barcode')
				break
			else:
				time.sleep(0.1)
	
	# TODO: Handle sdata error

	if sdata:
		session[Laser.RACK_ID] = sdata[:-2]
		app.logger.info('Laser Etch QC received ' + session[Laser.RACK_ID])
		if (sdata[:5] == 'ERROR'):
			app.logger.warn('Can not read 1D barcode')
			errorcode = 2
		else:
			if (sdata[:2] not in configfile.laser_etch_QC['Prefix']):
				errorcode = 3
				app.logger.warn('Invalid Rack ID')
	else:
		errorcode = -1

	app.logger.warn(errorcode)

	if (errorcode == 0):
		# Get barcodes
		data = tcpclient.send('T1')
		session[Laser.DATA] = data

		app.logger.info('Redirecting page to laser_process')
	else:
		session[Laser.DATA] = 'T1,1,,1,,1,,1,,1,,1,,1,,1,,1,,1,,1,,1,,1,,1,,1,,1,,1,,1,,1,,1,,1,,1,,1,,1,,1,'

	session[Laser.ERRORCODE] = errorcode
	plc_ser.send_data('GB')
	emit('redirect', url_for('laser_process'))

@socketio.on('process-loaded', namespace=Laser.NAMESPACE)
def laser_process_init():
	data = session.get(Laser.DATA)
	emit('process-init', data)