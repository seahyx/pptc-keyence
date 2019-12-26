from flask import Flask, render_template, request, jsonify
import wiringpi
import time

app = Flask(__name__)

# Wiring pi setup
wiringpi.wiringPiSetup()

wiringpi.pinMode(4, 1)

@app.route('/')
def index():
	return render_template('home.html')

@app.route('/open-door/')
def api():
	print('API request received')
	open_door()
	return jsonify(result='success')


def open_door():
	wiringpi.digitalWrite(4, 1)
	time.sleep(500)
	wiringpi.digitalWrite(4, 0)


# If we're running this script directly, this portion executes. The Flask
#  instance runs with the given parameters. Note that the "host=0.0.0.0" part
#  is essential to telling the system that we want the app visible to the 
#  outside world.
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)