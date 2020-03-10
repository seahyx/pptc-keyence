import socket
import sys

class TCPClient:

	SERVER_ADDRESS = None
	sock = None
	app = None

	def __init__(self, app, address, port):

		# Get app
		self.app = app

		# Create a TCP/IP socket
		self.SERVER_ADDRESS = (address, port)

	def connect(self):
		# Connect the socket to the port where the server is listening
		self.app.logger.info(f'Connecting to {self.SERVER_ADDRESS[0]}, port {self.SERVER_ADDRESS[1]}')
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.connect(self.SERVER_ADDRESS)
		self.app.logger.info(f'Connected to {self.SERVER_ADDRESS[0]}, port {self.SERVER_ADDRESS[1]}')

	def send(self, message):

		# Connect to server
		self.connect()

		try:
			# Send data
			self.app.logger.info(f'Sending "{message}" to {self.SERVER_ADDRESS[0]}, port {self.SERVER_ADDRESS[1]}')
			self.sock.sendall(str.encode(message))

			# Look for the response
			data = self.sock.recv(1024).decode('utf-8')
			self.app.logger.info(f"Received \"{data}\" from {self.SERVER_ADDRESS[0]}, port {self.SERVER_ADDRESS[1]}")
		except:
			self.app.logger.warning(f'Failed to send "{message}" to {self.SERVER_ADDRESS[0]}, port {self.SERVER_ADDRESS[1]}')
		finally:
			self.app.logger.info(f'Closing socket to {self.SERVER_ADDRESS[0]}, port {self.SERVER_ADDRESS[1]}')
			self.sock.close()