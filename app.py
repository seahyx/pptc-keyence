from app import app, db
from app.models import User
from flask_socketio import SocketIO, emit

# Debug mode (development environment)
app.debug = True
socketio = SocketIO(app)

@app.shell_context_processor
def make_shell_context():
	return {'db': db, 'User': User}

#  If we're running this script directly, this portion executes. The Flask
#  instance runs with the given parameters. Note that the "host=0.0.0.0" part
#  is essential to telling the system that we want the app visible to the 
#  outside world.
if __name__ == "__main__":
	socketio.run(app)