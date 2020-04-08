''' Dummy TCP server

This program is meant for testing and not to be run in production.
It will simulate the Vision system TCP responses for testing purposes.
'''


import threading
import socket
import sys


address, port = 'localhost', 8500


# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
SERVER_ADDRESS = (address, port)
print(f'Starting test server up on {address}, port {port}')
sock.bind(SERVER_ADDRESS)
print('Attempting to bind server address to socket')

# Listen for incoming connections
sock.listen(1)
toExit = False

while True:
	# Wait for a connection
	print('Waiting for a client connection...')

	connection, client_address = sock.accept()

	try:
		print(f'Connection from client {client_address}')

		while True:

			# Receive the message, should not be longer than buffersize per message
			data = connection.recv(1024)

			message = data.decode('utf-8').replace('\r', '').split(',')
			print(f'Received {message} from client')

			if data:
				if (message[0] == 'T1'):
					data = b'T1,0,MS3092555-RMF,0,TG2003637-RMF,0,MS3007019-TMP,0,TG2003671-RMF,0,TG2003667-RMF,0,TG2003626-RMF,0,TG2003657-RMF,0,TG2003660-RMF,0,MS6754129-LMX2,0,TG2003642-RMF,0,MS2929572-AMS1,0,MS6999347-LMX1,0,MS6324325-NULL,0,MS5357075-PW1,0,MS3085936-LPM,0,MS3247197-HP11,0,MS6262931-NULL,0,MS5342413-PW1,0,TG2003635-RMF,0,TG2003630-RMF,0,MS3040982-HP12,0,TG2003661-RMF,0,MS6675922-LDR,0,TG2003640-RMF'
				elif (message[0] == 'R0'):
					data = b'R0'
				elif (message[0][:2] == 'PW'):
					data = b'PW'
				elif (message[0] == 'exit'):
					toExit = True
					print('Exit signal received, breaking server loop')
					break

				print(f'Sending {repr(data.decode("utf-8"))} back to the client')
				connection.sendall(data)

			else:
				print(f'No more data from client {client_address}')
				break

		if toExit:
			connection.close()
			break

	finally:
		# Clean up the connection
		connection.close()
		print('Closed client connection')

		if toExit:
			break

print('Dummy tcp server closed')