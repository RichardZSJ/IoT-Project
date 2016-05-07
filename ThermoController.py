import time
import sys
import threading
import RoomSensor
import DoorSensor
import AppCommunicate
import CityWeather
import Temperature
import S3Upload
import Queue


# Signal defination
current_temp_queue = Queue.Queue()
relative_humidity_queue = Queue.Queue()
desire_temp_queue = Queue.Queue()
on_off_queue = Queue.Queue()
mode_queue = Queue.Queue()
ICL_queue = Queue.Queue()


def is_people_in_room():
	return (roomSensorThread.get_room_sensor_result() or doorSensorThread.get_door_sensor_result())


class thermostat():
	def __init__(self, current_temp_queue, on_off_queue, desire_temp_queue, relative_humidity_queue, ICL_queue, mode_queue):
		self.current_temp_queue = current_temp_queue
		self.on_off_queue = on_off_queue
		self.desire_temp_queue = desire_temp_queue
		self.relative_humidity_queue = relative_humidity_queue
		self.ICL_queue = ICL_queue
		self.mode_queue = mode_queue

	def run():
		try:
			while 1:
				print "People in room:", is_people_in_room()
				print "Room temperature:", RoomSensor.get_room_temp()
				time.sleep(1)
		except KeyboardInterrupt:
			exit(1)

	def turn_on(self):
		self.on_off = True

	def turn_off(self):
		self.on_off = False

	def set_desire_temp(desire_temp):
		self.desire_temp = desire_temp

	def set_mode(mode):
		self.mode = mode


if __name__ == '__main__':
	# Multithread
	roomSensorThread = RoomSensor.RoomSensorThread("RoomSensorThread")
	doorSensorThread = DoorSensor.DoorSensorThread("DoorSensorThread")
	appThread = AppCommunicate.AppCommuniacteServerThread("AppCommunicateThread")
	tempThread = Temperature.TemperatureThread("TemperatureThread")
	s3Thread = S3Upload.S3Uploader("S3Thread")

	roomSensorThread.daemon = True
	doorSensorThread.daemon = True
	appThread.daemon = True
	tempThread.daemon = True
	s3Thread.daemon = True

	roomSensorThread.start()
	doorSensorThread.start()
	appThread.start()
	tempThread.start()
	s3Thread.start()

	thermostat_ins = thermostat(current_temp_queue, on_off_queue, desire_temp_queue, relative_humidity_queue, ICL_queue, mode_queue)
	thermostat_ins.run()
	
