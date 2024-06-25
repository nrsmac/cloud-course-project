from fastapi.testclient import TestClient

def test__get_non_existent_file(client: TestClient):
    response = client.get("/files/non_existent_file")
    assert response.status_code == 404
    assert response.json() == {"detail": "File not found"}
    assert response.headers["content-type"] == "application/json"
