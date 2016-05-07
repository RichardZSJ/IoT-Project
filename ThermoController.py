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
ICL_queue = Queue.Queue()


class thermostat():
	def __init__(self, current_temp_queue, on_off_queue, desire_temp_queue, humidity_queue, ICL_queue, mode_queue):
		self.current_temp_queue = current_temp_queue
		self.on_off_queue = on_off_queue
		self.desire_temp_queue = desire_temp_queue
		self.humidity_queue = humidity_queue
		self.ICL_queue = ICL_queue
		self.mode_queue = mode_queue

		self.current_temp = None
		self.on_off = None
		self.desire_temp = None
		self.humidity = None
		self.ICL = None
		self.mode = "M"

	def run():
		try:
			while True:
				# ==================== Status Update ====================
				self.update_current_temp()
				self.update_desire_temp()
				self.update_on_off()
				self.update_humidity()
				self.update_ICL()
				self.update_mode()

				# ==================== Execution ====================
				print "People in room:", is_people_in_room()
				print "Room temperature:", RoomSensor.get_room_temp()

				if self.mode == 'M' and self.on_off == 'ON':
					print '========== Manual Mode =========='
					print 'Current temperature:', self.current_temp
					print 'Desire temperature:', self.desire_temp

					if (self.current_temp - self.desire_temp) > 0.5:
						print 'Current temperature too high'
						print '***** COOLING *****'

					elif (self.desire_temp - self.current_temp) > 0.5:
						print 'Current temperature too low'
						print '***** HEATING *****'

					else:
						print 'Current temperature matches desire temperature'

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
		except KeyboardInterrupt:
			exit(1)


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
	# Multithread
	motionThread = MotionDetection.MotionThread("MotionThread")
	appThread = AppCommunicate.AppCommuniacteServerThread("AppCommunicateThread")
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

	thermostat_ins = thermostat(current_temp_queue, on_off_queue, desire_temp_queue, humidity_queue, ICL_queue, mode_queue)
	thermostat_ins.run()
	
