import socket

HOST = '209.2.212.86'
PORT = 8888
BACKLOG = 10
SIZE = 1024

try:
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	print 'Socket Created'
except:
	print 'Fail to create socket'

try:
    s.bind((HOST,PORT))
    s.listen(BACKLOG)
except:
    print "Fail to bind host and port"

while (1):
    client, address = s.accept()
    data = client.recv(SIZE)
    if data:
        client.send(data)
        print data
    client.close()
