from os import path, environ
basedir = path.abspath(path.dirname(__file__))

import sys

class Config(object):
	''' Configuration settings storage '''

	# Database
	SQLALCHEMY_DATABASE_URI        = environ.get('DATABASE_URL') or 'sqlite:///' + path.join(basedir, 'app.db')
	SQLALCHEMY_TRACK_MODIFICATIONS = False

	# Flask-Session
	SESSION_TYPE                   = environ.get('SESSION_TYPE') or 'filesystem'

	# Flask Debug Tool
	DEBUG_TB_INTERCEPT_REDIRECTS   = False

	# Email
	MAIL_SERVER                    = environ.get('MAIL_SERVER')
	MAIL_PORT                      = int(environ.get('MAIL_PORT') or 25)
	MAIL_USE_TLS                   = environ.get('MAIL_USE_TLS') is not None
	MAIL_USERNAME                  = environ.get('MAIL_USERNAME')
	MAIL_PASSWORD                  = environ.get('MAIL_PASSWORD')
	ADMINS                         = ['seahyx@gmail.com', 'seahyw@gmail.com']

	# Secret key
	SECRET_KEY                     = environ.get('SECRET_KEY') or 'you-will-never-guess'