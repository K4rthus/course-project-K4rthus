from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_rfc7807_validation_error():
    """Тест формата ошибок валидации"""
    response = client.post("/suggestions", json={"title": ""})

    assert response.status_code == 422
    data = response.json()

    assert data["type"] == "/errors/validation"
    assert data["title"] == "Validation Error"
    assert "correlation_id" in data
    assert data["status"] == 422


def test_rfc7807_not_found():
    """Тест формата 404 ошибок"""
    response = client.get("/nonexistent-endpoint")

    assert response.status_code == 404
    data = response.json()

    assert data["type"] == "/errors/not_found"
    assert "correlation_id" in data
    assert data["status"] == 404


def test_correlation_id_uniqueness():
    """Тест уникальности correlation_id"""
    responses = []
    for _ in range(5):
        response = client.get("/nonexistent-endpoint")
        responses.append(response.json())

    correlation_ids = {r["correlation_id"] for r in responses}
    assert len(correlation_ids) == 5


def test_error_structure_consistency():
    """Тест консистентности структуры ошибок"""
    response = client.get("/nonexistent-endpoint")

    assert response.status_code == 404
    data = response.json()

    required_fields = {"type", "title", "status", "detail", "correlation_id"}
    assert all(field in data for field in required_fields)

    assert response.headers["content-type"] == "application/problem+json"
