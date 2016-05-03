import socket
import threading
import csv
import time

HOST = '209.2.212.58'		# Server host
PORT = 8888					# Server port
BACKLOG = 10
SIZE = 1024					# message size

cols = ['TimeStamp', 'AdjustTempTo', 'CurrentRoomTemp', 'CurrentRoomHumidity', 'CurrentOutdoorTemp', 'CurrentOutdoorHumidity']

class AppCommuniacteServerThread(threading.Thread):
	
	def __init__(self, threadName):
		threading.Thread.__init__(self)
		self.threadName = threadName
		self.mode = None
		self.setTemp = None
		self.currentTemp = None


	def run(self):
		print "Starting thread:", self.threadName + "..."
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		print 'Socket Created'

		try:
			s.bind((HOST,PORT))
			s.listen(BACKLOG)
		except:
			print "Fail to bind host and port, exiting"
			exit()

		while 1:
			client, address = s.accept()
			
			data = client.recv(SIZE)
			if data:
				# When receving message
				# Retrive data, log data to file, execute command.
				if type(data) is str:
					print "App message received:", data
					# First character in data indicates mode.
					if data[0] == 'M':
						# Manual mode
						self.setTemp = int(data[1:3])
						print "Execution: set temperature to", self.setTemp

						with open('userCommand.csv', 'wb') as csvfile:
							writer = csv.DictWriter(csvfile, fieldnames = cols)
							writer.writerow({''})

						with open(fileName, 'a') as csvfile:
							writer = csv.DictWriter(csvfile, fieldnames = cols)
							writer.writerow(self.tempDict)

					elif data[0] == 'S':
						# Schedule task
						if data[1] == 'A':
							# Absolute temperature adjustment
							# Data format: "MA26"
							self.setTemp = int(data[2:4])
							print "Set temperature to", self.setTemp
						elif data[1] == 'R':
							# Relative temperature adjustment
							if data[2] == 'U':
								# Temperature up
								self.setTemp += 1
								print "Set temperature to", self.setTemp
							elif data[2] == 'D':
								# Temperature down
								self.setTemp -= 1
								print "Set temperature to", self.setTemp

					elif data[0] == 'A':
						# Auto mode
						pass

				else:
					print "Communicate data type error"

			client.close()

if __name__ == '__main__':
	appThread = AppCommuniacteServerThread("AppCommunicateThread")
	appThread.start()
