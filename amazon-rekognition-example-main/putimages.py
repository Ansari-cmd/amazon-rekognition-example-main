import boto3

def store(img,name):
	s3 = boto3.resource('s3')

	# Get list of objects for indexing
	images=[(img,name)]

	# Iterate through list to upload objects to S3   
	for img in images:
		file = open(img[0],'rb')
		object = s3.Object('famousepersons-images','index/'+ img[0])
		ret = object.put(Body=file,
			Metadata={'FullName':img[1]})