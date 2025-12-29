#   app/tests/test_fraud.py
def test_batch_predict(client):
    response = client.post("/api/fraud/predict/batch")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        item = data[0]
        assert "user_email" in item
        assert "risk_score" in item
        assert "decision" in item

def test_single_user_predict(client):
    email = "test@example.com"
    response = client.get(f"/api/fraud/predict/user/{email}")

    # допустимо 200 или 404 — зависит от fetch
    assert response.status_code in (200, 404)
