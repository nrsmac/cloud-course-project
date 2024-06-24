import os

import boto3
from moto import mock_aws
from pytest import fixture

from tests.consts import TEST_BUCKET_NAME


def point_away_from_aws():
    """Point the AWS environment environments to dummy values to avoid using real AWS."""
    os.environ["AWS_ACCESS"] = "test"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "test"
    os.environ["AWS_SECURITY_TOKEN"] = "test"
    os.environ["AWS_SESSION_TOKEN"] = "test"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"


# flake8: noqa
@fixture
def mocked_aws():  # Fixtures represented as nouns instead of verbs
    """A fixture that mocks AWS services using moto."""
    with mock_aws():
        point_away_from_aws()

        # Create an s3 bucket
        s3_client = boto3.client("s3", region_name="us-west-2")
        s3_client.create_bucket(Bucket=TEST_BUCKET_NAME, CreateBucketConfiguration={"LocationConstraint": "us-west-2"})

        yield  # Don't exit context manager until the end of the test

        # Clean up: delete all objects the bucket and the bucket itself
        # Technically not needed since moto cleans up after itself, but needed if using real AWS
        response = s3_client.list_objects_v2(Bucket=TEST_BUCKET_NAME)
        for obj in response.get("Contents", []):
            s3_client.delete_object(Bucket=TEST_BUCKET_NAME, Key=obj["Key"])
        s3_client.delete_bucket(Bucket=TEST_BUCKET_NAME)
