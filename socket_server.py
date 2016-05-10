import socket
import sys
import time

HOST = '209.2.212.214'
PORT = 8888
BACKLOG = 10
SIZE = 1024

try:
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except:
	print 'Fail to create socket'
	sys.exit()
print 'Socket Created'

try:
	s.bind((HOST,PORT))
	s.listen(BACKLOG)
except:
	print "Fail to bind host and port"
print "Binded host and port"

while True:
	print 'Waiting for connection'
	client, address = s.accept()
	print 'Connection established'
	client.send('Hello' + '\r\n')
	print 'Sent: ' + 'Hello'

	while True:
		try:
			received_msg = client.recv(SIZE)
		except KeyboardInterrupt:
			sys.exit(-1)
		except:
			break

		if received_msg:
			print 'Received: ' + str(received_msg)
		else:
			break

	print 'Socket closed'
	client.close()