API = "/api/v1"


def test_liveness(client):
    assert client.get("/health/live").json()["status"] == "ok"


def test_readiness_when_model_loaded(client):
    response = client.get("/health/ready")
    assert response.status_code == 200
    assert response.json()["model_version"] == "test"


def test_readiness_without_model(client_without_model):
    response = client_without_model.get("/health/ready")
    assert response.status_code == 503
    assert response.json()["status"] == "unavailable"


def test_classify(client):
    response = client.post(f"{API}/classifications", json={"review": "I love this blender"})
    assert response.status_code == 200
    body = response.json()
    assert body["sentiment"] == "positive"
    assert set(body["scores"]) == {"negative", "neutral", "positive"}
    assert "X-Request-ID" in response.headers


def test_classify_batch_with_summary(client):
    response = client.post(f"{API}/classifications/batch",
                           json={"reviews": ["great", "it broke", "fine"]})
    assert response.status_code == 200
    body = response.json()
    assert [r["sentiment"] for r in body["results"]] == ["positive", "negative", "neutral"]
    assert body["summary"] == {"negative": 1, "neutral": 1, "positive": 1}


def test_empty_review_returns_problem_details(client):
    response = client.post(f"{API}/classifications", json={"review": "   "})
    assert response.status_code == 422
    assert response.headers["content-type"] == "application/problem+json"
    assert response.json()["detail"] == "The review is empty."


def test_missing_field_returns_problem_details(client):
    response = client.post(f"{API}/classifications", json={})
    assert response.status_code == 422
    assert response.json()["title"] == "Validation error"


def test_batch_too_large(client):
    response = client.post(f"{API}/classifications/batch", json={"reviews": ["a"] * 4})
    assert response.status_code == 422
    assert "At most 3" in response.json()["detail"]


def test_classify_without_model_returns_503(client_without_model):
    response = client_without_model.post(f"{API}/classifications", json={"review": "hello"})
    assert response.status_code == 503
    assert response.json()["title"] == "Model unavailable"


def test_model_card(client):
    body = client.get(f"{API}/model").json()
    assert body["classifier"] == "keyword-fake"
    assert body["labels"] == ["negative", "neutral", "positive"]


def test_serves_front_end_when_static_dir_is_set(settings, classifier, tmp_path):
    from fastapi.testclient import TestClient

    from review_sentiment.api.app import create_app

    (tmp_path / "index.html").write_text("<title>Review Sentiment</title>")
    app = create_app(settings.model_copy(update={"static_dir": tmp_path}),
                     classifier_factory=lambda _: classifier)
    with TestClient(app) as c:
        assert "Review Sentiment" in c.get("/").text
        assert c.post(f"{API}/classifications", json={"review": "great"}).status_code == 200
