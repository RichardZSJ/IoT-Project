import socket
import threading
import csv
import time
import datetime
import os

class AppCommuniacteServerThread(threading.Thread):
	
	def __init__(self, threadName):
		threading.Thread.__init__(self)
		self.threadName = threadName
		self.mode = None
		self.setTemp = None
		self.currentTemp = None
		self.fileName = 'userCommand.csv'
		self.HOST = '209.2.212.58'		# Server host
		self.PORT = 8888					# Server port
		self.BACKLOG = 10
		self.SIZE = 1024					# message size
		self.cols_user_command = ['TimeStamp', 'Mode', 'AdjustTempTo', 'ScheduleTime']
		self.cols_schedule = ['ScheduleTime', 'AdjustTempTo']

	def run(self):
		print "Starting thread:", self.threadName + "..."
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		print 'Socket Created'

		try:
			s.bind((self.HOST, self.PORT))
			s.listen(self.BACKLOG)
		except:
			print "Fail to bind host and port, change host address"
			exit()

		while 1:
			client, address = s.accept()
			
			data = client.recv(self.SIZE)
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
						commandDict = {'TimeStamp': int(time.time()), 'Mode': 'Manual', 'AdjustTempTo': self.setTemp}
						with open(fileName, 'a') as csvfile:
							writer = csv.DictWriter(csvfile, fieldnames = cols_user_command, lineterminator='\n')
							writer.writerow(commandDict)
						print "Logged user command to " + self.fileName

					elif data[0] == 'S':
						# Schedule task
						self.setTemp = int(data[1:3])
						unixScheduleTime = int(data[3:])
						datetimeTaskTime = datetime.datetime.fromtimestamp(unixScheduleTime).strftime('%Y-%m-%d %H:%M:%S')
						print "Schedule Task @ " + str(datetimeTaskTime) + ", set temperature to", self.setTemp
						commandDict = {'Mode': 'Schedule', 'setTemp': self.setTemp, 'Time': unixTaskTime}

						with open(fileName, 'a') as csvfile:
							writer = csv.DictWriter(csvfile, fieldnames=cols, lineterminator='\n')
							writer.writerow(commandDict)
						print "Logged user command to " + self.fileName
						reader = csv.reader(open(self.fileName))
						sortedSchedule = sorted(reader, key=operator.itemgetter(3), reverse=True)


					elif data[0] == 'A':
						# Auto mode
						pass

				else:
					print "Communicate data error"

			client.close()

if __name__ == '__main__':
	appThread = AppCommuniacteServerThread("AppCommunicateThread")
	appThread.start()
