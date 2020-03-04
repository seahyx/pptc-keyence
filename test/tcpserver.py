import socket
import sys

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
server_address = ('localhost', 10000)
print ('starting up on %s port %s' % server_address, file=sys.stderr)
sock.bind(server_address)

# Listen for incoming connections
sock.listen(1)
toExit = False

while True:
    # Wait for a connection
    print ('waiting for a connection', file=sys.stderr)
    connection, client_address = sock.accept()
    
    try:
        print ('connection from', client_address, file=sys.stderr)

        # Receive the data in small chunks and retransmit it
        while True:
            data = connection.recv(100)
            print ('received "%s"' % data, file=sys.stderr)
            if data:
                if (data == b'T1'):
                    data = b'T1 MSG-1001,MSG-1002,MSG-1003'
                print ('sending data back to the client', file=sys.stderr)
                connection.sendall(data)
                if (data == b'exit'):
                    toExit = True
            else:
                print ('no more data from', client_address, file=sys.stderr)
                break
        if (toExit):
            connection.close()    
            break
            
    finally:
        # Clean up the connection
        connection.close()    