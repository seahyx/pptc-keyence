from flask import flash, redirect, url_for
from flask_login import current_user
from app import app
from functools import wraps

class PermissionsManager():
	redirect_view = ''

	def admin_required(self, func):
		@wraps(func)
		def wrapper(*args, **kwargs):
			if current_user.is_authenticated and current_user.has_admin_rights():
				return func(*args, **kwargs)
			else:
				flash('You do not have the permission to access this page')
				return redirect(url_for(self.redirect_view))
		return wrapper