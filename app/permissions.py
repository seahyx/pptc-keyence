from flask import flash, redirect, url_for
from flask_login import current_user
from app import app
from functools import wraps

class PermissionsManager():
	''' Restricts user access to administrative functions '''
	
	redirect_view = ''

	def admin_required(self, func):
		@wraps(func)
		def wrapper(*args, **kwargs):
			if current_user.is_authenticated and current_user.has_admin_rights():
				return func(*args, **kwargs)
			else:
				flash('Page access denied, admin privileges required')
				app.logger.info(f'{current_user.username} denied access, admin privileges required')
				return redirect(url_for(self.redirect_view))
		return wrapper