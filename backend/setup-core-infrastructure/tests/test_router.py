from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_setup_core_infrastructure_router():
    response = client.get('/setup-core-infrastructure')
    assert response.status_code == 200