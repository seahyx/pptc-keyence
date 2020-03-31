from os import path, environ
basedir = path.abspath(path.dirname(__file__))

import sys
from configparser import ConfigParser

class ConfigFileLoader:
	''' Configuration file loader
	
	:param file: Configuration file to be read.
	'''

	CONF_SECTION = 'conf'
	PARSER = ConfigParser()
	config = ''

	def __init__(self, file):
		with open(file) as stream:
			self.PARSER.read_string(f'[{self.CONF_SECTION}]\n' + stream.read())
			self.config = self.PARSER[self.CONF_SECTION]
			print('Reading configuration files...', file=sys.stderr)
			for item in self.config:
				print(f'{item:<30} = {self.config[item]}', file=sys.stderr)

	def get(self, attribute, default):
		value = ''
		try:
			value = self.config[attribute]
		except KeyError:
			print(f'Error retrieving value from attribute {attribute}: Attribute does not exist', file=sys.stderr)
			value = default
		except:
			print(f'Error retrieving value from attribute {attribute}', file=sys.stderr)
			value = default
		finally:
			return value

	def __repr__(self):
		return f'<ConfigFileLoader config={config}>'

class Config(object):
	''' Configuration settings storage '''

	# Load configuration files
	config = ConfigFileLoader('main.cfg')

	# Vision System TCP Server
	VISION_TCP_ADDR                = config.get('Vision TCP Addr', 'localhost')
	VISION_TCP_PORT                = int(config.get('Vision TCP Port', 10000))

	# Database
	SQLALCHEMY_DATABASE_URI        = environ.get('DATABASE_URL') or 'sqlite:///' + path.join(basedir, 'app.db')
	SQLALCHEMY_TRACK_MODIFICATIONS = False

	# Flask-Session
	SESSION_TYPE                   = environ.get('SESSION_TYPE') or 'sqlalchemy'

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