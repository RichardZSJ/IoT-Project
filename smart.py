import Queue
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
from numpy.linalg import inv
from math import exp

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


#USER_TEMP = 25
ICL = "B"
#RH = 0.5

tempSensorPin = 1
fileName = 'environmentData.csv'
cols = ['response', '1', 'RH', 'T0', 'T1', 'T2', 'outdoor_temp', 'outdoor_humidity', 'w0', 'w1', 'w2']


def train():
	print 'training!'
	lam = 1.0
	DATA = []
	with open('environmentData.csv', 'r') as csvfile:
		reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
		for row in reader: 
			DATA.append(list(eval(row[0])))
	DATA = np.matrix(DATA)
	y = DATA[:,0]
	X = DATA[:,1:]
	#X = np.concatenate((np.matrix([1 for i in range(X.shape[0])]),X.T)).T
	tmp = inv(np.dot(X.T, X) + lam * np.identity(X.shape[1]))
	coef = tmp.dot(X.T).dot(y)
	return coef



class ImplementThread(threading.Thread):
	def __init__(self, threadName, desire_temp_queue, humidity_queue, mode_queue, feature_queue, user_change_queue):
		threading.Thread.__init__(self)
		self.starttime = int(time.time())
		self.trainFlag = True
		self.w = 1.0
		self.desire_temp_queue = desire_temp_queue
		self.humidity_queue = humidity_queue
		self.mode_queue = mode_queue
		self.feature_queue = feature_queue
		self.user_change_queue = user_change_queue

	def run(self):
		while 1:
			#READ sMODE from que
			MODE = get_queue(self.mode_queue)
			#if int(time.time()) - self.starttime <= 604800:
			if int(time.time()) - self.starttime <= 5:
				print 'waiting!'
				#time.sleep(100)
				time.sleep(1)
			elif MODE is not "S":
				time.sleep(1)
			else:
				self.w = exp(2.0*(int(time.time()) - self.starttime)/604800.0)
				print self.w
				if self.trainFlag == True:
					self.coef = train()
					self.trainFlag = False
				#Retrieve features from que
				data = get_queue(self.feature_queue)
				data = np.matrix(data)
				delta = self.coef.dot(data)[0,0]
				ta = temp2(ICL, data[0,1]).solve()
				prediction = delta + ta
				#Read desired_temp from que(desired_temp)
				desired_temp = get_queue(self.desire_temp_queue)
				if abs(prediction - desired_temp) >= 1.0:
					#SET desired_temp as prediction
					put_queue(self.desire_temp_queue, prediction)
				#READ user change signal(SIGNAL) from que:
				if not self.user_change_queue.empty():
					self.user_change_queue.get()
					#Read desired_temp from que(desired_temp)
					tempDict = {'response':(desired_temp - ta)*self.w, '1':1.0*self.w, 'RH':data[0,1]*self.w, 'T0':data[0,2]*self.w,'T1':data[0,3]*self.w,'T2':data[0,4]*self.w, 'outdoor_temp':data[0,5]*self.w, 'outdoor_humidity':data[0,6]*self.w, 'w0':data[0,7]*self.w, 'w1':data[0,8]*self.w, 'w2':data[0,9]*self.w}
					with open(fileName, 'a') as csvfile:
						writer = csv.DictWriter(csvfile, fieldnames = cols)
						writer.writerow(tempDict)
						self.trainFlag = True

				time.sleep(5)



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
	return current_temp

def get_room_humidity():
	pass


if __name__ == '__main__':
        current_temp_queue = Queue.Queue()
        on_off_queue = Queue.Queue()
        desire_temp_queue = Queue.Queue()
        humidity_queue = Queue.Queue()
        mode_queue = Queue.Queue()
	feature_queue = Queue.Queue()
	user_change_queue = Queue.Queue()

        current_temp_queue.put(float(25.5))
        on_off_queue.put("ON")
        desire_temp_queue.put(float(26.5))
        humidity_queue.put(int(70))
        mode_queue.put("S")
	feature_queue.put([1.0,0.3,1,0,0,24.0,30, 0,1,0])
	user_change_queue.put(False)

	implementThread = ImplementThread('implementThread', desire_temp_queue, humidity_queue, mode_queue, feature_queue, user_change_queue)
	implementThread.daemon = True
	implementThread.start()
	try:
		while 1:
			pass
	except KeyboardInterrupt:
		exit()
