import time
import sys
import threading
import MotionDetection
import AppCommunicate
import CityWeather
import Temperature
import S3Upload
import Queue


# Signal defination
current_temp_queue = Queue.Queue()
humidity_queue = Queue.Queue()
desire_temp_queue = Queue.Queue()
on_off_queue = Queue.Queue()
mode_queue = Queue.Queue()

# Multithread
motionThread = MotionDetection.MotionThread("MotionThread")
appThread = AppCommunicate.AppCommuniacteServerThread("AppCommunicateThread", current_temp_queue, on_off_queue, desire_temp_queue, humidity_queue, mode_queue)
tempThread = Temperature.TemperatureThread("TemperatureThread")
s3Thread = S3Upload.S3Uploader("S3Thread")

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
		self.mode = "MANUAL"
		self.not_auto_off_flag = True

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
		pass

	def heat_on(self):
		# Do something to heat up
		pass

	def no_operation(self):
		# Stop cooling and heating
		pass

if __name__ == '__main__':

	thermostat_ins = thermostat(current_temp_queue, on_off_queue, desire_temp_queue, humidity_queue, mode_queue)
	thermostat_ins.run()
	
