from flask import Flask
from config import Config
from configfile import ConfigFile
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_socketio import SocketIO
from flask_session import Session

use_flask_serial = True
if use_flask_serial:
	from flask_serial import Serial
	from flask_bootstrap import Bootstrap

from logging.config import dictConfig
from logging.handlers import SMTPHandler
from logging.handlers import RotatingFileHandler
from tcpclient import TCPClient
from serialclient import SerialClient
from csvreader import CSVReader
import logging
import os

import eventlet
eventlet.monkey_patch(thread=True, time=True)

# Logging configuration
dictConfig({
		'version': 1,
		'formatters': {'default': {
				'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
		}},
		'handlers': {'wsgi': {
				'class': 'logging.StreamHandler',
				'stream': 'ext://flask.logging.wsgi_errors_stream',
				'formatter': 'default'
		}},
		'root': {
				'level': 'INFO',
				'handlers': ['wsgi']
		}
})

app = Flask(__name__)

# Debug mode (development environment)
app.debug = False
debug_mode = False


# Init modules
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'
socketio = SocketIO(app, manage_session=False)
Session(app)
configfile = ConfigFile(app, 'main.cfg')
csvreader = CSVReader(configfile.laser_etch_QC['PNFile'])

if use_flask_serial:
	app.config['SERIAL_TIMEOUT'] = 0.1
	app.config['SERIAL_PORT'] = configfile.PLC_PORT
	app.config['SERIAL_BAUDRATE'] = configfile.PLC_BAUDRATE
	app.config['SERIAL_BYTESIZE'] = configfile.PLC_BYTESIZE
	app.config['SERIAL_PARITY'] = configfile.PLC_PARITY
	app.config['SERIAL_STOPBITS'] = configfile.PLC_STOPBITS

	plc_ser = Serial(app)
	bootstrap = Bootstrap(app)

# Insert root user if none exists
from app.models import User
try:
	userlist = User.query.all()
	
	if len(userlist) == 0:
		app.logger.info('Creating root user')
		user = User(username='root', account_type=0, password_hash='pbkdf2:sha256:150000$Sn5LeTtv$b9bfc8a77bc8e232c90f494dc09c64c2b9604901b3b34a1ea6d03ebea3083cdf')
		db.session.add(user)
		db.session.commit()
		
except:
	app.logger.warn('Error, no user table')

	with app.app_context():
		from flask_migrate import init as db_init, migrate as db_migrate, upgrade as db_upgrade
		app.logger.info('Initializing database...')
		db_init()
		db_migrate(message='Initializing database')
		db_upgrade()
		app.logger.info('Database initialized')

	app.logger.info('Creating root user')
	user = User(username='root', account_type=0, password_hash='pbkdf2:sha256:150000$Sn5LeTtv$b9bfc8a77bc8e232c90f494dc09c64c2b9604901b3b34a1ea6d03ebea3083cdf')
	db.session.add(user)
	db.session.commit()

# For debug
tcpclient = None
if debug_mode:
	tcpclient = TCPClient(app, 'localhost', 8500)
else:
	tcpclient = TCPClient(app, configfile.VISION_TCP_ADDR, configfile.VISION_TCP_PORT)

#PLC serial port
# plcSer = None
# Use flask-serial to handle
if not use_flask_serial:
	plc_ser = SerialClient(app, configfile.PLC_PORT, configfile.PLC_BAUDRATE, configfile.PLC_BYTESIZE,
				configfile.PLC_PARITY, configfile.PLC_STOPBITS)

# barcode reader serial port
barcode_ser = SerialClient(app, configfile.BARCODE_PORT, configfile.BARCODE_BAUDRATE, configfile.BARCODE_BYTESIZE,
			configfile.BARCODE_PARITY, configfile.BARCODE_STOPBITS)

from app import routes, models, errors, permissions

# Connection handshake with Vision System
tcpclient.send('R0')
# tcpclient.send('PW,1,001')

# Initialize motor
if use_flask_serial:
	plc_ser.on_send('H\r\n')
else:
	plc_ser.send_data('H')
app.logger.info('Sending H')

# Production email logging and file logs
if not debug_mode:
	# Send email to admins when server encounter errors in production
	if app.config['MAIL_SERVER']:
		auth = None
		if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
			auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
		secure = None
		if app.config['MAIL_USE_TLS']:
			secure = ()
		mail_handler = SMTPHandler(
			mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
			fromaddr='no-reply@' + app.config['MAIL_SERVER'],
			toaddrs=app.config['ADMINS'], subject='PPTC-Keyence Server Error Log',
			credentials=auth, secure=secure)
		mail_handler.setLevel(logging.ERROR)
		app.logger.addHandler(mail_handler)

	# Creates log files
	if not os.path.exists('logs'):
		os.mkdir('logs')
	file_handler = RotatingFileHandler('logs/2DBarcode.log', maxBytes=10240,
										 backupCount=10)
	file_handler.setFormatter(logging.Formatter(
		'%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
	file_handler.setLevel(logging.INFO)
	app.logger.addHandler(file_handler)

	app.logger.setLevel(logging.INFO)
	app.logger.info('Server startup...')