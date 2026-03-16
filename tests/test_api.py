from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_signal_endpoint_returns_mock_data():
    response = client.get("/api/signals/opcua/motor-1")
    assert response.status_code == 200
    body = response.json()
    assert body["asset_id"] == "motor-1"
    assert body["signals"]["protocol"] == "opcua"


def test_rest_gateway_endpoint_falls_back_to_mock_data():
    response = client.get("/api/signals/rest/motor-1")
    assert response.status_code == 200
    body = response.json()
    assert body["signals"]["protocol"] == "rest"


def test_upload_ingestion_accepts_text_document():
    response = client.post(
        "/api/ingest/upload",
        files={"files": ("quick_guide.txt", b"Motor troubleshooting checklist", "text/plain")},
    )
    assert response.status_code == 200
    body = response.json()
    assert "quick_guide.txt" in body["filenames"]
    assert body["documents_indexed"] >= 1
