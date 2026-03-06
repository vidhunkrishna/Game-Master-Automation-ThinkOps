"""FastAPI routes for agent operations."""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional
from app.services.agent_pipeline import AgentPipeline
from app.services.world_state_manager import WorldStateManager


# Initialize router
router = APIRouter(prefix="/agent", tags=["agent"])

# Global instances
_pipeline: Optional[AgentPipeline] = None
_world_state_manager: Optional[WorldStateManager] = None


def get_pipeline() -> AgentPipeline:
    """Dependency to get the agent pipeline."""
    global _pipeline
    if _pipeline is None:
        _pipeline = AgentPipeline(world_state_manager=get_world_state_manager())
    return _pipeline


def get_world_state_manager() -> WorldStateManager:
    """Dependency to get the world state manager."""
    global _world_state_manager
    if _world_state_manager is None:
        _world_state_manager = WorldStateManager()
    return _world_state_manager


# Pydantic models for request/response
class PlayerActionRequest(BaseModel):
    """Request model for player actions."""
    player_id: str
    action: str
    action_type: Optional[str] = None
    target: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "player_id": "player_1",
                "action": "explore",
                "action_type": "explore",
                "target": "north",
            }
        }


class PlayerActionResponse(BaseModel):
    """Response model for player actions."""
    success: bool
    player_id: str
    player_action: str
    world_time: int
    npc_actions: list
    story_event: Dict[str, Any]
    player_type: Dict[str, Any]
    risk_assessment: Dict[str, Any]
    world_state_summary: Dict[str, Any]
    error: Optional[str] = None


@router.post("/player_action", response_model=PlayerActionResponse)
async def process_player_action(
    request: PlayerActionRequest,
    pipeline: AgentPipeline = Depends(get_pipeline),
) -> Dict[str, Any]:
    """
    Process a player action through the agent pipeline.

    This endpoint:
    1. Receives player action input
    2. Sends to AgentPipeline for processing
    3. Coordinates NPC decisions
    4. Analyzes player behavior
    5. Predicts risk level
    6. Generates narrative event
    7. Returns comprehensive response

    Args:
        request: Player action request with player_id and action

    Returns:
        Dict: Response including NPC actions, story event, player type, and risk level

    Example request:
        {
            "player_id": "player_1",
            "action": "explore",
            "action_type": "explore",
            "target": "north"
        }

    Example response:
        {
            "success": true,
            "player_id": "player_1",
            "player_action": "explore",
            "world_time": 5,
            "npc_actions": [...],
            "story_event": {
                "event_id": "...",
                "description": "...",
                "severity": "low",
                "affected_npcs": [...]
            },
            "player_type": {
                "classification": "explorer",
                "confidence": 0.85,
                "probabilities": {...}
            },
            "risk_assessment": {
                "risk_level": "low",
                "danger_level": 20.0,
                "confidence": 0.75
            },
            "world_state_summary": {
                "danger_level": 20.0,
                "time_of_day": "morning",
                "weather": "sunny",
                "npc_count": 3,
                "avg_npc_health": 91.67
            }
        }
    """
    # Convert request to dictionary
    action_dict = {
        "player_id": request.player_id,
        "action": request.action,
        "type": request.action_type or request.action,
    }

    # Process action through pipeline
    result = await pipeline.process_player_action(action_dict)

    if not result.get("success"):
        raise HTTPException(
            status_code=400,
            detail=result.get("error", "Failed to process player action"),
        )

    return result


@router.get("/player/{player_id}/history")
async def get_player_history(
    player_id: str,
    pipeline: AgentPipeline = Depends(get_pipeline),
) -> Dict[str, Any]:
    """
    Get action history for a specific player.

    Args:
        player_id: Player identifier

    Returns:
        dict: Player action history
    """
    history = pipeline.get_player_history(player_id)
    return {
        "success": True,
        "player_id": player_id,
        "action_count": len(history),
        "history": history,
    }


@router.post("/player/{player_id}/reset_history")
async def reset_player_history(
    player_id: str,
    pipeline: AgentPipeline = Depends(get_pipeline),
) -> Dict[str, Any]:
    """
    Reset action history for a player.

    Args:
        player_id: Player identifier

    Returns:
        dict: Reset result
    """
    result = pipeline.reset_player_history(player_id)
    return result


@router.get("/world/state")
async def get_world_state(
    manager: WorldStateManager = Depends(get_world_state_manager),
) -> Dict[str, Any]:
    """
    Get current world state.

    Returns:
        dict: Current world state including NPCs, danger level, weather, etc.
    """
    return manager.get_world_state()


@router.get("/world/events")
async def get_world_events(
    limit: int = 20,
    manager: WorldStateManager = Depends(get_world_state_manager),
) -> Dict[str, Any]:
    """
    Get recent world events.

    Args:
        limit: Maximum number of events to retrieve

    Returns:
        dict: Recent event history
    """
    return manager.get_event_history(limit=limit)


@router.post("/world/initialize")
async def initialize_world(
    world_state: Dict[str, Any],
    manager: WorldStateManager = Depends(get_world_state_manager),
) -> Dict[str, Any]:
    """
    Initialize world state in database.

    Args:
        world_state: Initial world state dictionary

    Returns:
        dict: Initialization result
    """
    return manager.initialize_world(world_state)


@router.post("/world/reset")
async def reset_world(
    manager: WorldStateManager = Depends(get_world_state_manager),
) -> Dict[str, Any]:
    """
    Reset world state (clear all data).

    Returns:
        dict: Reset result
    """
    return manager.clear_world()


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint.

    Returns:
        dict: Service status
    """
    return {
        "status": "healthy",
        "service": "agent-pipeline",
        "version": "1.0.0",
    }
