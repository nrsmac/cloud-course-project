<<<<<<< Updated upstream
"""Test cases for s3.read_objects."""
=======
"""Test cases for `s3.read_objects`."""
>>>>>>> Stashed changes

import boto3
import boto3.exceptions
import pytest

<<<<<<< Updated upstream
=======
try:
    pass
except ImportError:  # pragma: no cover
    ...

>>>>>>> Stashed changes
from files_api.s3.read_objects import (
    fetch_s3_object,
    fetch_s3_objects_metadata,
    fetch_s3_objects_using_page_token,
    object_exists_in_s3,
)
from tests.consts import (
    TEST_BUCKET_NAME,
    TEST_OBJECT_KEY,
)


<<<<<<< Updated upstream
def test_object_exists_in_s3(mocked_aws: None):  # pylint: disable=unused-argument
=======
# pylint: disable=unused-argument
def test_object_exists_in_s3(mocked_aws: None):
>>>>>>> Stashed changes
    """Assert that `object_exists_in_s3` returns the correct value when an object is or isn't present."""
    s3_client = boto3.client("s3")
    s3_client.put_object(Bucket=TEST_BUCKET_NAME, Key=TEST_OBJECT_KEY, Body="test content")

    exists_in_s3 = object_exists_in_s3(TEST_BUCKET_NAME, TEST_OBJECT_KEY)
    assert exists_in_s3
    # Delete the object
    s3_client.delete_object(Bucket=TEST_BUCKET_NAME, Key=TEST_OBJECT_KEY)
    exists_in_s3 = object_exists_in_s3(TEST_BUCKET_NAME, TEST_OBJECT_KEY)
    assert not exists_in_s3


# pylint: disable=unused-argument
def test_fetch_s3_object(mocked_aws: None):
<<<<<<< Updated upstream
    """Assert that `fetch_s3_object` returns the correct object from an S3 bucket."""
=======
>>>>>>> Stashed changes
    s3_client = boto3.client("s3")
    s3_client.put_object(Bucket=TEST_BUCKET_NAME, Key=TEST_OBJECT_KEY, Body="test content")

    obj = fetch_s3_object(TEST_BUCKET_NAME, TEST_OBJECT_KEY)
    obj_content = obj["Body"].read().decode("utf-8")
    assert obj_content == "test content"


# pylint: disable=unused-argument
<<<<<<< Updated upstream
# flake8: noqa
def test_pagination(mocked_aws: None):
    """Assert that `fetch_s3_objects_metadata` paginates correctly."""
=======
def test_pagination(mocked_aws: None):
>>>>>>> Stashed changes
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


# pylint: disable=unused-argument
def test_mixed_page_sizes(mocked_aws: None):
<<<<<<< Updated upstream
    """Assert that `fetch_s3_objects_metadata` paginates correctly with mixed page sizes."""
=======
>>>>>>> Stashed changes
    s3_client = boto3.client("s3")
    for i in range(1, 7):
        s3_client.put_object(Bucket=TEST_BUCKET_NAME, Key=f"file{i}.txt", Body=f"content {i}")

    # 2 at a time
    files, next_page_token = fetch_s3_objects_metadata(TEST_BUCKET_NAME, max_keys=2)
<<<<<<< Updated upstream
=======
    assert len(files) == 2
>>>>>>> Stashed changes
    assert files[0]["Key"] == "file1.txt"
    assert files[1]["Key"] == "file2.txt"

    # 3 at a time
    files, next_page_token = fetch_s3_objects_using_page_token(TEST_BUCKET_NAME, next_page_token, max_keys=3)
    assert len(files) == 3
    assert files[0]["Key"] == "file3.txt"
    assert files[1]["Key"] == "file4.txt"
    assert files[2]["Key"] == "file5.txt"

    # 1 at a time
    files, next_page_token = fetch_s3_objects_using_page_token(TEST_BUCKET_NAME, next_page_token, max_keys=1)
    assert len(files) == 1
    assert files[0]["Key"] == "file6.txt"

    assert next_page_token is None


# pylint: disable=unused-argument
<<<<<<< Updated upstream
# flake8: noqa
def test_directory_queries(mocked_aws: None):
    """Assert that `fetch_s3_objects_metadata` returns the correct files for different prefixes."""
=======
def test_directory_queries(mocked_aws: None):
>>>>>>> Stashed changes
    s3_client = boto3.client("s3")
    s3_client.put_object(Bucket=TEST_BUCKET_NAME, Key="folder1/file1.txt", Body="content 1")
    s3_client.put_object(Bucket=TEST_BUCKET_NAME, Key="folder1/file2.txt", Body="content 2")
    s3_client.put_object(Bucket=TEST_BUCKET_NAME, Key="folder2/file3.txt", Body="content 3")
    s3_client.put_object(Bucket=TEST_BUCKET_NAME, Key="folder2/subfolder1/file4.txt", Body="content 4")
    s3_client.put_object(Bucket=TEST_BUCKET_NAME, Key="file5.txt", Body="content 5")

    # Query all files
    files, next_page_token = fetch_s3_objects_metadata(TEST_BUCKET_NAME)
    assert len(files) == 5
    assert files[0]["Key"] == "file5.txt"
    assert files[1]["Key"] == "folder1/file1.txt"
    assert files[2]["Key"] == "folder1/file2.txt"
    assert files[3]["Key"] == "folder2/file3.txt"
    assert files[4]["Key"] == "folder2/subfolder1/file4.txt"
    assert next_page_token is None

    # Folder 1
    files, next_page_token = fetch_s3_objects_metadata(TEST_BUCKET_NAME, prefix="folder1/")
    assert len(files) == 2
    assert files[0]["Key"] == "folder1/file1.txt"
    assert files[1]["Key"] == "folder1/file2.txt"
    assert next_page_token is None  # No other files in folder_1

    # Folder 2
    files, next_page_token = fetch_s3_objects_metadata(TEST_BUCKET_NAME, prefix="folder2/")
    assert len(files) == 2
    assert files[0]["Key"] == "folder2/file3.txt"
    assert files[1]["Key"] == "folder2/subfolder1/file4.txt"
    assert next_page_token is None  # No other files in folder_2

    # Nested Folder
    files, next_page_token = fetch_s3_objects_metadata(TEST_BUCKET_NAME, prefix="folder2/subfolder1/")
    assert len(files) == 1
    assert files[0]["Key"] == "folder2/subfolder1/file4.txt"
    assert next_page_token is None  # No other files in subfolder1

    # Non-existent folder
    files, next_page_token = fetch_s3_objects_metadata(TEST_BUCKET_NAME, prefix="folder3/")
    assert len(files) == 0


def test_raises_error_when_bucket_does_not_exist(mocked_aws: None):
<<<<<<< Updated upstream
    """Assert that functions raise an error when the bucket does not exist."""
=======
>>>>>>> Stashed changes
    with pytest.raises(Exception):
        fetch_s3_object("non-existent-bucket", "non-existent-key")
    with pytest.raises(Exception):
        fetch_s3_objects_metadata("non-existent-bucket")
    with pytest.raises(Exception):
        fetch_s3_objects_using_page_token("non-existent-bucket", "token")
<<<<<<< Updated upstream
        fetch_s3_objects_using_page_token("non-existent-bucket", "token")
=======
>>>>>>> Stashed changes
