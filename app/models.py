from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

@login.user_loader
def load_user(id):
	return User.query.get(int(id))

class User(UserMixin, db.Model):
	''' User database class
	
	Class representative of a user entry in the database.

	:var id: Primary key in database entry.
	
	:var username: Username of the user. Has a maximum of 32 characters. Is unique (cannot be repeated).

	:var password_hash: Hashed value of the user's password.

	:var account_type: Role of user.
	'''

	id = db.Column(db.Integer, primary_key=True)

	# account username
	username = db.Column(db.String(32), index=True, unique=True)

	# account password
	password_hash = db.Column(db.String(128))

	# account permission level
	account_type = db.Column(db.Integer, index=True)

	ACCOUNT_TYPES = [(0, 'Root'), (1, 'Administrator'), (2, 'Operator')]

	def set_password(self, password):
		''' Generates and updates password hash for the user. '''

		self.password_hash = generate_password_hash(password)
	
	def check_password(self, password):
		''' Returns ``True`` if password input is valid. '''

		return check_password_hash(self.password_hash, password)

	def get_account_type_name(self):
		''' Gets the descriptive name of the user's account type. '''

		return self.ACCOUNT_TYPES[self.account_type][1]
	
	def has_admin_rights(self):
		''' Returns ``True`` if user has admin rights. '''

		return (self.account_type == 0 or self.account_type == 1)

	def __repr__(self):
		return '<{} {}, account_type {}>'.format(self.get_account_type_name(), self.username, self.account_type)
