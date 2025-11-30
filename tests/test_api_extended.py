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

    def test_concurrent_ant_requests(self, client):
        # Test that multiple subsystems can request ants simultaneously
        responses = []
        subsystems = ["Defense", "Communication", "Collection"]

        for subsystem in subsystems:
            response = client.post("/ants/request", json={
                "subsystem_name": subsystem,
                "priority": 1,
                "estimated_duration_seconds": 30
            })
            responses.append(response)

        for response in responses:
            assert response.status_code == 200
            assert response.json()["assignment_successful"] is True

        # Verify each subsystem has one ant
        status = client.get("/colony/status/comprehensive").json()
        for subsystem in ["defense", "communication", "collection"]:
            assert status["ants_by_subsystem"][subsystem] == 1

    def test_emergency_mode_activation_deactivation(self, client):
        # Activate emergency mode
        response = client.put("/colony/emergency?activate=true")
        assert response.status_code == 200
        assert response.json()["emergency_mode"] is True

        # Check that colony is in emergency mode
        status = client.get("/colony/status/comprehensive").json()
        assert status["emergency_mode"] is True

        # Deactivate emergency mode
        response = client.put("/colony/emergency?activate=false")
        assert response.status_code == 200
        assert response.json()["emergency_mode"] is False

    def test_food_consumption_during_ant_creation(self, client):
        initial_status = client.get("/colony/status/comprehensive").json()
        initial_food = initial_status["food_stock"]

        # Create an ant
        response = client.post("/ants")
        assert response.status_code == 200

        # Check that food was consumed
        final_status = client.get("/colony/status/comprehensive").json()
        assert final_status["food_stock"] == initial_food - 10

    def test_ant_lifespan_configuration(self, client):
        # Set a specific lifespan
        response = client.put("/colony/config?ant_lifespan_minutes=3.5")
        assert response.status_code == 200

        # Create an ant and verify its expiry time
        ant_response = client.post("/ants")
        ant_data = ant_response.json()

        # Get ant details
        ant_id = ant_data["id"]
        response = client.get(f"/ants/{ant_id}")
        assert response.status_code == 200

        ant_details = response.json()
        assert "expiry_time" in ant_details

    def test_subsystem_priority_during_emergency(self, client):
        # Create limited ants
        for _ in range(3):
            client.post("/ants")

        # Activate emergency mode
        client.put("/colony/emergency?activate=true")

        # Request emergency ants for Defense (highest priority)
        response = client.post("/ants/emergency", json={
            "requesting_subsystem": "Defense",
            "number_needed": 3,
            "max_wait_seconds": 10
        })

        assert response.status_code == 200
        ants = response.json()
        assert len(ants) == 3

        for ant in ants:
            assert ant["emergency_assignment"] is True
            assert ant["ant"]["assigned_to"] == "defense"

    def test_invalid_subsystem_in_emergency_request(self, client):
        response = client.post("/ants/emergency", json={
            "requesting_subsystem": "InvalidSubsystem",
            "number_needed": 1,
            "max_wait_seconds": 10
        })

        assert response.status_code == 400
        assert "Unknown subsystem" in response.json()["detail"]

    def test_return_ant_without_food_no_death(self, client):
        # Request an ant
        ant_response = client.post("/ants/request", json={"subsystem_name": "Collection"})
        ant_id = ant_response.json()["ant"]["id"]

        initial_food = client.get("/colony/status/comprehensive").json()["food_stock"]

        # Return ant without food and not dead
        response = client.post("/ants/return", json={
            "ant_id": ant_id,
            "returned_with_food": False,
            "died_in_mission": False
        })

        assert response.status_code == 200
        data = response.json()
        assert data["food_gained"] is False
        assert data["ant_died"] is False

        # Verify food stock unchanged
        final_food = client.get("/colony/status/comprehensive").json()["food_stock"]
        assert final_food == initial_food

    def test_get_specific_ant_details(self, client):
        # Create an ant
        ant_response = client.post("/ants")
        ant_id = ant_response.json()["id"]

        # Get specific ant details
        response = client.get(f"/ants/{ant_id}")
        assert response.status_code == 200

        ant_data = response.json()
        assert ant_data["id"] == ant_id
        assert ant_data["state"] == "free"
        assert "created_at" in ant_data
        assert "expiry_time" in ant_data

    def test_get_nonexistent_ant(self, client):
        response = client.get("/ants/nonexistent-id")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_subsystem_statistics_endpoint(self, client):
        # Create ants and assign to different subsystems
        client.post("/ants/request", json={"subsystem_name": "Defense"})
        client.post("/ants/request", json={"subsystem_name": "Defense"})
        client.post("/ants/request", json={"subsystem_name": "Communication"})

        response = client.get("/subsystems/statistics")
        assert response.status_code == 200

        stats = response.json()
        assert "subsystem_statistics" in stats
        assert stats["subsystem_statistics"]["defense"]["assigned_ants"] == 2
        assert stats["subsystem_statistics"]["communication"]["assigned_ants"] == 1
        assert stats["subsystem_statistics"]["collection"]["assigned_ants"] == 0

    def test_batch_ant_creation(self, client):
        response = client.post("/ants/batch?count=5")
        assert response.status_code == 200

        data = response.json()
        assert len(data["created_ants"]) == 5
        assert data["total_created"] == 5

        # Verify all ants were created
        status = client.get("/colony/status/comprehensive").json()
        assert status["total_ants"] == 5

    def test_batch_ant_creation_exceeds_capacity(self, client):
        # Set low capacity
        client.put("/colony/config?max_ants=3")

        response = client.post("/ants/batch?count=5")
        assert response.status_code == 409
        assert "Cannot create 5 ants" in response.json()["detail"]

    def test_reassign_ant_to_different_subsystem(self, client):
        # Create and assign ant to Communication
        ant_response = client.post("/ants/request", json={"subsystem_name": "Communication"})
        ant_id = ant_response.json()["ant"]["id"]

        # Reassign to Defense
        response = client.put(f"/ants/{ant_id}/reassign", json={
            "new_subsystem": "Defense",
            "priority": 1
        })

        assert response.status_code == 200
        data = response.json()
        assert data["ant"]["assigned_to"] == "defense"
        assert "Reassigned ant" in data["message"]

    def test_colony_reset_endpoint(self, client):
        # Create some ants and modify colony state
        client.post("/ants/batch?count=3")
        client.put("/colony/config?food_stock=500")

        # Reset colony
        response = client.post("/colony/reset")
        assert response.status_code == 200

        # Verify reset
        status = client.get("/colony/status/comprehensive").json()
        assert status["total_ants"] == 0
        assert status["food_stock"] == 1000  # Default value
        assert status["max_ants"] == 100  # Default value