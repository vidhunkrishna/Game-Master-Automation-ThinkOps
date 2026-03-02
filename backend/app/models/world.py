from pydantic import BaseModel
from typing import Dict, Any
from datetime import datetime


class NPCState(BaseModel):
    id: str
    name: str
    health: float
    mood: str
    mood_level: float
    position_x: float
    position_y: float
    goal: str
    last_action: str = "idle"


class WorldState(BaseModel):
    time: int
    time_of_day: str
    danger_level: float
    weather: str
    npcs: Dict[str, NPCState]
    events: list[str] = []
    
    class Config:
        json_schema_extra = {
            "example": {
                "time": 0,
                "time_of_day": "morning",
                "danger_level": 20.0,
                "weather": "sunny",
                "npcs": {
                    "npc_1": {
                        "id": "npc_1",
                        "name": "Trader Bob",
                        "health": 95.0,
                        "mood": "happy",
                        "mood_level": 75.0,
                        "position_x": 10.0,
                        "position_y": 20.0,
                        "goal": "find_food",
                        "last_action": "idle"
                    }
                },
                "events": []
            }
        }


class NPCAction(BaseModel):
    npc_id: str
    action_type: str
    target: str = "none"
    priority: float
    expected_outcome: str
    reasoning: str


class ActionResult(BaseModel):
    success: bool
    npc_id: str
    action_type: str
    world_state_changes: Dict[str, Any]
    message: str
