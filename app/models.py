from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

@login.user_loader
def load_user(id):
	return User.query.get(int(id))

class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key = True)
	username = db.Column(db.String(64), index = True, unique = True)
	password_hash = db.Column(db.String(128))
	account_type = db.Column(db.Integer, index = True)

	ACCOUNT_TYPES = [(0, 'Root'), (1, 'Admin'), (2, 'User')]

	def set_password(self, password):
		self.password_hash = generate_password_hash(password)
	
	def check_password(self, password):
		return check_password_hash(self.password_hash, password)

	def get_account_type_name(self):
		return self.ACCOUNT_TYPES[self.account_type][1]
	
	def has_admin_rights(self):
		return (self.account_type == 0 or self.account_type == 1)

	def __repr__(self):
		return '<{} {}, account_type {}>'.format(self.get_account_type_name(), self.username, self.account_type)