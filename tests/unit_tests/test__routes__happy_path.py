"""Unit tests for the happy path scenarios of the API routes."""

from fastapi import status
from fastapi.testclient import TestClient

# Constants
TEST_FILE_PATH = "test_file.txt"
TEST_FILE_CONTENT = b"Hello, World!"
TEST_FILE_CONTENT_TYPE = "text/plain"


def test_upload_file(client: TestClient):
    """Asserts that a file can be uploaded successfully."""
    response = client.put(
        f"/v1/files/{TEST_FILE_PATH}",
        files={"file_content": (TEST_FILE_PATH, TEST_FILE_CONTENT, TEST_FILE_CONTENT_TYPE)},
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {
        "file_path": TEST_FILE_PATH,
        "message": f"File uploaded successfully at path: /{TEST_FILE_PATH}",
    }

    # Update an existing file
    updated_test_file_content = b"Hello, World! Updated!"
    response = client.put(
        f"/v1/files/{TEST_FILE_PATH}",
        files={"file_content": (TEST_FILE_PATH, updated_test_file_content, TEST_FILE_CONTENT_TYPE)},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "file_path": TEST_FILE_PATH,
        "message": f"File already exists at path: /{TEST_FILE_PATH}",
    }


def test_list_files_with_pagination(client: TestClient):
    """Asserts that files can be listed with pagination."""
    for i in range(15):
        client.put(
            f"/v1/files/file{i}.txt",
            files={"file_content": (f"file{i}.txt", TEST_FILE_CONTENT, TEST_FILE_CONTENT_TYPE)},
        )
    response = client.get("/v1/files?page_size=10")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["files"]) == 10
    assert "next_page_token" in data


def test_list_files_with_pagination_and_page_token(client: TestClient):  # pylint: disable=unused-argument
    """Asserts that files can be listed with pagination and page token."""
    ...  # pylint: disable=W2301


def test_get_file_metadata(client: TestClient):
    """Asserts that file metadata can be retrieved."""
    response = client.put(
        f"/v1/files/{TEST_FILE_PATH}",
        files={"file_content": (TEST_FILE_PATH, TEST_FILE_CONTENT, TEST_FILE_CONTENT_TYPE)},
    )

    assert response.status_code == status.HTTP_201_CREATED
    # Get file metadata
    response = client.head(f"/v1/files/{TEST_FILE_PATH}")
    assert response.status_code == status.HTTP_200_OK
    headers = response.headers
    assert headers["Content-Type"] == TEST_FILE_CONTENT_TYPE
    assert headers["Content-Length"] == str(len(TEST_FILE_CONTENT))
    assert "Last-Modified" in headers


def test_get_file_(client: TestClient):
    """Asserts that a file can be retrieved."""
    # Create a file
    client.put(
        f"/v1/files/{TEST_FILE_PATH}",
        files={"file_content": (TEST_FILE_PATH, TEST_FILE_CONTENT, TEST_FILE_CONTENT_TYPE)},
    )
    # Get file
    response = client.get(f"/v1/files/{TEST_FILE_PATH}")
    assert response.status_code == status.HTTP_200_OK
    assert TEST_FILE_CONTENT_TYPE in response.headers["Content-Type"]  # Fix charset=utf8 bug?
    assert response.content == TEST_FILE_CONTENT


def test_delete_file(client: TestClient):
    """Asserts that a file can be deleted and proper response is returned."""
    client.put(
        f"/v1/files/{TEST_FILE_PATH}",
        files={"file_content": (TEST_FILE_PATH, TEST_FILE_CONTENT, TEST_FILE_CONTENT_TYPE)},
    )

    # Delete file
    response = client.delete(f"/v1/files/{TEST_FILE_PATH}")
    assert response.status_code == status.HTTP_200_OK
    # Assert empty response body
    assert response.content == b""
