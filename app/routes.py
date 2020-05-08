from flask import render_template, jsonify, flash, redirect, url_for, request, session, send_from_directory
from flask_login import current_user, login_user, logout_user, login_required
from flask_socketio import emit, disconnect
from app import app, db, socketio, tcpclient, plc_ser, barcode_ser, configfile, csvreader
from app.forms import LoginForm, RegistrationForm, ChangePasswordForm
from app.models import User
from app.permissions import PermissionsManager
from logfile import Log_file, Audit_trail
from fileutil import Path_Util
from werkzeug.urls import url_parse
from time import sleep, time as current_time
from timeit import default_timer as timer
from datetime import datetime
import glob
import os

# Consts
class Laser:
	NAMESPACE   = '/laser/api'
	WORK_ORDER  = 'laser_work_order'
	PART_NUMBER = 'laser_part_number'
	INSTRUMENT  = 'laser_instrument'
	RACK_ID     = 'laser_rack_id'
	DATA        = 'laser_data'
	MASK		= 'mask'
	ERRORCODE	= 0
	class RACK_TYPE:
		TUBE   = 1
		TROUGH = 2
	class ITEM_QTY:
		TUBE	= 24
		TROUGH	= 4

class Cartridge:
	NAMESPACE   = '/cartridge/api'
	CARTRIDGE_ID     = 'cartridge_id'
	WORK_ORDER  = 'cartridge_work_order'
	DATA        = 'cartridge_data'
	ITEM_QTY	= 21
	ERRORCODE	= 0


permissions = PermissionsManager()
permissions.redirect_view = 'index'
app.start_pressed = False
app.use_flask_serial = True
app.nspace = ''

# move files from vision image dir to respective dir
def move_image_files (destdir, subfolder):
	filenames = os.listdir(configfile.VISION_IMAGE_DIR)
	finaldest = Path_Util(destdir).mkdir(subfolder)
	s = Path_Util(configfile.VISION_IMAGE_DIR)
	app.logger.info(f'Move images from {configfile.VISION_IMAGE_DIR} to {finaldest}')
	for filename in filenames:
		s.move(filename, finaldest)

def get_folder_count(folder):
	dest = configfile.cartridge_assembly_QC['ImageDir']+'/'+folder+'*'
	return (len(glob.glob(dest)))

def get_subfolder(subfolder):
	folder_count = get_folder_count(subfolder)
	if (folder_count == 0):
		return subfolder
	else:
		return (subfolder+'_'+str(folder_count))


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
				Audit_trail.write_file(configfile.AUDIT_TRAIL_DIR, user.username, 'Invalid user/password')
				session['USERNAME'] = ''
				app.logger.info('Log in failed: Wrong password')
				return redirect(url_for('login'))
		else:
			# Wrong username
			app.logger.info('Log in failed: Wrong username')
			Audit_trail.write_file(configfile.AUDIT_TRAIL_DIR, user.username, 'Invalid user/password')
			session['USERNAME'] = ''
			return redirect(url_for('login'))

		# Correct username and password
		flash('Logged in successfully')
		app.logger.info(f'Logged in successfully with username {user.username}')
		session['USERNAME'] = user.username
		Audit_trail.write_file(configfile.AUDIT_TRAIL_DIR, user.username, 'Login successful')
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
	Audit_trail.write_file(configfile.AUDIT_TRAIL_DIR, session['USERNAME'], 'Logged out')
	app.logger.info('Redirecting to login page...')
	return redirect(url_for('login'))


@app.route('/cartridge/')
@login_required
def cartridge():
	app.logger.info('Loading cartridge page...')
	tcpclient.send('PW,1,1')
	return render_template('cartridge.html', title='Cartridge Assembly QC')

