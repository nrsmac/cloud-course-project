import os

import boto3
import botocore
import pytest
from moto import mock_aws

from tests.consts import TEST_BUCKET_NAME
from tests.utils import delete_s3_bucket


def point_away_from_aws():
    """Point the AWS environment environments to dummy values to avoid using real AWS."""
    os.environ["AWS_ACCESS"] = "test"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "test"
    os.environ["AWS_SECURITY_TOKEN"] = "test"
    os.environ["AWS_SESSION_TOKEN"] = "test"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"


# flake8: noqa
@pytest.fixture(scope="function")
def mocked_aws():  # Fixtures represented as nouns instead of verbs
    """A fixture that mocks AWS services using moto."""
    with mock_aws():
        # Set the environment variables to point away from AWS
        point_away_from_aws()

        # 1. Create an S3 bucket
        s3_client = boto3.client("s3")
        s3_client.create_bucket(Bucket=TEST_BUCKET_NAME)

        yield

        # 2. Clean up/Teardown by deleting the bucket
        try:
            delete_s3_bucket(TEST_BUCKET_NAME)
        except botocore.exceptions.ClientError as err:
            if err.response["Error"]["Code"] == "NoSuchBucket":
                pass
            else:
                raise
