import socket
import threading
import csv
import time
import datetime
import os
import queue

class AppCommuniacteServerThread(threading.Thread):
	
	def __init__(self, threadName, current_temp_queue, on_off_queue, desire_temp_queue, humidity_queue, ICL_queue, mode_queue):
		threading.Thread.__init__(self)
		self.threadName = threadName

		self.current_temp_queue = current_temp_queue
		self.on_off_queue = on_off_queue
		self.desire_temp_queue = desire_temp_queue
		self.humidity_queue = humidity_queue
		self.ICL_queue = ICL_queue
		self.mode_queue = mode_queue

		self.desire_temp = None
		self.current_temp = None
		self.on_off = None
		self.humidity = None

		self.fileName = 'userCommand.csv'
		self.scheduleFile = 'scheduleTasks.csv'
		self.HOST = '209.2.212.58'			# Server host
		self.PORT = 8888					# Server port
		self.SIZE = 1024					# message size
		self.cols_user_command = ['TimeStamp', 'Mode', 'AdjustTempTo', 'ScheduleTime']
		self.cols_schedule = ['ScheduleTime', 'AdjustTempTo']


	def run(self):
		print "Starting thread:", self.threadName + "..."
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		print 'Socket Created'
		try:
			s.bind((self.HOST, self.PORT))
		except socket.error as msg:
			print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
			print "Have you change the host address?"
			sys.exit()

		print 'Socket bind complete'
		s.listen(5)
		print 'Socket listening ...'

		while 1:
			client, address = s.accept()
			print 'Connection established with ' + str(address)
			client.send("Welcome!")

			data = client.recv(self.SIZE)
			if data:
				# When receving message
				# Retrive data, log data to file, update queue.
				if type(data) is str:
					print "App message received:", data
					# First character in data indicates mode.
					if data[0] == 'M':
						# Manual mode
						self.desire_temp = int(data[1:3])
						print "Execution: set temperature to", self.desire_temp
						commandDict = {'TimeStamp': int(time.time()), 'Mode': 'Manual', 'AdjustTempTo': self.desire_temp}
						with open(self.fileName, 'a') as csvfile:
							writer = csv.DictWriter(csvfile, fieldnames=self.cols_user_command, lineterminator='\n')
							writer.writerow(commandDict)
						print "Logged user command to " + self.fileName

					elif data[0] == 'S':
						# Schedule task
						self.desire_temp = int(data[1:3])
						unixScheduleTime = int(data[3:])
						datetimeTaskTime = datetime.datetime.fromtimestamp(unixScheduleTime).strftime('%Y-%m-%d %H:%M:%S')
						print "Schedule Task @ " + str(datetimeTaskTime) + ", set temperature to", self.desire_temp
						commandDict = {'TimeStamp': int(time.time()), 'Mode': 'Schedule', 'AdjustTempTo': self.desire_temp, 'ScheduleTime': unixScheduleTime}
						with open(self.fileName, 'a') as csvfile:
							writer = csv.DictWriter(csvfile, fieldnames=self.cols_user_command, lineterminator='\n')
							writer.writerow(commandDict)
						print "Logged user command to " + self.fileName

						scheduleDict = {'ScheduleTime': unixScheduleTime, 'AdjustTempTo': self.desire_temp}
						with open(self.scheduleFile, 'a') as csvfile:
							writer = csv.DictWriter(csvfile, fieldnames=self.cols_schedule, lineterminator='\n')
							writer.writerow(commandDict)
						reader = csv.reader(open(self.scheduleFile))
						sortedSchedule = sorted(reader, key=operator.itemgetter(0), reverse=False)
						try:
							os.remove(self.scheduleFile)
						except:
							pass
						with open(self.scheduleFile, 'a') as csvfile:
							writer = csv.DictWriter(csvfile, fieldnames=self.cols_schedule, lineterminator='\n')
							for row in sortedSchedule:
								writer.writerow({'ScheduleTime': row[0], 'AdjustTempTo': row[1]})

					elif data[0] == 'I':
						# Remote turn on
						


					elif data[0] == 'O':
						# Remote turn off


					elif data[0] == 'A':
						# Auto mode
						# Enter auto mode
						pass

				else:
					print "Communicate data error"

			client.close()

if __name__ == '__main__':
	appThread = AppCommuniacteServerThread("AppCommunicateThread")
	appThread.daemon = True
	appThread.start()
	try:
		while True:
			time.sleep(10)
	except KeyboardInterrupt:
		exit()
