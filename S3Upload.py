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


	def __init__(self, trainingData, threadName):
		# Get s3 resource , function for this is in utils/aws
		threading.Thread.__init__(self)
		self.S3 = aws.getResource('s3','us-east-1')
		self.trainingData = trainingData
		self.threadName = threadName
		#self.S3_BUCKET_NAME = 'iotmon4mtadata'

	def run(self):
		print "Starting thread:", self.threadName + "..."
		while True:
			self.uploadData()
			time.sleep(self.INTERVAL)

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

	"""def checkBucketPolicy(self):
		# Desired policy
		with open('amlS3Policy.json','rb') as policy:
			targetPolicy = policy.read().format(bucketName=self.S3Bucket.name,keyName=self.trainingData)
			policy.close()
    
		# get current bucket policy
		existingPolicy = ''

		try:
			existingPolicy = self.S3.BucketPolicy(self.S3_BUCKET_NAME).policy
			updatedPolicy = self.verifyOrFixPolicy(existingPolicy,targetPolicy)


		except ClientError as e:
		    # If a client error is thrown, then check that it was a 404 error.
		    # If it was a 404 error, then the bucket policy does not exist.
		    error_code = int(e.response['Error']['Code'])
		    if error_code != 404:
		    	raise e



	def verifyOrFixPolicy(self,existingPolicy,targetPolicy):
		if existingPolicy == '':
			return targetPolicy
        jsonPolicy = json.loads(existingPolicy)
        targetStatement = json.loads(targetPolicy)['Statement'][0]
        targetResouceArn = targetPolicy['Resource'][0]
        for statement in jsonPolicy['Statement']:
        	if (
        		statement.has_key('Principal') and
        		statement['Principal'].has_key('Service') and
        		statement['Principal']['Service'] == 'machinelearning.amazonaws.com' and
        		statement['Effect'] == "Allow" and
        		"s3:GetObject" in statement['Action']):
        		if targetResouceArn == statement['Resource'] or targetResouceArn in statement['Resource']:
                    # no change required
                    return None
	            elif isinstance(statement['Resource'], str) or isinstance(statement['Resource'], unicode):
	                # convert the resource value to a list
	                statement['Resource'] = [statement['Resource']]
	            # If we reach here then we know that resource is a list that doesn't contain target_resource_arn
                statement['Resource'].append(targetResouceArn)
                return json.dumps(jsonPolicy)
	    # If we reach here then we know that simplest change is to append the desired statement into the policy.
        jsonPolicy['Statement'].append(targetStatement)
        return json.dumps(jsonPolicy)"""


    	

if __name__ == "__main__":
	s3Thread = S3Uploader(FILENAME, "S3Thread")
	s3Thread.deamon = True
	s3Thread.start()
	try:
		while True:
			time.sleep(10000)
	except KeyboardInterrupt:
		exit
