import boto3
import pendulum

from files_api import s3
from files_api.s3.write_objects import upload_s3_object

TEST_BUCKET_NAME = "nrsmac-test-bucket-mlops-club"


def test__upload_s3_object():
    # Create an s3 bucket
    s3_client = boto3.client("s3", region_name="us-west-2")
    s3_client.create_bucket(Bucket=TEST_BUCKET_NAME, CreateBucketConfiguration={"LocationConstraint": "us-west-2"})

    # Upload file to a bucket with a particular content type
    object_key = "test_file.txt"
    file_content = b"Hello, World!"
    content_type = "text/plain"

    upload_s3_object(
        bucket_name=TEST_BUCKET_NAME,
        object_key=object_key,
        file_content=file_content,
        content_type=content_type,
        s3_client=s3_client,
    )
    # Check that the file was uploaded with correct content type
    # TODO replace with our own function calls
    response = s3_client.get_object(Bucket=TEST_BUCKET_NAME, Key=object_key)
    assert response["ContentType"] == content_type
    assert response["Body"].read() == file_content

    # Clean up deleting all objects the bucket and the bucket itself
    # TODO replace with our own function calls
    response = s3_client.list_objects_v2(Bucket=TEST_BUCKET_NAME)
    for obj in response.get("Contents", []):
        s3_client.delete_object(Bucket=TEST_BUCKET_NAME, Key=obj["Key"])
    s3_client.delete_bucket(Bucket=TEST_BUCKET_NAME)
