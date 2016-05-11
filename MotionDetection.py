import mraa
import time
import threading

roomSensorPin = 8
doorSensorPin = 7

class MotionThread(threading.Thread):
	def __init__(self, threadName):
		threading.Thread.__init__(self)
		self.threadName = threadName

		self.timer = 0
		self.room_seneor = mraa.Gpio(roomSensorPin)
		self.room_seneor.dir(mraa.DIR_IN)
		self.room_sensor_result = False

		self.door_seneor = mraa.Gpio(doorSensorPin)
		self.door_seneor.dir(mraa.DIR_IN)
		self.door_sensor_result = False

	def run(self):
		print "Starting thread:", self.threadName + "..."
		try:
			while True:
				if (self.room_seneor.read()):
					self.room_sensor_result = True
					# Calibrate door sensor result
					self.door_sensor_result = True
					self.timer = 0
				else:
					self.timer += 1
					if (self.timer > 5):
						self.room_sensor_result = False

				if (self.door_seneor.read()):
					# Flip the flag
					self.door_sensor_result = (not self.door_sensor_result)

					# Wait until the sensor become low
					while (self.door_seneor.read()):
						pass

				print self.threadName + ': People in room:', self.is_people_in_room()
				print self.threadName + ': Door:', self.get_door_sensor_result()
				time.sleep(3)

		except KeyboardInterrupt:
			exit(1)

	def is_people_in_room(self):
		return (self.door_sensor_result or self.room_sensor_result)

	def get_room_sensor_result(self):
		return self.room_sensor_result

	def get_door_sensor_result(self):
		return self.door_sensor_result

if __name__ == '__main__':
	motionThread = MotionThread("MotionThread")
	motionThread.daemon = True
	motionThread.start()
	try:
		while(1):
			print "Room sensor:", motionThread.get_room_sensor_result()
			print "Door sensor:", motionThread.get_door_sensor_result()
			time.sleep(1)
	except KeyboardInterrupt:
		exit