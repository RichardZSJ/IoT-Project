import Queue
import mraa
import time
import datetime
from math import log
import threading
import CityWeather
import csv
import cmath
import math
from math import sqrt
from math import pow
from sympy.solvers import solve
from sympy import Symbol
import random
import numpy as np
#from sklearn.linear_model import Ridge
#import matplotlib.pyplot as plt
from numpy.linalg import inv
from math import exp


#USER_TEMP = 25
ICL = "B"
RH = 0.5

tempSensorPin = 1
fileName = 'environmentData.csv'
cols = ['response', '1', 'RH', 'T0', 'T1', 'T2', 'outdoor_temp', 'outdoor_humidity', 'w0', 'w1', 'w2']
Icl_table = {"A":0.96, "B":0.726, "C":1.089}


#set Tr = Tcl
class temp2():
	def __init__(self, Icl, Rh):
		self.E = 2.718
		self.Icl = Icl_table[Icl]
		self.fcl = 1.025 + 0.15 * Icl_table[Icl]
		self.M = 115.0
		self.Rh = Rh
		self.Rcl = Icl_table[Icl] * 0.155
		self.tr = 22.0
		self.V = 0.11
		self.hc = 12.1*sqrt(self.V)
		self.W = 0.0
	def solve(self):
		self.A = 35.7 - 0.0275*(self.M - self.W) - self.Rcl * ((self.M - self.W) - 3.05 * (5.73 - 0.007 * (self.M - self.W) - 2.96*self.Rh) - 0.42 * ((self.M - self.W) - 58.15) - 0.0173*self.M*(5.87 - 2.96*self.Rh) - 0.0476 * self.M)
		self.B = 0.0014 * self.M * self.Rcl
		self.C = (self.M - self.W) - self.fcl * self.hc * self.A - 3.05*(5.73 - 0.007*(self.M - self.W) - 2.96*self.Rh) - 0.42*(self.M - self.W - 58.15) - 0.0173*self.M*(5.87-self.Rh) - 34*0.0014*self.M
		self.ta = -self.C/(0.0015*self.M + self.fcl*self.hc*(self.B+1))
		return self.ta


class TemperatureThread(threading.Thread):
	def __init__(self, threadName, current_temp_queue, desire_temp_queue, humidity_queue, feature_queue):
		threading.Thread.__init__(self)
		self.threadName = threadName
		self.tempDict = {}
		self.starttime = int(time.time())
		self.current_temp_queue = current_temp_queue
		self.desire_temp_queue = desire_temp_queue
		self.humidity_queue = humidity_queue
		self.feature_queue = feature_queue

	def run(self):
		while 1:
			current_temp = get_room_temp()
			humidity = get_room_humidity()
			#WRITE current_temp into que
			put_queue(self.current_temp_queue, current_temp)
			put_queue(self.humidity_queue, humidity)

			ta = temp2(ICL, RH).solve()
			#Read desired temp from que(desired_temp)
			desired_temp = get_queue(self.desire_temp_queue)
			response = desired_temp - ta
			self.tempDict['response'] = response
			self.tempDict['1'] = 1.0
			self.tempDict['RH'] = RH

			now = datetime.datetime.now()
			if (now.hour in range(0,5)):
				T0,T1,T2 = 1,0,0
			if (now.hour in range(6,11)):
				T0,T1,T2 = 0,1,0
			if (now.hour in range(12,17)):
				T0,T1,T2 = 0,0,1
			if (now.hour in range(18,23)):
				T0,T1,T2 = 0,0,0
			self.tempDict['T0'], self.tempDict['T1'], self.tempDict['T2'] = T0, T1, T2

			cityWeather = CityWeather.get_weather('New York')					
			self.tempDict['outdoor_temp'] = int(cityWeather['temperature']['temp'])
			self.tempDict['outdoor_humidity'] = float(cityWeather['humidity']) * 0.01
			status = cityWeather['status']
			if status == 'Clear':
				w0,w1,w2 = 1,0,0
			elif status == 'Clouds':
				w0,w1,w2 = 0,1,0
			elif status == 'Rain':
				w0,w1,w2 = 0,0,1
			else:
				w0,w1,w2 = 0,0,0
			self.tempDict['w0'], self.tempDict['w1'], self.tempDict['w2'] = w0, w1, w2

			#if int(time.time()) - self.starttime <= 604800:
			if int(time.time()) - self.starttime <= 10:
				with open(fileName, 'a') as csvfile:
					writer = csv.DictWriter(csvfile, fieldnames = cols)
					writer.writerow(self.tempDict)
			else:
				features = [1.0, RH, T0, T1, T2, self.tempDict['outdoor_temp'], self.tempDict['outdoor_humidity'], w0, w1, w2]
				#WRITE features to a que
				put_queue(self.feature_queue, features)
			#time.sleep(5)
			time.sleep(1)


def get_queue(queue):
	if not queue.empty():
		data = queue.get()
		queue.put(data)
		return data
	else:
		print 'Error: queue is empty when trying to get, waiting to re-get'
		time.sleep(0.5)
		get_queue(queue)

def put_queue(queue, data):
	print "PUT!"
	while not queue.empty():
		queue.get()
	queue.put(data)

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
	return round(current_temp, 1)

def get_room_humidity():
	pass

if __name__ == '__main__':
        current_temp_queue = Queue.Queue()
        desire_temp_queue = Queue.Queue()
        humidity_queue = Queue.Queue()
	feature_queue = Queue.Queue()	

        current_temp_queue.put(float(25.5))
        desire_temp_queue.put(float(26.5))
        humidity_queue.put(int(70))
	#feature_queque.put()
	
	tempThread = TemperatureThread('tempThread', current_temp_queue, desire_temp_queue, humidity_queue, feature_queue)
	tempThread.daemon = True
	tempThread.start()
	try:
		while 1:
			pass
	except KeyboardInterrupt:
		exit()
