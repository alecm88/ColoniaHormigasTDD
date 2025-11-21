import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from src.main import app, colony
from src.ant import Ant
from src.subsystems import Subsystem, SubsystemType

@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_colony():
    # Reset colony before each test
    colony.ants.clear()
    colony.max_ants = 100
    colony.food_stock = 1000
    yield


class TestIntegrationAPI:
    def test_request_ant_for_valid_subsystem(self, client):
        request_data = {
            "subsystem_name": "S05_DEF",
            "priority": 1,
            "estimated_duration_seconds": 30
        }
        response = client.post("/ants/request", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert "S05_DEF" in data["receptor"]
        assert "S03_REI" in data["emisor"]
        assert "contenido" in data
        assert data["contenido"]["assignment_successful"] is True
        assert data["contenido"]["ant"]["state"] == "assigned"
        assert data["contenido"]["ant"]["assigned_to"] == "S05_DEF"