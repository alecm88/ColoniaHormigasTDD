import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from src.main import app, colony
from src.ant import Ant
from src.subsystems import Subsystem, SubsystemType
import time

@pytest.fixture
def client():
    return TestClient(app)

class TestIntegrationAPI:
    def test_request_ant_for_valid_subsystem_comm(self, client):
        request_data = {
            "subsystem_name": SubsystemType.DEFENSE.value,
            "priority": 1,
            "estimated_duration_seconds": 30
        }
        response = client.post("/ants/request", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert "timestamp" in data
        assert "id" in data
        assert SubsystemType.DEFENSE.value in data["receptor"]
        assert SubsystemType.QUEEN.value in data["emisor"]
        assert "mensaje" in data
        assert data["mensaje"]["assignment_successful"] is True
        assert data["mensaje"]["ant"]["state"] == "assigned"
        assert data["mensaje"]["ant"]["assigned_to"] == SubsystemType.DEFENSE.value

    def test_get_ant_for_valid_subsystem_comm(self, client):
        #Assign the ant first
        request_data = {
            "subsystem_name": "S05_DEF",
            "priority": 1,
            "estimated_duration_seconds": 30
        }
        response = client.post("/ants/request", json=request_data)
        data = response.json()
        communication_id = data["id"]
        ant_id = data["mensaje"]["ant"]["id"]

        #Get the ant request simulating a DEFENSE subsystem call   
        messageResponse = client.get("/messages/S05_DEF")
        assert messageResponse.status_code == 200
        messageData = messageResponse.json()

        # Por el momento no podemos comparar id del mensaje. Tenemos que revisar la hormiga.
        assert any(message["mensaje"]["ant"]["id"] == ant_id for message in messageData)
        for message in messageData:
            if message["mensaje"]["ant"]["id"] == ant_id:
                assert "id" in message
                assert "timestamp" in message
                assert "S05_DEF" in message["receptor"]
                assert "S03_REI" in message["emisor"]
                assert "mensaje" in message
                assert message["mensaje"]["assignment_successful"] is True
                assert message["mensaje"]["ant"]["state"] == "assigned"
                assert message["mensaje"]["ant"]["assigned_to"] == "S05_DEF"

                
    def test_messages_queue_empty_comm(self, client):
        #Get the message queue
        #This might backfire if communication system is receiving messages
        messageResponse = client.get("/messages/S03_REI")
        assert messageResponse.status_code == 404 or len(messageResponse.json()) == 0

    def test_service_start(self, client):
        response = client.post("/service?interval=5&run_for_minutes=0.1&activate=true")

        assert response.status_code == 200
        assert response.json()["current_status"]["is_running"] is True

    def test_service_stop(self, client):
        response = client.post("/service?interval=5&run_for_minutes=1&activate=true")

        assert response.status_code == 200
        assert response.json()["current_status"]["is_running"] is True

        # Stop service before time is up
        request_data = {
            "activate": False
        }
        response = client.post("/service?activate=false")

        time.sleep(1)  # Give some time for service to stop

        assert response.status_code == 200
        assert response.json()["current_status"]["is_running"] is False