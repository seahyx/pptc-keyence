import socket
import sys

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
server_address = ('localhost', 8500)
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
					data = b'T1,0,MS3092555-RMF,0,TG2003637-RMF,0,MS3007019-TMP,0,TG2003671-RMF,0,TG2003667-RMF,0,TG2003626-RMF,0,TG2003657-RMF,0,TG2003660-RMF,0,MS6754129-LMX2,0,TG2003642-RMF,0,MS2929572-AMS1,0,MS6999347-LMX1,0,MS6324325-NULL,0,MS5357075-PW1,0,MS3085936-LPM,0,MS3247197-HP11,0,MS6262931-NULL,0,MS5342413-PW1,0,TG2003635-RMF,0,TG2003630-RMF,0,MS3040982-HP12,0,TG2003661-RMF,0,MS6675922-LDR,0,TG2003640-RMF'
				elif (message[0] == 'R0'):
					data = b'R0'
				elif (message[0][:2] == 'PW'):
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