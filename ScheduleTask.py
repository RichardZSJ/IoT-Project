import time
import threading

class ScheduleThread(threading.Thread):
	def __init__(self, threadName, desire_temp_queue, on_off_queue, schedule_priority_queue):
		threading.Thread.__init__(self)
		self.threadName = threadName
		self.desire_temp_queue = desire_temp_queue
		self.on_off_queue = on_off_queue
		self.schedule_priority_queue = schedule_priority_queue

		# Read scheduleTasks.csv and put all incoming schedule tasks into schedule_priority_queue
		with open('scheduleTasks.csv', 'rb') as f:
			reader = csv.reader(f)
			for row in reader:
				if int(row[0]) > int(time.time()):
					# If the schedule time hasn't passed
					self.schedule_priority_queue.put((int(row[0]), row[1]))

	def run(self):
		while True:
			time.sleep(1)
			# Keeping checking the first element in self.schedule_priority_queue
			if not self.schedule_priority_queue.empty():
				unixScheduleTime, action = self.schedule_priority_queue.get()
				if int(unixScheduleTime) < int(time.time()):
					# If the time has come
					if str(action) is 'ON' or 'OFF':
						put_queue(self.on_off_queue, str(action))
					else:
						put_queue(self.on_off_queue, float(action))
				else:
					# If the time hasn't come, put the task back
					self.schedule_priority_queue.put((unixScheduleTime, action))

	def get_queue(self, queue):
		if not queue.empty():
			data = queue.get()
			queue.put(data)
			return data
		else:
			print 'Error: queue is empty when trying to get, waiting to re-get'
			time.sleep(0.5)
			self.get_queue(queue)

	def put_queue(self, queue, data):
		while not queue.empty():
			queue.get()
		queue.put(data)

if __name__ == '__main__':
