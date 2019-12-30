from app import db


class User(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	username = db.Column(db.String(64), index = True, unique = True)
	password_hash = db.Column(db.String(128))
	accountType = db.Column(db.Integer, index = True)

	def __repr__(self):
		return '<User {}, accountType {}>'.format(self.username, self.accountType)