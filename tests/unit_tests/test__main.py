import pytest
from fastapi.testclient import TestClient
from fastapi import status

from src.files_api.main import APP

# Constants
TEST_FILE_PATH = "test_file.txt"
TEST_FILE_CONTENT = b"Hello, World!"
TEST_FILE_CONTENT_TYPE = "text/plain"


# Fixture for FastAPI test client
@pytest.fixture
def client(mocked_aws) -> TestClient:  # pylint: disable=unused-argument
    with TestClient(APP) as client:
        yield client


def test__upload_file__happy_path(client: TestClient):
    # Create a file
    response = client.put(
        f"/files/{TEST_FILE_PATH}",
        files={"file": (TEST_FILE_PATH, TEST_FILE_CONTENT, TEST_FILE_CONTENT_TYPE)},
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {
        "file_path": TEST_FILE_PATH,
        "message": f"File uploaded successfully at path: /{TEST_FILE_PATH}"
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
        "message": f"File already exists at path: /{TEST_FILE_PATH}"
    }


def test__list_files_with_pagination__happy_path(client: TestClient):
    # Create a file under myfolder/
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



def test__get_file_metadata(client: TestClient):
    # Create a file
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


def test_get_file(client: TestClient):
    # Create a file
    client.put(
        f"/files/{TEST_FILE_PATH}",
        files={"file": (TEST_FILE_PATH, TEST_FILE_CONTENT, TEST_FILE_CONTENT_TYPE)},
    )
    # Get file
    response = client.get(f"/files/{TEST_FILE_PATH}")
    assert response.status_code == status.HTTP_200_OK
    assert response.headers["Content-Type"] == TEST_FILE_CONTENT_TYPE
    assert response.content == TEST_FILE_CONTENT


def test_delete_file(client: TestClient): ...
