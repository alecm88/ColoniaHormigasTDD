import pytest, time
from src.service import Service

@pytest.fixture
def client():
    return TestClient(app)

class TestService:
    def test_start_service(self):
        service = Service(5, 0.1)
        service.run_for_duration()
        status = service.get_status()
        assert status['calls'] > 0

        