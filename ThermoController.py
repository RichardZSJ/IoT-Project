import time
import sys
import threading
import MotionDetection
import AppCommunicate
import CityWeather
import Temperature
import S3Upload
import Queue
import ScheduleTask
import csv

# Pin definition
REDPIN = 4
BLUEPIN = 3

# Signal defination
current_temp_queue = Queue.Queue(0)
humidity_queue = Queue.Queue(0)
desire_temp_queue = Queue.Queue(0)
on_off_queue = Queue.Queue(0)
mode_queue = Queue.Queue(0)
user_change_queue = Queue.Queue(0)

# Feature queue
feature_queue = Queue.Queue(0)

# Priority Queue for schedule tasks
schedule_priority_queue = Queue.PriorityQueue(0)

# Multithread
motionThread = MotionDetection.MotionThread("MotionThread")
appThread = AppCommunicate.AppCommuniacteServerThread("AppCommunicateThread", current_temp_queue, 
			on_off_queue, desire_temp_queue, humidity_queue, mode_queue, schedule_priority_queue)
tempThread = Temperature.TemperatureThread("TemperatureThread")
s3Thread = S3Upload.S3Uploader("S3Thread")
scheduleThread = ScheduleTask.ScheduleThread("ScheduleThread", desire_temp_queue, on_off_queue, schedule_priority_queue)

motionThread.daemon = True
appThread.daemon = True
tempThread.daemon = True
s3Thread.daemon = True

motionThread.start()
appThread.start()
tempThread.start()
s3Thread.start()

class thermostat():
	def __init__(self, current_temp_queue, on_off_queue, desire_temp_queue, humidity_queue, mode_queue):
		self.current_temp_queue = current_temp_queue
		self.on_off_queue = on_off_queue
		self.desire_temp_queue = desire_temp_queue
		self.humidity_queue = humidity_queue
		self.mode_queue = mode_queue

		self.current_temp = None
		self.on_off = 'ON'
		self.desire_temp = None
		self.humidity = None
		self.mode = "M"
		self.not_auto_off_flag = True

		self.redLED = mraa.Gpio(REDPIN)
		self.blueLED = mraa.Gpio(BLUEPIN)
		self.redLED.dir(mraa.DIR_OUT)
		self.blueLED.dir(mraa.DIR_OUT)

	def run(self):
		try:
			while True:
				if self.on_off is 'ON' and (motionThread.is_people_in_room() or self.not_auto_off_flag):
					# ==================== Get each status ====================
					self.current_temp = self.get_queue(self.current_temp_queue)
					self.desire_temp = self.get_queue(self.desire_temp_queue)
					self.on_off = self.get_queue(self.on_off_queue)
					self.humidity = self.get_queue(self.humidity_queue)
					self.mode = self.get_queue(self.mode_queue)

					# ==================== Execution ====================
					if self.mode is 'M' and self.on_off is 'ON':
						print '========== Manual Mode =========='
						print 'Current temperature:', self.current_temp
						print 'Desire temperature:', self.desire_temp

						if (self.current_temp - self.desire_temp) > 0.5:
							print 'Current temperature too high'
							print '***** COOLING *****'
							self.cool_on()

						elif (self.desire_temp - self.current_temp) > 0.5:
							print 'Current temperature too low'
							print '***** HEATING *****'
							self.heat_on()

						else:
							print 'Current temperature matches desire temperature'
							# Stop

					elif self.mode == 'A' and self.on_off == 'ON':
						print '========== Smart Mode =========='
						print 'Current temperature:', self.current_temp
						print 'Desire temperature:', self.desire_temp

						if (self.current_temp - self.desire_temp) > 0.5:
							print 'Current temperature too high'
							print '***** COOLING *****'

						elif (self.desire_temp - self.current_temp) > 0.5:
							print 'Current temperature too low'
							print '***** HEATING *****'

					elif self.on_off == 'OFF':
						print 'Thermostat OFF'

					time.sleep(10)

				else:
					print "Thermostat: No one in room"
					self.put_queue(self.on_off_queue, "OFF")
					time.sleep(1)

		except KeyboardInterrupt:
			exit(1)


	def get_queue(self, queue):
		if not queue.empty():
			data = queue.get()
			queue.put(data)
			return data
		else:
			print 'Error: queue is empty when trying to get'

	def put_queue(self, queue, data):
		while not queue.empty():
			queue.get()
		queue.put(data)

	def cool_on(self):
		# Do something to cool down
		self.blueLED.write(True)

	def heat_on(self):
		# Do something to heat up
		self.redLED.write(True)

	def no_operation(self):
		# Stop cooling and heating
		self.blueLED.write(False)
		self.redLED.write(False)

if __name__ == '__main__':
	print "System starting..."
	thermostat_ins = thermostat(current_temp_queue, on_off_queue, desire_temp_queue, humidity_queue, mode_queue)
	thermostat_ins.run()
	
