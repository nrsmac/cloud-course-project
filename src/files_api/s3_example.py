"""Example of using boto3-stubs[s3] package with mypy."""

import boto3

try:
    from mypy_boto3_s3 import S3Client
    from mypy_boto3_s3.type_defs import PutObjectOutputTypeDef
except ImportError:
    print("boto3-stubs[s3] is not installed")

BUCKET_NAME = "some-bucket"

session = boto3.Session()
s3_client: "S3Client" = session.client("s3")

# Write a file to S3
response: "PutObjectOutputTypeDef" = s3_client.put_object(
    Bucket=BUCKET_NAME, Key="folder/hello.txt", Body="Hello, world!", ContentType="text/plain"
)
