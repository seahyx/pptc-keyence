import threading
import socket
import sys

class TCPClient:
	''' TCP interface for client

	This class will connect to the Vision TCP server/dummy test server
	in the background. It will initialize with the server address and port
	as configured in the config file.

	:param app: The flask application instance.

	:param address: IP address of the tcp server. Defaults to ``'localhost'``.

	:param port: Port number of the tcp server. Defaults to ``8500``.
	'''

	SERVER_ADDRESS = None
	sock = None
	app = None

	def __init__(self, app, address='localhost', port=8500):

		# Get app
		self.app = app

		# Create a TCP/IP socket
		self.SERVER_ADDRESS = (address, port)

	def connect(self):
		''' Connect the socket to the port where the server is listening '''

		try:
			self.app.logger.info(f'Attempting connection to {self.SERVER_ADDRESS[0]}, port {self.SERVER_ADDRESS[1]}')
			self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.sock.connect(self.SERVER_ADDRESS)
			self.app.logger.info(f'Connected to {self.SERVER_ADDRESS[0]}, port {self.SERVER_ADDRESS[1]}')
			return True

		except:
			self.app.logger.info(f'Connection failed')
			return False

	def send(self, message):
		''' Send message

		:type message: str
		:param message: Message to be sent
		'''

		# Connect to server
		connected = self.connect()
		if not connected:
			return None

		data_decoded = ['']

		try:
			# Send data
			self.app.logger.info(f'Sending "{message}" to server')
			self.sock.sendall(str.encode(message))

			# Look for the response
			data = self.sock.recv(1024)
			
			# Response is received
			data_decoded = data.decode('utf-8').split(',')
			self.app.logger.info(f'Received {data_decoded} from server')

		except:

			self.app.logger.warning(f'Failed to send "{message}" to {self.SERVER_ADDRESS[0]}, port {self.SERVER_ADDRESS[1]}')

		finally:

			self.sock.close()
			self.app.logger.info(f'Closed client socket')
			
			return data_decoded