"""Test cases for `s3.read_objects`."""

import boto3

from files_api.s3.read_objects import (
    fetch_s3_objects_metadata,
    fetch_s3_objects_using_page_token,
    object_exists_in_s3,
)
from tests.consts import (
    TEST_BUCKET_NAME,
    TEST_OBJECT_KEY,
)


def test_object_exists_in_s3(mocked_aws: None):
    """Assert that `object_exists_in_s3` returns the correct value when an object is or isn't present."""
    s3_client = boto3.client("s3")
    s3_client.put_object(Bucket=TEST_BUCKET_NAME, Key=TEST_OBJECT_KEY, Body="test content")

    exists_in_s3 = object_exists_in_s3(TEST_BUCKET_NAME, TEST_OBJECT_KEY)
    assert exists_in_s3
    # Delete the object
    s3_client.delete_object(Bucket=TEST_BUCKET_NAME, Key=TEST_OBJECT_KEY)
    exists_in_s3 = object_exists_in_s3(TEST_BUCKET_NAME, TEST_OBJECT_KEY)
    assert not exists_in_s3


def test_pagination(mocked_aws: None):
    # Upload 5 objects
    s3_client = boto3.client("s3")
    for i in range(1, 6):
        s3_client.put_object(Bucket=TEST_BUCKET_NAME, Key=f"file{i}.txt", Body=f"content {i}")

    # Paginate 2 at a time
    files, next_page_token = fetch_s3_objects_metadata(TEST_BUCKET_NAME, max_keys=2)
    assert len(files) == 2
    assert files[0]["Key"] == "file1.txt"
    assert files[1]["Key"] == "file2.txt"

    files, next_page_token = fetch_s3_objects_using_page_token(TEST_BUCKET_NAME, next_page_token, max_keys=2)
    assert len(files) == 2
    assert files[0]["Key"] == "file3.txt"
    assert files[1]["Key"] == "file4.txt"

    files, next_page_token = fetch_s3_objects_using_page_token(TEST_BUCKET_NAME, next_page_token, max_keys=2)
    assert len(files) == 1
    assert files[0]["Key"] == "file5.txt"
    assert next_page_token is None


def test_mixed_page_sizes(mocked_aws: None): ...


def test_directory_queries(mocked_aws: None): ...


# TODO: implement
