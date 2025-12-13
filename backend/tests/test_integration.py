"""
Integration tests for the grading pipeline.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """Test client fixture."""
    return TestClient(app)


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_upload_invalid_file(client):
    """Test uploading invalid file type."""
    response = client.post(
        "/api/exams/upload",
        files={"file": ("test.exe", b"fake content", "application/x-msdownload")}
    )
    assert response.status_code == 400


def test_parse_nonexistent_exam(client):
    """Test parsing non-existent exam."""
    response = client.post("/api/exams/nonexistent-id/parse")
    assert response.status_code == 404


def test_grade_nonexistent_exam(client):
    """Test grading non-existent exam."""
    response = client.post(
        "/api/exams/nonexistent-id/grade",
        json={
            "exam_id": "nonexistent-id",
            "student_answers": []
        }
    )
    assert response.status_code == 400

