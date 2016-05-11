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
import pyupm_i2clcd as lcd
import smart
import mraa

# Pin definition
REDPIN = 4
BLUEPIN = 3

# LCD
myLcd = lcd.Jhd1313m1(0, 0x3E, 0x62)
myLcd.clear()
myLcd.setColor(255, 255, 0)


# Queue defination
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

current_temp_queue.put(25.0)
humidity_queue.put(50)
desire_temp_queue.put(25.0)
on_off_queue.put("ON")
mode_queue.put("M")

# Multithread
motionThread = MotionDetection.MotionThread("MotionThread")
appThread = AppCommunicate.AppCommuniacteServerThread("AppCommunicateThread", current_temp_queue, 
			on_off_queue, desire_temp_queue, humidity_queue, mode_queue, schedule_priority_queue, user_change_queue)
tempThread = Temperature.TemperatureThread("TemperatureThread", current_temp_queue, desire_temp_queue, humidity_queue, feature_queue)
s3Thread = S3Upload.S3Uploader("S3Thread")
scheduleThread = ScheduleTask.ScheduleThread("ScheduleThread", desire_temp_queue, on_off_queue, schedule_priority_queue)
smartThread = smart.ImplementThread("SmartThread", desire_temp_queue, humidity_queue, mode_queue, feature_queue, user_change_queue)

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
		self.auto_off_enable = True

		self.redLED = mraa.Gpio(REDPIN)
		self.blueLED = mraa.Gpio(BLUEPIN)
		self.redLED.dir(mraa.DIR_OUT)
		self.blueLED.dir(mraa.DIR_OUT)

	def run(self):
		time.sleep(3)
		try:
			while True:
				# ==================== Get each status ====================
				self.current_temp = self.get_queue(self.current_temp_queue)
				self.desire_temp = self.get_queue(self.desire_temp_queue)
				self.on_off = self.get_queue(self.on_off_queue)
				self.humidity = self.get_queue(self.humidity_queue)
				self.mode = self.get_queue(self.mode_queue)

				if self.on_off is 'ON' and (motionThread.is_people_in_room() or not self.auto_off_enable):

					# ==================== Execution ====================
					if self.mode is 'M' and self.on_off is 'ON':
						print ''
						print '========== Manual Mode =========='
						print 'Current temperature:', self.current_temp
						print 'Desire temperature:', self.desire_temp

						try:
							if (self.current_temp - self.desire_temp) > 0.5:
								print 'Current temperature too high'
								print ''
								print '***** COOLING *****'
								print ''
								self.set_cool(True)
							else:
								self.set_cool(False)
						except:
							pass
						try:
							if (self.desire_temp - self.current_temp) > 0.5:
								print 'Current temperature too low'
								print ''
								print '***** HEATING *****'
								print ''
								self.set_heat(True)
							else:
								self.set_heat(False)
						except:
							pass

					elif self.mode == 'A' and self.on_off == 'ON':
						print '========== Smart Mode =========='
						print 'Current temperature:', self.current_temp
						print 'Desire temperature:', self.desire_temp

						if (self.current_temp - self.desire_temp) > 0.5:
							print 'Current temperature too high'
							print ''
							print '***** COOLING *****'
							print ''

						elif (self.desire_temp - self.current_temp) > 0.5:
							print 'Current temperature too low'
							print ''
							print '***** HEATING *****'
							print ''

					elif self.on_off == 'OFF':
						print 'Thermostat OFF'

					if self.mode:
						myLcd.setCursor(0,0)
						myLcd.write("MODE: " + self.mode)
					if self.current_temp and self.desire_temp:
						myLcd.setCursor(1,0)
						myLcd.write("CT:" + str(self.current_temp) + "  DT:" + str(self.desire_temp))
					time.sleep(3.1)

				else:
					print "Thermostat: No one in room"
					self.put_queue(self.on_off_queue, "OFF")
					myLcd.clear()
					myLcd.setColor(255, 255, 0)
					myLcd.setCursor(0,0)
					myLcd.write("OFF")
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

	def set_cool(self, value):
		# Do something to cool down
		self.blueLED.write(value)

	def set_heat(self, value):
		# Do something to heat up
		self.redLED.write(value)


if __name__ == '__main__':
	print "System starting..."
	thermostat_ins = thermostat(current_temp_queue, on_off_queue, desire_temp_queue, humidity_queue, mode_queue)
	thermostat_ins.run()
	
