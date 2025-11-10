from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_sql_injection_attempt_in_filter():
    """Тест на попытку SQL инъекции в параметры фильтрации"""
    response = client.get("/suggestions?status=pending'; DROP TABLE suggestions; --")
    assert response.status_code in [200, 422]
    if response.status_code == 200:
        assert response.json() == []


def test_xss_in_suggestion_content():
    """Тест на XSS в содержимом предложения"""
    malicious_title = 'Test<script>alert("xss")</script>'
    response = client.post(
        "/suggestions", json={"title": malicious_title, "text": "normal text"}
    )

    assert response.status_code in [200, 422]

    if response.status_code == 200:
        data = response.json()
        assert "<script>" not in data["title"]
        assert "&lt;script&gt;" in data["title"]


def test_long_string_attack():
    """Тест на атаку длинной строкой"""
    long_string = "A" * 10000
    response = client.post(
        "/suggestions", json={"title": long_string[:101], "text": "normal text"}
    )
    assert response.status_code == 422


def test_special_characters_in_input():
    """Тест на специальные символы во вводе"""
    special_chars_title = "Test & < > \" ' ; --"
    response = client.post(
        "/suggestions", json={"title": special_chars_title, "text": "normal text"}
    )

    assert response.status_code in [200, 422]

    if response.status_code == 200:
        data = response.json()
        assert "&" in data["title"] or "&amp;" in data["title"]
        assert "<" not in data["title"] or "&lt;" in data["title"]