@app.route('/cartridge/process/')
@login_required
def cartridge_process():
	Audit_trail.write_file(configfile.AUDIT_TRAIL_DIR, session['USERNAME'], 'Access Cartridge Assembly QC')
	app.logger.info('Loading cartridge-process page...')

	cartridge_id = session.get(Cartridge.CARTRIDGE_ID)
	data         = session.get(Cartridge.DATA)
	errno        = session.get(Cartridge.ERRORCODE)

	#if not cartridge_id or not data:
	#	app.logger.warning(f'Insufficient data received, redirecting back to cartridge page, cartridge_id: {cartridge_id}, data: {data}')
		# Need to log the info
	#	return(redirect(url_for('cartridge')))

	return render_template(
		'cartridge-process.html',
		title        = 'Cartridge Assembly QC - Processing',
		cartridge_id = cartridge_id,
		data         = data,
		errno        = errno,
		done_url     = url_for('cartridge'),
		)


@app.route('/laser/')
@login_required
def laser():
	app.logger.info('Loading laser page...')

	# Default laser instruments available
	laser_instruments = configfile.laser_etch_QC['Instrument']

	# Minimum length for part number and work order
	part_number_len = configfile.laser_etch_QC['PNLength']
	work_order_len = configfile.laser_etch_QC['WOLength']

	return render_template(
		'laser.html',
		title='Laser Etch QC',
		instruments=laser_instruments,
		work_order_len=work_order_len)

@app.route('/laser/process/')
@login_required
def laser_process():
	app.logger.info('Loading laser-process page...')
	Audit_trail.write_file(configfile.AUDIT_TRAIL_DIR, session['USERNAME'], 'Access Laser Etch QC')

	work_order  = session.get(Laser.WORK_ORDER)
	part_number = session.get(Laser.PART_NUMBER)
	rack_id     = session.get(Laser.RACK_ID)
	rack_type   = session.get(Laser.RACK_TYPE)
	instrument  = session.get(Laser.INSTRUMENT)
	data        = session.get(Laser.DATA)
	errno     	= session.get(Laser.ERRORCODE)

	if not work_order or not part_number or not rack_id or not data:
		app.logger.warning(f'Insufficient data received, redirecting back to laser page, work_order: {work_order}, part_number: {part_number}, rack_id: {rack_id}, instrument: {instrument}, data: {data}')
		return(redirect(url_for('laser')))
	
	if not rack_type:
		rack_type = -1

	return render_template(
		'laser-process.html',
		title            = 'Laser Etch QC - Processing',
		work_order       = work_order,
		part_number      = part_number,
		rack_id          = rack_id,
		laser_instrument = instrument,
		data             = data,
		rack_type        = rack_type,
		errno            = errno,
		done_url         = url_for('laser'),
		)

