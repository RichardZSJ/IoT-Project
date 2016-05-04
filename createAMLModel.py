# Creating aws machine learning model
# This program uploads the finalData.csv file to S3, and used it as a data source to train a binary 
# classification model
import time,sys,random

import boto3

import S3

sys.path.append('../utils')
import aws

TIMESTAMP  =  time.strftime('%Y-%m-%d-%H-%M-%S')
DATA_SOURCE_NAME = 'MTA_DataSource'
DATA_SOURCE_ID = 'mtaData_' + TIMESTAMP
ML_MODEL_ID = 'mlModel_' + TIMESTAMP
S3_FILE_NAME = 'dataplus.csv'
S3_URI = "s3://iotmon4mtadata/dataplus.csv"
DATA_SCHEMA_LOCATION = "s3://iotmon4mtadata/dataplus.csv.schema"

# Upload to S3
S3_ins = S3.S3(S3_FILE_NAME)
S3_ins.uploadData()


########## Machine Learning ##########
mlClient = aws.getClient('machinelearning', 'us-east-1')

dataSource = mlClient.create_data_source_from_s3(
	DataSourceId = DATA_SOURCE_ID,
	DataSourceName = DATA_SOURCE_NAME,
	DataSpec = {
		'DataLocationS3': S3_URI,
		'DataSchemaLocationS3': DATA_SCHEMA_LOCATION
		#'DataSchema': 'string'
	},
	ComputeStatistics = True
)

mlModel = mlClient.create_ml_model(
	MLModelId = ML_MODEL_ID,
	MLModelName='MTA_ML_Model',
	MLModelType = 'BINARY',
	TrainingDataSourceId = dataSource["DataSourceId"]
)

print mlModel