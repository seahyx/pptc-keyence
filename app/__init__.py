from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_socketio import SocketIO
from logging.config import dictConfig
from logging.handlers import SMTPHandler
from logging.handlers import RotatingFileHandler
from app.tcpclient import TCPClient
from app.test.tcpserver import TCPServer
import logging
import os

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
app.debug = True

# Init modules
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'
socketio = SocketIO(app)

# For debug
tcpserver = None
tcpclient = TCPClient(app, app.config['VISION_TCP_ADDR'], app.config['VISION_TCP_PORT'])
if app.debug:
	tcpserver = TCPServer(app)
	tcpclient = TCPClient(app)

from app import routes, models, errors, permissions

# Insert root user if none exists
from app.models import User
userlist = User.query.all()
if len(userlist) == 0:
	user = User(username='root', account_type=0, password_hash='pbkdf2:sha256:150000$Sn5LeTtv$b9bfc8a77bc8e232c90f494dc09c64c2b9604901b3b34a1ea6d03ebea3083cdf')
	db.session.add(user)
	db.session.commit()

# Connection handshake with Vision System
tcpclient.send('R0')
tcpclient.send('PW,1,001')

# Production email logging and file logs
if not app.debug:
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
	file_handler = RotatingFileHandler('logs/PPTC-Keyence.log', maxBytes=10240,
										 backupCount=10)
	file_handler.setFormatter(logging.Formatter(
		'%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
	file_handler.setLevel(logging.INFO)
	app.logger.addHandler(file_handler)

	app.logger.setLevel(logging.INFO)
	app.logger.info('Server startup...')