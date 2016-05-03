import mraa
import time
import threading

roomSensorPin = 8

class RoomSensorThread(threading.Thread):
	def __init__(self, threadName):
		threading.Thread.__init__(self)
		self.threadName = threadName
		self.timer = 0
		self.room_seneor = mraa.Gpio(roomSensorPin)
		self.room_seneor.dir(mraa.DIR_IN)
		self.room_sensor_result = False

	def run(self):
		print "Starting thread:", self.threadName + "..."
		marker = 1
		try:
			while (1):
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

		except KeyboardInterrupt:
			exit(1)

	def get_room_sensor_result(self):
		return self.room_sensor_result


if __name__ == '__main__':

	roomSensorThread = threading.Thread(target=room_sensor_thread)
	doorSensorThread = threading.Thread(target=door_sensor_thread)
	roomSensorThread.daemon = True
	doorSensorThread.daemon = True
	roomSensorThread.start()
	doorSensorThread.start()

	try:
		while(1):
			print is_people_in_room()
			time.sleep(0.1)
	except KeyboardInterrupt:
		exit