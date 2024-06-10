from calendar import c

import boto3

BUCKET_NAME = "nrsmac-cloud-course-bucket"

session = boto3.Session()
s3_client = session.client("s3")

# Write a file to S3
s3_client.put_object(Bucket=BUCKET_NAME, Key="folder/hello.txt", Body="Hello, world!", ContentType="text/plain")