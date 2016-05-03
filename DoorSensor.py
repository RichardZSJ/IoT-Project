import mraa
import time
import threading

doorSensorPin = 7

class DoorSensorThread(threading.Thread):
	def __init__(self, threadName):
		threading.Thread.__init__(self)
		self.threadName = threadName
		self.door_seneor = mraa.Gpio(doorSensorPin)
		self.door_seneor.dir(mraa.DIR_IN)
		self.door_sensor_result = False

	def run(self):
		print "Starting thread:", self.threadName + "..."
		try:
			while (1):
				if (self.door_seneor.read()):
					print "door_seneor high"
					# Wait until the sensor become low
					while (self.door_seneor.read()):
						pass
					# Flip the flag
					self.door_sensor_result = not self.door_sensor_result

		except KeyboardInterrupt:
			exit

	def get_door_sensor_result(self):
		return self.door_sensor_result