@app.route('/manual/test/')
@login_required
def manual_test():
	app.logger.info('Loading manual test page...')
	Audit_trail.write_file(configfile.AUDIT_TRAIL_DIR, session['USERNAME'], 'Access Manual Test')

	return render_template(
		'manual-test.html',
		title            = 'Manual Test',
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

	return send_from_directory(configfile.VISION_IMAGE_DIR, filename, as_attachment=True)


# SocketIO interfaces

#
# Home
#

@socketio.on('connect', namespace='/home/api')
def laser_connect():
	app.logger.info('Connected to Home client interface')
	plc_ser.on_send('H\r\n')
	emit('connect', 'Connected to Home api')

@socketio.on('disconnect', namespace='/home/api')
def laser_disconnect():
	app.logger.info('Disconnected from Home client interface')

@socketio.on('PLC-serial', namespace='/home/api')
def send_wait_serial(data):
	app.logger.info(f'Sending {data} to PLC')
	plc_ser.on_send(data+'\r\n')

#
#Cartridge Assembly QC
#

@socketio.on('connect', namespace=Cartridge.NAMESPACE)
def cartridge_connect():
	app.logger.info('Connected to Cartridge Assembly QC client interface')
	emit('connect', 'Connected to Cartridge Assembly QC api')
	
@socketio.on('disconnect', namespace=Cartridge.NAMESPACE)
def cartridge_disconnect():
	app.logger.info('Disconnected from Cartridge Assembly QC client interface')

@socketio.on('PLC-serial', namespace=Cartridge.NAMESPACE)
def send_wait_serial(data):
	app.logger.info(f'Sending {data} to PLC')
	plc_ser.on_send(data+'\r\n')


@socketio.on('scan-position', namespace=Cartridge.NAMESPACE)
def read_1dbarcodes():
	app.logger.info('Reading 1d barcode')
	# Get Rack ID
	barcode_ser.purge()
	barcode_ser.send_data("LON")

	errno = 0
	start = timer()
	while True:
		if barcode_ser.data_ready:
			tdata = barcode_ser.get().strip()
			if (',' in tdata):
				cartridge_id, work_order = tdata.split(',')
				if (get_folder_count(cartridge_id) >= configfile.cartridge_assembly_QC['Max Retry']):
					errno = -3
			else:
				cartridge_id = ''
				work_order = ''
				errno = -2

			break
		else:
			end = timer()
			if end - start > 2.0:
				app.logger.warn('Timeout getting barcode')
				cartridge_id = ''
				work_order = ''
				errno = -2
				break
			else:
				sleep(0.1)

	# TODO: Check whether it has exceeded max retry
	
	session[Cartridge.CARTRIDGE_ID] = cartridge_id
	session[Cartridge.WORK_ORDER] = work_order
	session[Cartridge.ERRORCODE] = errno

	if (errno == 0):
		plc_ser.on_send('G3\r\n')
		plc_ser.on_send('S\r\n')
		emit('get_cartridge_id', {'Cart_ID':cartridge_id, 'Error_No':errno})
	else:
		plc_ser.on_send('GB\r\n')
		session[Cartridge.DATA]=[]
		logdata = (cartridge_id, 'FAIL', work_order) +('', )*Cartridge.ITEM_QTY
		Log_file.write_file (configfile.cartridge_assembly_QC['LogFile'], logdata, 0)
		app.logger.info('Redirecting page to cartridge-process')
		emit('redirect', url_for('cartridge_process'))
		# Log error

@socketio.on('scan-position2', namespace=Cartridge.NAMESPACE)
def read_2dbarcodes():
	app.logger.info('Reading 2d barcode')

	# Get barcodes
	items = tcpclient.send('T1')
	items.pop(0)
	totalitem = int(len(items)/2)
	
	newdata = []
	cartridge_id = session[Cartridge.CARTRIDGE_ID]
	if ('-' in cartridge_id):
		a, section = cartridge_id.split('-')
		
		if (totalitem != Cartridge.ITEM_QTY):
			errno = -6
			session[Cartridge.DATA] = ['1', ''] * 23
			# data = b'T1,0,MS3092555-RMF,0,TG2003637-RMF,0,MS3007019-TMP,0,TG2003671-RMF,0,TG2003667-RMF,0,TG2003626-RMF,0,TG2003657-RMF,0,TG2003660-RMF,0,MS6754129-LMX2,0,TG2003642-RMF,0,MS2929572-AMS1,0,MS6999347-LMX1,0,MS6324325-NULL,0,MS5357075-PW1,0,MS3085936-LPM,0,MS3247197-HP11,0,MS6262931-NULL,0,MS5342413-PW1,0,TG2003635-RMF,0,TG2003630-RMF,0,MS3040982-HP12,0,TG2003661-RMF,0,MS6675922-LDR,0,TG2003640-RMF'
		
		else:
			sections = configfile.cartridge_assembly_QC_config.sections()
			app.logger.info(section)
			if (section not in sections): # Invalid rack id
				app.logger.warn('Invalid cartridge id: '+section)
				errno = -4
				for i in range (totalitem):
					newdata.append('1')
					newdata.append('')
					newdata.append(items[i*2+1])

				session[Cartridge.DATA] = newdata
			else:
				i=1
				masks = []
				for j in range (21):
					if (i==3):
						i = 4
					keyword = 'Position_'+str(i)
					masks.append(configfile.cartridge_assembly_QC_config.get(section, keyword))
					i += 1

				for i in range(totalitem):
					if (items[i*2] == '0'): #success
						masklen = -len(masks[i])
						if (items[i*2+1][masklen:] == masks[i]):
							newdata.append('0')
							newdata.append(masks[i])
							newdata.append(items[i*2+1])
						else:
							newdata.append('1')
							newdata.append(masks[i])
							newdata.append(items[i*2+1])
							# app.logger.info(newdata)
							errno = -5
					else:
						newdata.append('1')
						newdata.append(masks[i])
						newdata.append(items[i*2+1])
						errno = -7
				app.logger.info(newdata)
				session[Cartridge.DATA] = newdata
	else: # Invalid cartridge id
		app.logger.info ('Invalid cartridge id: '+session[Cartridge.CARTRIDGE_ID])
		errno = -4
		for i in range(Cartridge.ITEM_QTY):
			newdata.append('1')
			newdata.append('') # mask
			newdata.append(items[i*2+1])
		session[Cartridge.DATA] = newdata

	# writing to log file
	if (errno == 0): # pass
		logdata = (cartridge_id, 'PASS', session[Cartridge.WORK_ORDER])
	else:
		logdata = (cartridge_id, 'FAIL', session[Cartridge.WORK_ORDER])

	tmpdata = session[Cartridge.DATA]
	for i in range (int(len(tmpdata)/3)):
		logdata = logdata +(tmpdata[i*3 + 2], )

	Log_file.write_file (configfile.cartridge_assembly_QC['LogFile'], logdata, 0)
	session[Cartridge.ERRORCODE] = errno
	app.logger.info("Go to home position")
	plc_ser.on_send('GB\r\n')
	app.logger.info('Redirecting page to cartridge-process')
	emit('redirect', url_for('cartridge_process'))

@socketio.on('move_images', namespace=Cartridge.NAMESPACE)
def cartridge_move_images():
	app.logger.info('Move vision images')
	subfolder = get_subfolder(session[Cartridge.CARTRIDGE_ID])
	move_image_files(configfile.cartridge_assembly_QC['ImageDir'], subfolder)

#
# Laser Etch QC
#

@socketio.on('connect', namespace=Laser.NAMESPACE)
def laser_connect():
	app.logger.info('Connected to Laser Etch QC client interface')
	app.start_pressed = False
	emit('connect', 'Connected to Laser Etch QC api')

@socketio.on('disconnect', namespace=Laser.NAMESPACE)
def laser_disconnect():
	app.logger.info('Disconnected from Laser Etch QC client interface')

@socketio.on('PLC-serial', namespace=Laser.NAMESPACE)
def send_wait_serial(data):
	app.logger.info(f'Sending {data} to PLC')
	if app.use_flask_serial:
		plc_ser.on_send(data+'\r\n')
	else:
		plc_ser.send_data(data)
		socketio.start_background_task(wait_for_start)

if not app.use_flask_serial:
	def wait_for_start():
		while (not app.start_pressed):
			if (plc_ser.data_ready):
				sdata = plc_ser.get()
				if (sdata[0] == 'R'):
					socketio.emit('plc-message', 'R', namespace=Laser.NAMESPACE)
					app.start_pressed = False
					break
			sleep(0.1)
		app.start_pressed = False

@socketio.on('start', namespace=Laser.NAMESPACE)
def laser_start(work_order, part_number):
	app.logger.info(f'Laser Etch QC start, work order: {work_order}, part number: {part_number}')
	if not app.use_flask_serial:
		app.start_pressed = True

	# TODO: Validate work order/part number
	mask, racktype = csvreader.search(part_number)
	if (mask == None):
		app.logger.error ('Invalid Part Number:'+part_number)
		logdata = (work_order, part_number, '', '',  'FALSE', '', '', 'FAIL')
		Log_file.write_file (configfile.laser_etch_QC['LogFile'], logdata, 1)
		emit('partnumber-result', 'N')
	else:
		if (racktype == 'Tube'):
			session[Laser.RACK_TYPE] = Laser.RACK_TYPE.TUBE
			tcpclient.send('PW,1,3')
		else:
			session[Laser.RACK_TYPE] = Laser.RACK_TYPE.TROUGH
			tcpclient.send('PW,1,2')

		session[Laser.WORK_ORDER] = work_order
		session[Laser.PART_NUMBER] = part_number
		session[Laser.MASK] = mask
		emit('partnumber-result', 'Y')

@socketio.on('confirm', namespace=Laser.NAMESPACE)
def laser_confirm(laser_instrument):
	app.logger.info(f'Laser Etch QC confirm, laser instrument: {laser_instrument}')
	errno = 0 # Default no error

	# Save variables
	session[Laser.INSTRUMENT] = laser_instrument

	if app.use_flask_serial:
		plc_ser.on_send('S\r\n')
	else:
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
					sleep(0.1)

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
					sleep(0.1)
		
		# TODO: Handle sdata error

		if sdata:
			session[Laser.RACK_ID] = sdata[:-2]
			app.logger.info('Laser Etch QC received ' + session[Laser.RACK_ID])
			if (sdata[:5] == 'ERROR'):
				app.logger.warn('Can not read 1D barcode')
				errno = -2
			else:
				if (sdata[:2] not in configfile.laser_etch_QC['Prefix']):
					errno = -3
					app.logger.warn('Invalid Rack ID')
		else:
			errno = -1

		app.logger.warn(errno)

		if (errno == 0):
			# Get barcodes
			data = tcpclient.send('T1').pop(0)
			session[Laser.DATA] = data

			app.logger.info('Redirecting page to laser_process')
		else:
			session[Laser.DATA] = ['1', ''] * 24
			# data = b'T1,0,MS3092555-RMF,0,TG2003637-RMF,0,MS3007019-TMP,0,TG2003671-RMF,0,TG2003667-RMF,0,TG2003626-RMF,0,TG2003657-RMF,0,TG2003660-RMF,0,MS6754129-LMX2,0,TG2003642-RMF,0,MS2929572-AMS1,0,MS6999347-LMX1,0,MS6324325-NULL,0,MS5357075-PW1,0,MS3085936-LPM,0,MS3247197-HP11,0,MS6262931-NULL,0,MS5342413-PW1,0,TG2003635-RMF,0,TG2003630-RMF,0,MS3040982-HP12,0,TG2003661-RMF,0,MS6675922-LDR,0,TG2003640-RMF'

		session[Laser.ERRORCODE] = errno
		plc_ser.send_data('GB')
		app.logger.info("Sending GB")
		emit('redirect', url_for('laser_process'))

@socketio.on('scan-position', namespace=Laser.NAMESPACE)
def read_barcodes():
	# Get Rack ID
	barcode_ser.purge()
	barcode_ser.send_data("LON")

	errno = 0
	start = timer()
	sdata = None
	while True:
		if barcode_ser.data_ready:
			sdata = barcode_ser.get().strip()
			break
		else:
			end = timer()
			if end - start > 2.0:
				app.logger.warn('Timeout getting barcode')
				errno = -2
				break
			else:
				sleep(0.1)
	
	# TODO: Handle sdata error

	if sdata:
		session[Laser.RACK_ID] = sdata
		app.logger.info('Rack ID: ' + sdata)
		if (sdata == 'ERROR'):
			app.logger.error('Error reading Rack ID barcode')
			errno = -3
		else:
			# Check the prefix
			if (sdata[:2] not in configfile.laser_etch_QC['Prefix']):
				errno = -4
				app.logger.error('Invalid Rack ID')
	else:
		session[Laser.RACK_ID] = ''
		errno = -1

	if (errno == 0):
		# Get barcodes
		items = tcpclient.send('T1')
		items.pop(0)
		totalitem = int(len(items)/2)
		masklen = -len(session[Laser.MASK])
		newdata = []
		
		if (session[Laser.RACK_TYPE] == Laser.RACK_TYPE.TROUGH):
			if (totalitem != Laser.ITEM_QTY.TROUGH):
				errno = -6
		elif (session[Laser.RACK_TYPE] == Laser.RACK_TYPE.TUBE):
			if (totalitem != Laser.ITEM_QTY.TUBE):
				errno = -6
		
		if (errno == 0):
			for i in range(totalitem):

				if (items[i*2] == '0'): #success
					# app.logger.info('ok barcode')
					if (items[i*2+1][masklen:] == session[Laser.MASK]):
						newdata.append('0')
						newdata.append(items[i*2+1])
					else:
						newdata.append('1')
						newdata.append(items[i*2+1])
						# app.logger.info(newdata)
						errno = -5
				else:
					newdata.append('1')
					newdata.append(items[i*2+1])
					errno = -7
			app.logger.info(newdata)
			session[Laser.DATA] = newdata
		else:
			if (session[Laser.RACK_TYPE] == Laser.RACK_TYPE.TROUGH):
				session[Laser.DATA] = ['1', ''] * 4
			else:
				session[Laser.DATA] = ['1', ''] * 24

	else:
		if (session[Laser.RACK_TYPE] == Laser.RACK_TYPE.TROUGH):
			session[Laser.DATA] = ['1', ''] * 4
		else:
			session[Laser.DATA] = ['1', ''] * 24

		# data = b'T1,0,MS3092555-RMF,0,TG2003637-RMF,0,MS3007019-TMP,0,TG2003671-RMF,0,TG2003667-RMF,0,TG2003626-RMF,0,TG2003657-RMF,0,TG2003660-RMF,0,MS6754129-LMX2,0,TG2003642-RMF,0,MS2929572-AMS1,0,MS6999347-LMX1,0,MS6324325-NULL,0,MS5357075-PW1,0,MS3085936-LPM,0,MS3247197-HP11,0,MS6262931-NULL,0,MS5342413-PW1,0,TG2003635-RMF,0,TG2003630-RMF,0,MS3040982-HP12,0,TG2003661-RMF,0,MS6675922-LDR,0,TG2003640-RMF'

	session[Laser.ERRORCODE] = errno
	# writing to log file
	logdata = (session[Laser.WORK_ORDER], session[Laser.PART_NUMBER], session[Laser.INSTRUMENT], session[Laser.RACK_ID])
	if (errno == 0): # pass
		logdata = logdata + ('TRUE', 'TRUE', 'TRUE', 'PASS',)
	else:
		if (errno > -5):
			logdata = logdata + ('TRUE', 'FALSE', 'FALSE', 'FAIL',)
		else:
			logdata = logdata + ('TRUE', 'TRUE', 'FALSE', 'FAIL',)

	Log_file.write_file (configfile.laser_etch_QC['LogFile'], logdata, 1)
	app.logger.info("Go to home position")
	plc_ser.on_send('GB\r\n')
	app.logger.info('Redirecting page to laser_process')
	emit('redirect', url_for('laser_process'))

@socketio.on('move_images', namespace=Laser.NAMESPACE)
def laser_move_images():
	app.logger.info('Move vision images')
	subfolder = session[Laser.RACK_ID] +datetime.now().strftime('_%Y%m%d_%H%M%S')
	move_image_files(configfile.laser_etch_QC['ImageDir'], subfolder)

# PLC_SERIAL message
@plc_ser.on_message()
def handle_message(msg):
	senddata = msg.decode("utf-8").strip()
	if (senddata in ('G2')):
		socketio.emit('plc-message', senddata, namespace=Laser.NAMESPACE)
	elif (senddata in ('G1', 'G3')):
		socketio.emit('plc-message', senddata, namespace=Cartridge.NAMESPACE)
	elif (senddata in ('R')):
		socketio.emit('plc-message', senddata, namespace=Laser.NAMESPACE)
		socketio.emit('plc-message', senddata, namespace=Cartridge.NAMESPACE)
	elif (senddata in ('H0', 'E')):
		socketio.emit('plc-message', senddata, namespace=Laser.NAMESPACE)
		socketio.emit('plc-message', senddata, namespace=Cartridge.NAMESPACE)
		socketio.emit('plc-message', senddata, namespace='/home/api')

@plc_ser.on_log()
def handle_logging(level, info):
	app.logger.info(info)

@socketio.on('plc-message', namespace=Laser.NAMESPACE)
def dotest(msg):
	app.logger.info(msg)

#@socketio.on_error_default
#def default_error_handler(e):
#	app.logger.error(request.event['message'])
#	app.logger.error(request.event['args'])
