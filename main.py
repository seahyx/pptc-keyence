from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def index():
	return render_template('home.html')

@app.route('/open-door/')
def api():
	return jsonify(result='hello')