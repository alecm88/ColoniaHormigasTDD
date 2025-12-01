import pytest, time
from src.service import Service

class TestService:
    def test_start_service(self):
        service = Service(5, 0.1)
        service.service_start()
        time.sleep(6)  # Wait a bit to let the service run
        status = service.get_status()
        assert status['calls'] > 0