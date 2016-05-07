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
		self.mode = None
		self.ICL = None

		self.fileName = 'userCommand.csv'
		self.scheduleFile = 'scheduleTasks.csv'
		self.HOST = '209.2.212.58'			# Server host
		self.PORT = 8888					# Server port
		self.SIZE = 1024					# message size
		self.cols_user_command = ['TimeStamp', 'Mode', 'AdjustTempTo', 'ScheduleTime']
		self.cols_schedule = ['ScheduleTime', 'AdjustTempTo']


	def run(self):
		time.sleep(5)
		# Waiting for threads to start
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
		while True:
			# ==================== Status Update ====================
			self.update_current_temp()
			self.update_desire_temp()
			self.update_on_off()
			self.update_humidity()
			self.update_ICL()
			self.update_mode()

			# ==================== Communication ====================
			# The client(socket) is closed everytime a communication ends
			# A new client will be established for each communication
			client, address = s.accept()
			print 'Connection established with ' + str(address)
			message = 
			client.send(message)

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
						# Clear on_off_queue and put new status
						pass

					elif data[0] == 'O':
						# Remote turn off
						# Clear on_off_queue and put new status
						pass

					elif data[0] == 'A':
						# Auto mode
						# Clear mode_queue and put new status
						pass

				else:
					print "Communicate data error"

			client.close()


	def update_current_temp(self):
		if not self.current_temp_queue.empty():
			self.current_temp = self.current_temp_queue.get()
			self.current_temp_queue.put(self.current_temp)
		else:
			print 'Error: current_temp_queue is empty when trying to get'

	def update_desire_temp(self):
		if not self.desire_temp_queue.empty():
			self.desire_temp = self.desire_temp_queue.get()
			self.desire_temp_queue.put(self.desire_temp)
		else:
			print 'Error: desire_temp_queue is empty when trying to get'

	def update_on_off(self):
		if not self.on_off_queue.empty():
			self.on_off = self.on_off_queue.get()
			self.on_off_queue.put(self.on_off)
		else:
			print 'Error: on_off_queue is empty when trying to get'

	def update_humidity(self):
		if not self.humidity_queue.empty():
			self.humidity = self.humidity_queue.get()
			self.humidity_queue.put(self.humidity)
		else:
			print 'Error: humidity_queue is empty when trying to get'

	def update_ICL(self):
		if not self.ICL_queue.empty():
			self.ICL = self.ICL_queue.get()
			self.ICL_queue.put(self.ICL)
		else:
			print 'Error: ICL_queue is empty when trying to get'

	def update_mode(self):
		if not self.mode_queue.empty():
			self.mode = self.mode_queue.get()
			self.mode_queue(self.mode)
		else:
			print 'Error: mode_queue is empty when trying to get'


if __name__ == '__main__':
	appThread = AppCommuniacteServerThread("AppCommunicateThread")
	appThread.daemon = True
	appThread.start()
	try:
		while True:
			time.sleep(10)
	except KeyboardInterrupt:
		exit()
