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
		marker = 1
		try:
			while True:
				if (self.room_seneor.read()):
					print "room_seneor high"
					self.room_sensor_result = True
					# Calibrate door sensor result
					# door_sensor_result = True
					print 'People in room', marker
					marker += 1
					self.timer = 0
					time.sleep(0.1)
				else:
					print "room_seneor low"
					self.timer += 1
					time.sleep(1)
					print 'Timer:', self.timer
					if (self.timer > 30):
						self.room_sensor_result = False

				if (self.door_seneor.read()):
					print "door_seneor high"
					# Wait until the sensor become low
					while (self.door_seneor.read()):
						pass
					# Flip the flag
					self.door_sensor_result = not self.door_sensor_result

		except KeyboardInterrupt:
			exit(1)

	def get_room_sensor_result(self):
		return self.room_sensor_result

	def get_door_sensor_result(self):
		return self.door_sensor_result

	def is_people_in_room(self):
		return (self.door_sensor_result or self.room_sensor_result)


if __name__ == '__main__':
	motionThread = MotionThread("MotionThread")
	motionThread.daemon = True
	motionThread.start()
	try:
		while(1):
			print motionThread.is_people_in_room()
			time.sleep(1)
	except KeyboardInterrupt:
		exit