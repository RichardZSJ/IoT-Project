import time
import sys
import threading
import RoomSensor
import DoorSensor
import AppCommunicate
import CityWeather
import Temperature
import S3Upload

def is_people_in_room():
	return (roomSensorThread.get_room_sensor_result() or doorSensorThread.get_door_sensor_result())

# Main thread
def mainThread():
	try:
		while 1:
			print "People in room:", is_people_in_room()
			print "Room temperature:", RoomSensor.get_room_temp()
			time.sleep(1)
	except KeyboardInterrupt:
		exit(1)

class auto_on_off_thread(threading.Thread):
	

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

	mainThread()
	