import socket
import sys


# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
server_address = ('localhost', 10000)
print ('connecting to %s port %s' % server_address, file=sys.stderr)
sock.connect(server_address)

try:
    
    # Send data
    message = input('Data to send: ')
    print ('sending "%s"' % message, file=sys.stderr)
    sock.sendall(str.encode(message))

    # Look for the response
    amount_received = 0
    amount_expected = len(message)
    
    while amount_received < amount_expected:
        data = sock.recv(100)
        amount_received += len(data)
        print ('received "%s"' % data.decode('utf-8'), file=sys.stderr)

				# 000000000010000000000200000000003000000000040000000000500000000006000000000070000000000800000000009000000000010000000000100000000002

finally:
    print ('closing socket', file=sys.stderr)
    sock.close()