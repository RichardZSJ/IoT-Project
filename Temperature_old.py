import mraa
import time
import datetime
from math import log
import threading
import CityWeather
import csv

tempSensorPin = 1
fileName = 'environmentData.csv'
cols = ['timestamp', 'room_temp', 'room_humidity', 'outdoor_temp', 'outdoor_humidity']

class TemperatureThread(threading.Thread):
	def __init__(self, threadName):
		threading.Thread.__init__(self)
		self.threadName = threadName
		self.tempDict = {}

	def run(self):
		while 1:
			now = datetime.datetime.now()
			if (now.hour in range(0,5)):
				self.tempDict['timestamp'] = '0-6'
			if (now.hour in range(6,11)):
				self.tempDict['timestamp'] = '6-12'
			if (now.hour in range(12,17)):
				self.tempDict['timestamp'] = '12-18'
			if (now.hour in range(18,23)):
				self.tempDict['timestamp'] = '18-24'

			cityWeather = CityWeather.get_weather('New York')
			self.tempDict['room_temp'] = int(get_room_temp())
			self.tempDict['outdoor_temp'] = int(cityWeather['temperature']['temp'])
			self.tempDict['outdoor_humidity'] = int(cityWeather['humidity'])
			# print self.tempDict
			with open(fileName, 'a') as csvfile:
				writer = csv.DictWriter(csvfile, fieldnames = cols)
				writer.writerow(self.tempDict)
			time.sleep(5)

def get_room_temp():
	tempSensor = mraa.Aio(tempSensorPin)
	v = tempSensor.read()
	vcc = 1023.0
	R_1 = 100000.0
	R_0 = 100000.0
	r = (vcc * R_1 - v * R_1)/float(v)
	T_0 = 298.15
	B = 4275.0
	current_temp = 1.0/(1/T_0 + log(r/R_0)/B) - 273.15
	return current_temp

def get_room_humidity():
	pass

if __name__ == '__main__':
	tempThread = TemperatureThread('tempThread')
	tempThread.daemon = True
	tempThread.start()
	try:
		while 1:
			pass
	except KeyboardInterrupt:
		exit()
