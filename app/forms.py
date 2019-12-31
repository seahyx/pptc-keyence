from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField, SubmitField
from wtforms.validators import ValidationError, DataRequired, EqualTo, Length
from app.models import User

class LoginForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired('Username is required, please')])
	password = PasswordField('Password', validators=[DataRequired('Password is required, please')])
	rmb_me = BooleanField('Remember Me')
	submit = SubmitField('Enter')

class RegistrationForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired('Username required lah'), Length(min=4, message='Username must be at least %(min)d letters long eh')])

	password = PasswordField('Password', validators=[DataRequired('Password also required lah'), Length(min=4, message='Password must be at least %(min)d characters long eh')])

	password2 = PasswordField('Confirm Password', validators=[DataRequired('Confirm the password leh'), EqualTo('password', 'Password type second time must be same eh')])

	account_type = SelectField('Account Type', choices=[(0, 'User'), (1, 'Admin')], coerce=int, default=0)

	submit = SubmitField('Register')

	def validate_username(self, username):
		user = User.query.filter_by(username=username.data).first()
		if user is not None:
			raise ValidationError('This username chosen already lah')
