from functools import wraps
import time
import serial
import threading
import sys
import queue


class SerialClient:

	''' Serial interface to barcode scanner

	This class will attempt a serial connection to the specified port on the terminal. Can be used as follow::

		from flask import Flask
		from serialclient import SerialClient

		app = Flask(__name__)

		# Init and attempt connection to com3
		plc_ser = SerialClient(app, "com3")

		# Send data
		plc_ser.send_data('R')

		# Check if data is ready
		if plc_ser.data_ready:

			# Retrieve data
			data = plc_ser.get()
			print(repr(data))

	A loop may be required to check if the data is ready before retrieving it.

	:param app: The flask application instance.

	:param port: The port to connect to.

	:param baudrate: Baud rate of the connection. Defaults to ``9600``.

	:param parity: Parity of the connection. Defaults to ``serial.PARITY_EVEN``.

	:param stopbits: Stop bits of the connection. Defaults to ``serial.STOPBITS_ONE``.

	:param bytesize: Size of a byte. Defaults to ``serial.EIGHTBITS``.

	:param timeout: Connection timeout. Defaults to ``1``.

	'''
	
	def __init__(self, app, port, baudrate=9600, bytesize=serial.EIGHTBITS, parity=serial.PARITY_EVEN, 
				stopbits=serial.STOPBITS_ONE, timeout=1):
		self.app = app
		self.data_ready = False
		self.data = None
		self.ser = None

		self.app.logger.info(f'Attempting open to port {port}')

		try:

			self.ser = serial.Serial(
				port=port,
				baudrate=baudrate,
				parity=parity,
				stopbits=stopbits,
				bytesize=bytesize,
				timeout=timeout
			)

			if self.ser.isOpen():
				self.ser.close()
			
			self.ser.open()
			
			self.thread = threading.Thread(target=self.read_from_port, args=())
			self.thread.daemon = True
			self.thread.start()

		except:

			self.app.logger.info(f'Failed to open port {port}')
			return
		
	def get(self):
		self.data_ready = False
		return self.data

	def purge(self):
		self.data_ready = False
		return
		
	def send_data(self, data):

		if not self.ser:
			self.app.logger.warn(f'Serial port not initialized, data {repr(data)} not sent')
			return

		self.app.logger.info(f'Sending {repr(data)}')
		return (self.ser.write(str.encode(data+"\r\n")))

	def close(self):
		
		if not self.ser:
			self.app.logger.warn(f'Serial port not initialized, port is closed')
			return
		
		self.app.logger.info('Closing serial port')
		self.ser.close()
		self.thread.stop()

	def handle_data (self, data):

		if not self.ser:
			self.app.logger.warn(f'Serial port not initialized, no data is handled')
			return
		
		self.app.logger.info(f'Received data {repr(data)}')
		self.data = data
		self.data_ready = True
		
	def read_from_port(self):
		self.app.logger.info(f'Reading serial from port')
		while True:
			reading = self.ser.readline().decode()
			if (len(reading) > 1):
				self.handle_data(reading)
			else:
				time.sleep(0.1)


	# Dummy commands to cover Serial on testing

	def on_send(self, data):
		self.app.logger.info(f'on_send: {data}')
	
	def on_message(self):
		''' Dummy on_message for testing without using Flask-Serial '''
		def decorator(func):
			@wraps(func)
			def wrapper():
				self.app.logger.info('on_message called, nothing is going to happen because this is for debugging')
			return wrapper
		return decorator
	
	def on_log(self):
		''' Dummy on_log for testing without using Flask-Serial '''
		def decorator(func):
			@wraps(func)
			def wrapper():
				self.app.logger.info('on_log called, nothing is going to happen because this is for debugging')
			return wrapper
		return decorator