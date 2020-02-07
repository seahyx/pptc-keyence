from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField, SubmitField
from wtforms.validators import ValidationError, DataRequired, EqualTo, Length
from app.models import User

class LoginForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired('Username is required, please')])
	password = PasswordField('Password', validators=[DataRequired('Password is required, please')])
	rmb_me = BooleanField('Remember this login')
	submit = SubmitField('Enter')

class RegistrationForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired('Username is required, please'), Length(min=4, message='Username must be at least %(min)d letters long')])

	password = PasswordField('Password', validators=[DataRequired('Password is required, please'), Length(min=4, message='Password must be at least %(min)d characters long')])

	password2 = PasswordField('Confirm Password', validators=[DataRequired('Please confirm the password'), EqualTo('password', 'Passwords must match, please try again')])

	account_type = SelectField('Account Type', choices=User.ACCOUNT_TYPES[1:len(User.ACCOUNT_TYPES)], coerce=int, default=2)

	submit = SubmitField('Register')

	def validate_username(self, username):
		user = User.query.filter_by(username=username.data).first()
		if user is not None:
			raise ValidationError('This username has been taken, please choose another one')

class ChangePasswordForm(FlaskForm):
	password = PasswordField('Password', validators=[DataRequired('Password is required'), Length(min=4, message='Password must be at least %(min)d characters long')])

	password2 = PasswordField('Confirm Password', validators=[DataRequired('Please confirm the password'), EqualTo('password', 'Passwords must match')])

	submit = SubmitField('Register')