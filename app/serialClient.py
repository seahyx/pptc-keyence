import time
import serial
import threading
import sys
import queue


class SerialClient:

	''' Serial interface to barcode scanner

	This class will attempt a serial connection to the specified port on the terminal. Can be used as follows::

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
	
	def __init__(self, app, port, baudrate=9600, parity=serial.PARITY_EVEN, 
				stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=1):
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