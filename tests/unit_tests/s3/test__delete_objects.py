"""Test cases for `s3.delete_objects`."""

import boto3

from files_api.s3.delete_objects import delete_s3_object
from files_api.s3.read_objects import object_exists_in_s3
from files_api.s3.write_objects import upload_s3_object
from tests.consts import (
    TEST_BUCKET_NAME,
    TEST_OBJECT_KEY,
)


# pylint: disable=unused-argument
def test_delete_existing_s3_object(mocked_aws: None):
    """Assert that `delete_s3_object` deletes an object from an S3 bucket."""
    boto3.client("s3")
    object_key = TEST_OBJECT_KEY

    upload_s3_object(
        bucket_name=TEST_BUCKET_NAME, object_key=object_key, file_content=b"Hello, World!", content_type="text/plain"
    )

    assert object_exists_in_s3(TEST_BUCKET_NAME, object_key)
    delete_s3_object(TEST_BUCKET_NAME, object_key)
    assert not object_exists_in_s3(TEST_BUCKET_NAME, object_key)


# pylint: disable=unused-argument
def test_delete_nonexistent_s3_object(mocked_aws: None):
    """Assert that `delete_s3_object` does not raise an error when deleting a nonexistent object."""
    object_key = "test.txt"
    assert not object_exists_in_s3(TEST_BUCKET_NAME, object_key)
    delete_s3_object(TEST_BUCKET_NAME, object_key)
    assert not object_exists_in_s3(TEST_BUCKET_NAME, object_key)
    assert not object_exists_in_s3(TEST_BUCKET_NAME, object_key)
    assert not object_exists_in_s3(TEST_BUCKET_NAME, object_key)
