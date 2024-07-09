"""Tests for the `write_objects` module in the `s3` package."""

import boto3

from files_api.s3.write_objects import upload_s3_object
from tests.fixtures.mocked_aws import TEST_BUCKET_NAME


# pylint: disable=unused-argument
def test__upload_s3_object(mocked_aws: None):
    """Assert that `upload_s3_object` uploads a file to an S3 bucket with the correct content type."""
    # Upload file to a bucket with a particular content type
    object_key = "test_file.txt"
    file_content = b"Hello, World!"
    content_type = "text/plain"

    upload_s3_object(
        bucket_name=TEST_BUCKET_NAME,
        object_key=object_key,
        file_content=file_content,
        content_type=content_type,
    )

    s3_client = boto3.client("s3")

    # Check that the file was uploaded with correct content type
    response = s3_client.get_object(Bucket=TEST_BUCKET_NAME, Key=object_key)
    assert response["ContentType"] == content_type
    assert response["Body"].read() == file_content
