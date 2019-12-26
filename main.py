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
	open_door()
	return jsonify(result='success')


def open_door():
	wiringpi.digitalWrite(4, 1)
	time.sleep(500)
	wiringpi.digitalWrite(4, 0)
