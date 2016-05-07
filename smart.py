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
import time
import datetime
from math import log
import threading
import CityWeather
import csv


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


USER_TEMP = 25
ICL = "A"
RH = 0.7

tempSensorPin = 1
fileName = 'environmentData.csv'
#cols = ['timestamp', 'room_temp', 'room_humidity', 'outdoor_temp', 'outdoor_humidity']
cols = ['response', 'RH', 'T0', 'T1', 'T2', 'outdoor_temp', 'outdoor_humidity', 'w0', 'w1', 'w2']


def train():
	DATA = []
	with open('environmentData.csv', 'rb') as csvfile:
		reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
		for row in reader: 
			DATA.append(eval(row[0]))
	DATA = np.matrix(DATA)
	y = DATA[:,0]
	X = DATA[:,1:]
	return (y, X)


class TemperatureThread(threading.Thread):
	def __init__(self, threadName):
		threading.Thread.__init__(self)
		self.threadName = threadName
		self.tempDict = {}

	def run(self):
		while 1:
			ta = temp2(ICL, RH).solve()
			response = USER_TEMP - ta
			self.tempDict['response'] = response
			#self.tempDict['ICL'] = ICL
			self.tempDict['RH'] = RH

			now = datetime.datetime.now()
			if (now.hour in range(0,5)):
				#self.tempDict['timestamp'] = '0-6'
				T0,T1,T2 = 1,0,0
			if (now.hour in range(6,11)):
				#self.tempDict['timestamp'] = '6-12'
				T0,T1,T2 = 0,1,0
			if (now.hour in range(12,17)):
				#self.tempDict['timestamp'] = '12-18'
				T0,T1,T2 = 0,0,1
			if (now.hour in range(18,23)):
				#self.tempDict['timestamp'] = '18-24'
				T0,T1,T2 = 0,0,0
			self.tempDict['T0'], self.tempDict['T1'], self.tempDict['T2'] = T0, T1, T2

			cityWeather = CityWeather.get_weather('New York')					
			#self.tempDict['room_temp'] = int(get_room_temp())
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
