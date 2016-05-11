import socket
import threading
import csv
import time
import datetime
import os
import Queue
import sys

class AppCommuniacteServerThread(threading.Thread):
	
	def __init__(self, threadName, current_temp_queue, on_off_queue, desire_temp_queue, humidity_queue, mode_queue, schedule_priority_queue, user_change_queue):
		threading.Thread.__init__(self)
		self.threadName = threadName

		self.current_temp_queue = current_temp_queue
		self.on_off_queue = on_off_queue
		self.desire_temp_queue = desire_temp_queue
		self.humidity_queue = humidity_queue
		self.mode_queue = mode_queue
		self.schedule_priority_queue = schedule_priority_queue

		self.desire_temp = None
		self.current_temp = None
		self.on_off = None
		self.humidity = None
		self.mode = None

		self.fileName = 'userCommand.csv'
		self.scheduleFile = 'scheduleTasks.csv'
		self.HOST = '209.2.212.89'			# Server host
		self.PORT = 8888					# Server port
		self.SIZE = 1024					# message size
		self.cols_user_command = ['TimeStamp', 'Mode', 'AdjustTempTo', 'ON / OFF', 'ScheduleTime']
		self.cols_schedule = ['ScheduleTime', 'Action']


	def run(self):
		time.sleep(3)
		# Wait for other threads to start first
		print "Starting thread:", self.threadName + "..."
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		print self.threadName + ': Socket Created'
		try:
			s.bind((self.HOST, self.PORT))
		except socket.error as msg:
			print self.threadName + ': Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
			print self.threadName + ": Have you change the host address?"
			sys.exit()

		print self.threadName + ': Socket bind complete'
		s.listen(10)
		print self.threadName + ': Socket listening...'

		while True:
			print self.threadName + ": Waiting for connection..."
			client, address = s.accept()
			print self.threadName + ': Connection established with ' + str(address)

			# ==================== Get each status ====================
			self.current_temp = self.get_queue(self.current_temp_queue)
			self.desire_temp = self.get_queue(self.desire_temp_queue)
			self.on_off = self.get_queue(self.on_off_queue)
			self.humidity = self.get_queue(self.humidity_queue)
			self.mode = self.get_queue(self.mode_queue)

			# ==================== Communication ====================
			# The client(socket) is closed everytime a communication ends
			# A new client will be established for each communication

			if self.on_off is 'ON':
				# current_temp: 25.5	humidity: 70	desire_temp: 26.0
				# message length: 10
				message = str(self.current_temp) + str(self.humidity) + str(self.desire_temp)
			elif self.on_off is 'OFF':
				# message length: 3
				message = "OFF"

			client.send(message + '\r\n')
			print self.threadName + ': Sent message: ' + message

			while True:

				data = client.recv(self.SIZE)
				print self.threadName + ': Received message: ' + data

				if len(data) is not 0:
					# When receving message
					# Retrive data, log data to file, update queue.
					print self.threadName + ": App message received: " + data

					# First character in data indicates mode.
					if data[0] is 'M':
						# Manual mode
						self.desire_temp = float(data[1:5])
						print self.threadName + ": Received new desired temperature of", self.desire_temp
						commandDict = {'TimeStamp': int(time.time()), 'Mode': 'Manual', 'AdjustTempTo': self.desire_temp}
						with open(self.fileName, 'a') as csvfile:
							writer = csv.DictWriter(csvfile, fieldnames=self.cols_user_command, lineterminator='\n')
							writer.writerow(commandDict)
						print self.threadName + ": Logged user command to " + self.fileName

						# Put desire_temp into queue
						self.desire_temp_queue.get()
						self.desire_temp_queue.put(self.desire_temp)

					elif data[0] is 'S':
						if data[1] is 'O' or 'C':
							# Schedule on / off
							if data[1] is 'O':
								schedule_on_off = 'ON'
							else:
								schedule_on_off = 'OFF'
							unixScheduleTime = int(data[3:14])
							commandDict = {
											'TimeStamp': int(time.time()),
											'Mode': 'Schedule',
											'ON / OFF': schedule_on_off,
											'ScheduleTime': unixScheduleTime
											}
							datetimeTaskTime = datetime.datetime.fromtimestamp(unixScheduleTime).strftime('%Y-%m-%d %H:%M:%S')
							print self.threadName + ": Schedule Task @ " + str(datetimeTaskTime) + ", trun on or off:", schedule_on_off

							scheduleDict = {
											'ScheduleTime': unixScheduleTime,
											'Action': schedule_on_off
											}
							# Put schedule tasks into priority queue
							schedule_priority_queue.put((unixScheduleTime, schedule_on_off))

						else:
							# Schedule temperature adjust
							# Get parameters from data
							schedule_desire_temp = float(data[1:5])
							unixScheduleTime = int(data[5:16])

							# Put parameters in a dict and write to userCommand.csv
							commandDict = {
											'TimeStamp': int(time.time()),
											'Mode': 'Schedule',
											'AdjustTempTo': schedule_desire_temp,
											'ScheduleTime': unixScheduleTime
											}
							datetimeTaskTime = datetime.datetime.fromtimestamp(unixScheduleTime).strftime('%Y-%m-%d %H:%M:%S')
							print self.threadName + ": Schedule Task @ " + str(datetimeTaskTime) + ", set temperature to", schedule_desire_temp

							# Put schedule tasks in a dict, write to scheduleTasks.csv
							scheduleDict = {
											'ScheduleTime': unixScheduleTime,
											'Action': schedule_desire_temp
											}
							# Put schedule tasks into priority queue
							schedule_priority_queue.put((unixScheduleTime, schedule_desire_temp))

						with open(self.scheduleFile, 'a') as csvfile:
							writer = csv.DictWriter(csvfile, fieldnames=self.cols_schedule, lineterminator='\n')
							writer.writerow(commandDict)

						with open(self.fileName, 'a') as csvfile:
							writer = csv.DictWriter(csvfile, fieldnames=self.cols_user_command, lineterminator='\n')
							writer.writerow(commandDict)
						print self.threadName + ": Logged user command to " + self.fileName

					elif data[0] is 'O':
						# Remote turn on
						# Clear on_off_queue and put new status
						self.put_queue(self.on_off_queue, 'ON')

					elif data[0] is 'C':
						# Remote turn off
						# Clear on_off_queue and put new status
						self.put_queue(self.on_off_queue, 'OFF')

					elif data[0] is 'A':
						# Auto mode
						# Clear mode_queue and put new status
						self.put_queue(self.mode_queue, 'A')

					elif data[0] is 'R':
						# Update and resend status
						# ==================== Get each status ====================
						self.current_temp = self.get_queue(self.current_temp_queue)
						self.desire_temp = self.get_queue(self.desire_temp_queue)
						self.on_off = self.get_queue(self.on_off_queue)
						self.humidity = self.get_queue(self.humidity_queue)
						self.mode = self.get_queue(self.mode_queue)
						
						message = str(self.current_temp) + str(self.humidity) + str(self.desire_temp)
						client.send(message + '\r\n')
						print self.threadName + ': Sent message: ' + message

				else:
					# If data length is 0
					break

			# Each time an inner loop ends:
			print self.threadName + ": Socket closed"
			client.close()


	def get_queue(self, queue):
		if not queue.empty():
			data = queue.get()
			queue.put(data)
			return data
		else:
			print 'Error: queue is empty when trying to get, waiting to re-get'
			time.sleep(0.5)
			self.get_queue(queue)

	def put_queue(self, queue, data):
		while not queue.empty():
			queue.get()
		queue.put(data)


if __name__ == '__main__':
	current_temp_queue = Queue.Queue()
	on_off_queue = Queue.Queue()
	desire_temp_queue = Queue.Queue()
	humidity_queue = Queue.Queue()
	mode_queue = Queue.Queue()

	schedule_priority_queue = Queue.PriorityQueue()
	user_change_queue = Queue.Queue()

	current_temp_queue.put(float(55.5))
	on_off_queue.put("ON")
	desire_temp_queue.put(float(46.5))
	humidity_queue.put(int(50))
	mode_queue.put("M")

	appThread = AppCommuniacteServerThread("AppCommunicateThread", 
		current_temp_queue, on_off_queue, desire_temp_queue, humidity_queue, mode_queue, schedule_priority_queue, user_change_queue)
	appThread.daemon = True
	appThread.start()
	try:
		while True:
			time.sleep(10)
			current_temp_queue.put(float(15.5))
			on_off_queue.put("ON")
			desire_temp_queue.put(float(86.5))
			humidity_queue.put(int(99))
			mode_queue.put("M")
	except KeyboardInterrupt:
		sys.exit()
