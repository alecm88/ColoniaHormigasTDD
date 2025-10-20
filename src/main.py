from fastapi import FastAPI, HTTPException
from typing import Dict, List, Any
from src.colony import Colony
from src.ant import Ant

app = FastAPI(title="Ant Colony API", version="1.0.0")

# Global colony instance with default max of 10 ants
colony = Colony(max_ants=10)


@app.get("/")
async def root():
    return {"message": "Ant Colony Management System"}


@app.post("/ants", response_model=Dict[str, Any])
async def create_ant():
    """Create a new ant if colony is not at maximum capacity"""
    ant = colony.create_ant()
    if ant is None:
        raise HTTPException(
            status_code=409,
            detail="Cannot create ant: colony is at maximum capacity"
        )
    return ant.to_dict()


@app.get("/ants", response_model=List[Dict[str, Any]])
async def get_all_ants():
    """Get all alive ants in the colony"""
    return [ant.to_dict() for ant in colony.get_alive_ants()]


@app.get("/ants/{ant_id}", response_model=Dict[str, Any])
async def get_ant(ant_id: str):
    """Get a specific ant by ID"""
    ant = colony.get_ant_by_id(ant_id)
    if ant is None:
        raise HTTPException(status_code=404, detail="Ant not found or dead")
    return ant.to_dict()


@app.get("/colony/status", response_model=Dict[str, Any])
async def get_colony_status():
    """Get colony status including ant counts and capacity"""
    return colony.get_status()


@app.post("/colony/cleanup")
async def cleanup_dead_ants():
    """Manually trigger cleanup of dead ants"""
    cleaned_count = colony.cleanup_dead_ants()
    return {"message": f"Cleaned up {cleaned_count} dead ants"}


@app.put("/colony/config")
async def configure_colony(max_ants: int):
    """Configure the maximum number of ants in the colony"""
    if max_ants < 1:
        raise HTTPException(status_code=400, detail="max_ants must be at least 1")

    colony.max_ants = max_ants
    # Clean up excess ants if new limit is lower
    if len(colony.get_alive_ants()) > max_ants:
        colony.cleanup_dead_ants()

    return {"message": f"Colony configured for maximum {max_ants} ants"}