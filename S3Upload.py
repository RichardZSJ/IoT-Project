# *********************************************************************************************
# All S3 related helper function
# *********************************************************************************************
import time
import sys
import json
import boto3
from botocore.exceptions import ClientError 
import aws
import threading

FILENAME = "environmentData.csv"

class S3Uploader(threading.Thread):
	S3 = None
	S3_BUCKET_NAME = 'iot_project'
	S3Bucket = None
	trainingData = None
	INTERVAL = 3600

	def __init__(self, threadName, trainingData = FILENAME):
		threading.Thread.__init__(self)
		self.S3 = aws.getResource('s3','us-east-1')
		self.trainingData = trainingData
		self.threadName = threadName

	def run(self):
		print "Starting thread:", self.threadName + "..."
		while True:
			time.sleep(self.INTERVAL)
			self.uploadData()

	def uploadData(self):

		# if the given bucket exist get the bucket or create one 
		if self.bucketExists():	
			self.S3Bucket = self.S3.Bucket(self.S3_BUCKET_NAME)
		else:
			self.S3Bucket = self.S3.create_bucket(Bucket=self.S3_BUCKET_NAME)

		# Upload data to S3
		self.uploadToS3()		

	def uploadToS3(self):
		with open(self.trainingData,'rb') as data:
			# uploading data
			self.S3Bucket.Object(self.trainingData).put(Body=data)

	def bucketExists(self):
		try:
			# Get S3 bucket related details
			self.S3.meta.client.head_bucket(Bucket=self.S3_BUCKET_NAME)
			return True

		except ClientError:
			return False


if __name__ == "__main__":
	s3Thread = S3Uploader("S3Thread", FILENAME)
	s3Thread.deamon = True
	s3Thread.start()
	try:
		while True:
			time.sleep(10000)
	except KeyboardInterrupt:
		exit
