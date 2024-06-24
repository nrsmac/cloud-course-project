import pytest
from fastapi import status
from fastapi.testclient import TestClient

from files_api.main import create_app
from tests.consts import TEST_BUCKET_NAME

# Constants
TEST_FILE_PATH = "test_file.txt"
TEST_FILE_CONTENT = b"Hello, World!"
TEST_FILE_CONTENT_TYPE = "text/plain"


@pytest.fixture
def client(mocked_aws) -> TestClient:  # pylint: disable=unused-argument
    """Fixture for FastAPI test client."""
    app = create_app(s3_bucket_name=TEST_BUCKET_NAME)
    with TestClient(app) as client:
        yield client


def test__upload_file__happy_path(client: TestClient):
    """Asserts that a file can be uploaded successfully."""
    response = client.put(
        f"/files/{TEST_FILE_PATH}",
        files={"file": (TEST_FILE_PATH, TEST_FILE_CONTENT, TEST_FILE_CONTENT_TYPE)},
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {
        "file_path": TEST_FILE_PATH,
        "message": f"File uploaded successfully at path: /{TEST_FILE_PATH}",
    }

    # Update an existing file
    updated_test_file_content = b"Hello, World! Updated!"
    response = client.put(
        f"/files/{TEST_FILE_PATH}",
        files={"file": (TEST_FILE_PATH, updated_test_file_content, TEST_FILE_CONTENT_TYPE)},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "file_path": TEST_FILE_PATH,
        "message": f"File already exists at path: /{TEST_FILE_PATH}",
    }


def test__list_files_with_pagination__happy_path(client: TestClient):
    """Asserts that files can be listed with pagination."""
    for i in range(1, 15):
        test_file_path = f"files/file{i}.txt"
        response = client.put(
            f"/files/{test_file_path}",
            files={"file": (test_file_path, TEST_FILE_CONTENT, TEST_FILE_CONTENT_TYPE)},
        )

    # List files under myfolder/
    response = client.get("/files?pageSize=10")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["files"]) == 10
    assert "next_page_token" in data
    assert data["next_page_token"] is not None


def test__list_files_with_pagination_and_page_token__happy_path(client: TestClient):
    """Asserts that files can be listed with pagination and page token."""
    ...


def test__get_file_metadata__happy_path(client: TestClient):
    """Asserts that file metadata can be retrieved."""
    response = client.put(
        f"/files/{TEST_FILE_PATH}",
        files={"file": (TEST_FILE_PATH, TEST_FILE_CONTENT, TEST_FILE_CONTENT_TYPE)},
    )
    # Get file metadata
    response = client.head(f"/files/{TEST_FILE_PATH}")
    assert response.status_code == status.HTTP_200_OK
    assert response.headers["Content-Type"] == TEST_FILE_CONTENT_TYPE
    assert response.headers["Content-Length"] == str(len(TEST_FILE_CONTENT))
    assert "Last-Modified" in response.headers


def test__get_file___happy_path(client: TestClient):
    """Asserts that a file can be retrieved."""
    # Create a file
    client.put(
        f"/files/{TEST_FILE_PATH}",
        files={"file": (TEST_FILE_PATH, TEST_FILE_CONTENT, TEST_FILE_CONTENT_TYPE)},
    )
    # Get file
    response = client.get(f"/files/{TEST_FILE_PATH}")
    assert response.status_code == status.HTTP_200_OK
    assert TEST_FILE_CONTENT_TYPE in response.headers["Content-Type"]  # Fix charset=utf8 bug?
    assert response.content == TEST_FILE_CONTENT


def test__delete_file__happy_path(client: TestClient):
    """Asserts that a file can be deleted and proper response is returned."""
    client.put(
        f"/files/{TEST_FILE_PATH}",
        files={"file": (TEST_FILE_PATH, TEST_FILE_CONTENT, TEST_FILE_CONTENT_TYPE)},
    )

    # Delete file
    response = client.delete(f"/files/{TEST_FILE_PATH}")
    assert response.status_code == status.HTTP_200_OK
    # Assert empty response body
    assert response.content == b""
