import socket
import sys

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
server_address = ('localhost', 10000)
print (f'starting up on {server_address[0]} port {server_address[1]}', file=sys.stderr)
sock.bind(server_address)

# Listen for incoming connections
sock.listen(1)
toExit = False

while True:
	# Wait for a connection
	print('Waiting for a connection...', file=sys.stderr)

	connection, client_address = sock.accept()
	
	try:
		print('Connection from {client_address}', file=sys.stderr)

		# Receive the data in small chunks and retransmit it
		while True:

			data = connection.recv(1024)
			message = data.decode('utf-8').split(',')
			print(f'Received "{message}"', file=sys.stderr)

			if data:
				if (message[0] == 'T1'):
					data = b'T1 MSG-1001, MSG-1002, MSG-1003'
				elif (message[0] == 'N0'):
					data = b'N0'
				elif (message[0] == 'PW'):
					data = b'PW'
				elif (message[0] == 'exit'):
					toExit = True
				
				if not toExit:
					print('Sending data back to the client', file=sys.stderr)
					connection.sendall(data)
			else:
				print('No more data from', client_address, file=sys.stderr)
				break
		if (toExit):
			print('Closing connection', file=sys.stderr)
			connection.close()    
			break
			
	finally:
		# Clean up the connection
		connection.close()    