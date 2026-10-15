import pytest
from app import create_app

@pytest.fixture()
def client():
    app = create_app()
    app.config.update(TESTING=True)
    with app.test_client() as client:
        yield client

def test_home_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Student Score Predictor' in response.data

def test_health_endpoint(client):
    response = client.get('/health')
    assert response.status_code == 200
    assert response.get_json()['status'] == 'healthy'

def test_prediction_endpoint(client):
    response = client.post('/predict', json={'study_hours': 4})
    assert response.status_code == 200
    result = response.get_json()
    assert result['study_hours'] == 4
    assert 0 <= result['predicted_score'] <= 100

def test_invalid_input_rejected(client):
    response = client.post('/predict', json={'study_hours': 30})
    assert response.status_code == 400

def test_metrics_endpoint(client):
    client.get('/')
    response = client.get('/metrics')
    assert response.status_code == 200
    assert b'student_score_http_requests_total' in response.data
