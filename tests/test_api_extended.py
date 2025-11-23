import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from src.main import app, colony
from src.ant import AntState


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_colony():
    # Reset colony before each test with academic requirements
    colony.ants.clear()
    colony.max_ants = 100
    colony.food_stock = 1000
    colony.ant_lifespan_minutes = 1.5
    colony.emergency_mode = False
    yield


class TestQueenAntAPI:
    def test_root_endpoint_shows_queen_ant_info(self, client):
        response = client.get("/info")
        assert response.status_code == 200
        data = response.json()
        assert "Hormiga Reina" in data["message"]
        assert data["version"] == "1.0.0"
        assert "S01_COM" in data["available_subsystems"]
        assert "S02_REC" in data["available_subsystems"]
        assert "S04_ENT" in data["available_subsystems"]
        assert "S05_DEF" in data["available_subsystems"]

    # Lo cambiamos para aceptar los subsistemazs nuevos. Lo movemos para test_api_integration
    # def test_request_ant_for_valid_subsystem(self, client):
    #     request_data = {
    #         "subsystem_name": "defense",
    #         "priority": 1,
    #         "estimated_duration_seconds": 30
    #     }
    #     response = client.post("/ants/request", json=request_data)

    #     assert response.status_code == 200
    #     data = response.json()
    #     assert data["assignment_successful"] is True
    #     assert "Defense" in data["message"]
    #     assert "ant" in data
    #     assert data["ant"]["state"] == "assigned"
    #     assert data["ant"]["assigned_to"] == "defense"

    def test_request_ant_for_invalid_subsystem(self, client):
        request_data = {
            "subsystem_name": "InvalidSystem",
            "priority": 1,
            "estimated_duration_seconds": 30
        }
        response = client.post("/ants/request", json=request_data)

        assert response.status_code == 422

    def test_return_ant_successful(self, client):
        # First request an ant
        request_data = {"subsystem_name": "Collection"}
        ant_response = client.post("/ants/request", json=request_data)
        ant_id = ant_response.json()["ant"]["id"]

        # Return the ant with food
        return_data = {
            "ant_id": ant_id,
            "returned_with_food": True,
            "died_in_mission": False
        }
        response = client.post("/ants/return", json=return_data)

        assert response.status_code == 200
        data = response.json()
        assert "returned with food" in data["message"]
        assert data["food_gained"] is True
        assert data["ant_died"] is False

    def test_return_ant_died_in_mission(self, client):
        # First request an ant
        request_data = {"subsystem_name": "Defense"}
        ant_response = client.post("/ants/request", json=request_data)
        ant_id = ant_response.json()["ant"]["id"]

        # Return the ant as dead
        return_data = {
            "ant_id": ant_id,
            "returned_with_food": False,
            "died_in_mission": True
        }
        response = client.post("/ants/return", json=return_data)

        assert response.status_code == 200
        data = response.json()
        assert "died in mission" in data["message"]
        assert data["food_gained"] is False
        assert data["ant_died"] is True

    def test_return_nonexistent_ant(self, client):
        return_data = {
            "ant_id": "nonexistent-id",
            "returned_with_food": False,
            "died_in_mission": False
        }
        response = client.post("/ants/return", json=return_data)

        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_request_emergency_ants(self, client):
        # Create some ants first
        client.post("/ants")
        client.post("/ants")

        emergency_data = {
            "requesting_subsystem": "Defense",
            "number_needed": 2,
            "max_wait_seconds": 30
        }
        response = client.post("/ants/emergency", json=emergency_data)

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        for ant_data in data:
            assert ant_data["reassigned"] is True
            assert ant_data["emergency_assignment"] is True
            assert ant_data["ant"]["assigned_to"] == "defense"

    def test_get_comprehensive_colony_status(self, client):
        # Create some ants in different states
        client.post("/ants")  # Free ant
        ant_response = client.post("/ants/request", json={"subsystem_name": "Defense"})

        response = client.get("/colony/status/comprehensive")

        assert response.status_code == 200
        data = response.json()

        expected_keys = {
            'total_ants', 'alive_ants', 'free_ants', 'assigned_ants', 'dead_ants',
            'max_ants', 'food_stock', 'can_create_more', 'emergency_mode',
            'ants_by_subsystem', 'ant_lifespan_minutes'
        }
        assert set(data.keys()) == expected_keys
        assert data["max_ants"] == 100
        assert data["food_stock"] > 0
        assert data["ant_lifespan_minutes"] == 1.5

    def test_get_ants_filtered_by_state(self, client):
        # Create ants in different states
        client.post("/ants")  # Free ant
        client.post("/ants/request", json={"subsystem_name": "S01_COM"})  # Assigned ant

        # Test getting free ants
        response = client.get("/ants?state=free")
        assert response.status_code == 200
        free_ants = response.json()
        assert len(free_ants) == 1
        assert free_ants[0]["state"] == "free"

        # Test getting assigned ants
        response = client.get("/ants?state=assigned")
        assert response.status_code == 200
        assigned_ants = response.json()
        assert len(assigned_ants) == 1
        assert assigned_ants[0]["state"] == "assigned"

    def test_configure_colony_parameters(self, client):
        config_params = "max_ants=50&food_stock=2000&ant_lifespan_minutes=2.0"
        response = client.put(f"/colony/config?{config_params}")

        assert response.status_code == 200
        data = response.json()
        assert data["changes"]["max_ants"] == 50
        assert data["changes"]["food_stock"] == 2000
        assert data["changes"]["ant_lifespan_minutes"] == 2.0

        # Verify changes were applied
        status = data["current_status"]
        assert status["max_ants"] == 50
        assert status["food_stock"] == 2000
        assert status["ant_lifespan_minutes"] == 2.0

    def test_configure_colony_invalid_parameters(self, client):
        # Test invalid max_ants
        response = client.put("/colony/config?max_ants=0")
        assert response.status_code == 400
        assert "must be at least 1" in response.json()["detail"]

        # Test negative food_stock
        response = client.put("/colony/config?food_stock=-10")
        assert response.status_code == 400
        assert "cannot be negative" in response.json()["detail"]

        # Test invalid lifespan
        response = client.put("/colony/config?ant_lifespan_minutes=0")
        assert response.status_code == 400
        assert "must be positive" in response.json()["detail"]

    def test_add_food_to_colony(self, client):
        initial_status = client.get("/colony/status/comprehensive").json()
        initial_food = initial_status["food_stock"]

        response = client.post("/colony/food/add?amount=100")

        assert response.status_code == 200
        data = response.json()
        assert data["total_food_stock"] == initial_food + 100
        assert "Added 100 food units" in data["message"]

    def test_add_invalid_food_amount(self, client):
        response = client.post("/colony/food/add?amount=0")
        assert response.status_code == 400
        assert "must be positive" in response.json()["detail"]

    def test_get_available_subsystems(self, client):
        response = client.get("/subsystems")

        assert response.status_code == 200
        data = response.json()

        assert "available_subsystems" in data
        assert "priority_explanation" in data

        subsystems = data["available_subsystems"]
        assert len(subsystems) == 3

        # Check that Defense has priority 1 (highest)
        defense = next(s for s in subsystems if s["name"] == "Defense")
        assert defense["priority_level"] == 1

    def test_cleanup_dead_ants_endpoint(self, client):
        # Create an ant and make it die (would need actual time passage in real scenario)
        client.post("/ants")

        response = client.post("/colony/cleanup")

        assert response.status_code == 200
        data = response.json()
        assert "Cleaned up" in data["message"]
        assert "remaining_ants" in data

    def test_ant_assignment_priority_system(self, client):
        # Create ants and assign to different priority subsystems
        defense_response = client.post("/ants/request", json={
            "subsystem_name": "Defense",
            "priority": 1
        })
        comm_response = client.post("/ants/request", json={
            "subsystem_name": "Communication",
            "priority": 2
        })
        collection_response = client.post("/ants/request", json={
            "subsystem_name": "Collection",
            "priority": 3
        })

        # All should succeed
        assert defense_response.status_code == 200
        assert comm_response.status_code == 200
        assert collection_response.status_code == 200

        # Check status shows proper distribution
        status_response = client.get("/colony/status/comprehensive")
        status = status_response.json()

        assert status["ants_by_subsystem"]["defense"] == 1
        assert status["ants_by_subsystem"]["communication"] == 1
        assert status["ants_by_subsystem"]["collection"] == 1

    # def test_backward_compatibility_endpoints(self, client):
    #     # Test that old endpoints still work
    #     response = client.get("/colony/status")
    #     assert response.status_code == 200

    #     # Should have the basic keys for backward compatibility
    #     data = response.json()
    #     basic_keys = {'total_ants', 'alive_ants', 'dead_ants', 'max_ants', 'can_create_more'}
    #     assert basic_keys.issubset(set(data.keys()))