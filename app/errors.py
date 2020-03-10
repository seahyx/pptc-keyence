from flask import render_template
from app import app, db

@app.errorhandler(404)
def not_found_error(error):
	app.logger.warning('404 Resource Not Found')
	return render_template('404.html', title='404 This is a sad day', no_header=True), 404

@app.errorhandler(500)
def internal_error(error):
	db.session.rollback()
	app.logger.warning('500 Internal Server Error')
	return render_template('500.html', title='500 This is a sad day', no_header=True), 500