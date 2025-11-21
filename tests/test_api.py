import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from src.main import app, colony
from src.ant import Ant

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


class TestAntsAPI:
    def test_root_endpoint(self, client):
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "Sistema de Hormiga Reina"}
        
    def test_get_colony_status(self, client):
        response = client.get("/colony/status")
        assert response.status_code == 200
        data = response.json()

        expected_keys = {'total_ants', 'alive_ants', 'free_ants', 'assigned_ants', 'dead_ants', 'max_ants', 'food_stock'}
        assert set(data.keys()) == expected_keys
        assert data['total_ants'] == 0
        assert data['alive_ants'] == 0
        assert data['free_ants'] == 0
        assert data['assigned_ants'] == 0
        assert data['dead_ants'] == 0
        assert data['max_ants'] == 100
        assert data['food_stock'] == 1000

    def test_create_ant_success(self, client):
        response = client.post("/ants")
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "birth_time" in data
        assert "death_time" in data
        assert data["is_alive"] is True
        assert data["age_seconds"] < 1

    # def test_get_colony_status(self, client):
    #     # Create some ants
    #     client.post("/ants")
    #     client.post("/ants")

    #     response = client.get("/colony/status")
    #     assert response.status_code == 200
    #     data = response.json()

    #     expected_keys = {'total_ants', 'alive_ants', 'dead_ants', 'max_ants', 'can_create_more'}
    #     assert set(data.keys()) == expected_keys
    #     assert data["alive_ants"] == 2
    #     assert data["total_ants"] == 2
    #     assert data["dead_ants"] == 0
    #     assert data["max_ants"] == 10
    #     assert data["can_create_more"] is True

    def test_create_ant_at_capacity_fails(self, client):
        # Configure colony to max 1 ant
        client.put("/colony/config?max_ants=1")

        # Create first ant (should succeed)
        response1 = client.post("/ants")
        assert response1.status_code == 200

        # Try to create second ant (should fail)
        response2 = client.post("/ants")
        assert response2.status_code == 409
        assert "Sin capacidad" in response2.json()["detail"]
        
    def test_create_ant_at_capacity_fails(self, client):
        # Configure colony to little food
        client.put("/colony/config?food_stock=10")

        # Create first ant (should succeed)
        response1 = client.post("/ants")
        assert response1.status_code == 200

        # Try to create second ant (should fail)
        response2 = client.post("/ants")
        assert response2.status_code == 409
        assert "Sin recursos" in response2.json()["detail"]

    def test_get_all_ants(self, client):
        # Create two ants
        client.post("/ants")
        client.post("/ants")

        response = client.get("/ants")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        for ant in data:
            assert "id" in ant
            assert ant["is_alive"] is True

    def test_get_ant_by_id(self, client):
        # Create an ant
        create_response = client.post("/ants")
        ant_id = create_response.json()["id"]

        # Get the ant by ID
        response = client.get(f"/ants/{ant_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == ant_id
        assert data["is_alive"] is True

    def test_get_nonexistent_ant(self, client):
        response = client.get("/ants/nonexistent-id")
        assert response.status_code == 404
        assert "Hormiga no encontrada" in response.json()["detail"]

    # def test_cleanup_dead_ants(self, client):
    #     # Create an ant
    #     create_response = client.post("/ants")
    #     ant_id = create_response.json()["id"]

    #     # Make the ant die by accessing colony directly
    #     colony.ants[ant_id].birth_time = datetime.now() - timedelta(seconds=91)

    #     # Cleanup dead ants
    #     response = client.post("/colony/cleanup")
    #     assert response.status_code == 200
    #     assert "Cleaned up 1 dead ants" in response.json()["message"]

    #     # Verify ant is gone
    #     get_response = client.get(f"/ants/{ant_id}")
    #     assert get_response.status_code == 404

    # def test_configure_colony_max_ants(self, client):
    #     response = client.put("/colony/config?max_ants=5")
    #     assert response.status_code == 200
    #     assert "maximum 5 ants" in response.json()["message"]

    #     # Verify the configuration
    #     status_response = client.get("/colony/status")
    #     assert status_response.json()["max_ants"] == 5

    # def test_configure_colony_invalid_max_ants(self, client):
    #     response = client.put("/colony/config?max_ants=0")
    #     assert response.status_code == 400
    #     assert "must be at least 1" in response.json()["detail"]

    # def test_ant_lifecycle_integration(self, client):
    #     # Configure small colony
    #     client.put("/colony/config?max_ants=2")

    #     # Create two ants (at capacity)
    #     ant1_response = client.post("/ants")
    #     ant2_response = client.post("/ants")
    #     assert ant1_response.status_code == 200
    #     assert ant2_response.status_code == 200

    #     # Try to create third ant (should fail)
    #     ant3_response = client.post("/ants")
    #     assert ant3_response.status_code == 409

    #     # Make first ant die
    #     ant1_id = ant1_response.json()["id"]
    #     colony.ants[ant1_id].birth_time = datetime.now() - timedelta(seconds=91)

    #     # Now should be able to create new ant (cleanup happens automatically)
    #     ant4_response = client.post("/ants")
    #     assert ant4_response.status_code == 200

    #     # Verify status
    #     status_response = client.get("/colony/status")
    #     status_data = status_response.json()
    #     assert status_data["alive_ants"] == 2  # ant2 + ant4