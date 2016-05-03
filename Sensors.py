import mraa
import time
from math import log
import threading

roomSensorPin = 8
tempSensorPin = 1

class RoomSensorThread(threading.Thread):
	def __init__(self, threadName):
		threading.Thread.__init__(self)
		self.threadName = threadName
		self.timer = 0
		self.room_seneor = mraa.Gpio(roomSensorPin)
		self.room_seneor.dir(mraa.DIR_IN)
		self.room_sensor_result = False

	def run(self):
		print "Starting thread:", self.threadName, "..."
		marker = 1
		try:
			while (1):
				if (room_seneor.read()):
					print "room_seneor high"
					room_sensor_result = True
					# Calibrate door sensor result
					door_sensor_result = True
					print 'People in room', marker
					marker += 1
					timer = 0
					time.sleep(0.1)
				else:
					print "room_seneor low"
					timer += 1
					time.sleep(1)
					print 'Timer:', timer
					if (timer > 30):
						room_sensor_result = False

		except KeyboardInterrupt:
			exit

	def get_room_sensor_result():
		return room_sensor_result


def get_room_temp(self):
	temp_sensor = mraa.Aio(tempSensorPin)
	v = tempSensor.read()
	vcc = 1023.0
	R_1 = 100000.0
	R_0 = 100000.0
	r = (vcc * R_1 - v * R_1)/float(v)
	T_0 = 298.15
	B = 4275.0
	current_temp = 1.0/(1/T_0 + log(r/R_0)/B) - 273.15
	return current_temp


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