from fastapi import APIRouter, HTTPException, Depends
from app.models.world import WorldState, NPCAction

router = APIRouter(prefix="/api", tags=["game"])

def get_orchestrator():
    from app.main import orchestrator
    return orchestrator


@router.get("/world/state")
async def get_world_state(orchestrator = Depends(get_orchestrator)) -> WorldState:
    return orchestrator.get_world_state()


@router.post("/world/tick")
async def process_simulation_tick(orchestrator = Depends(get_orchestrator)) -> dict:
    try:
        updated_state = await orchestrator.process_tick()
        return updated_state
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/world/state/summary")
async def get_world_summary(orchestrator = Depends(get_orchestrator)) -> dict:
    state = orchestrator.get_world_state()
    return {
        "time": state.time,
        "time_of_day": state.time_of_day,
        "danger_level": state.danger_level,
        "weather": state.weather,
        "npc_count": len(state.npcs),
        "event_count": len(state.events),
        "last_event": state.events[-1] if state.events else "None"
    }


@router.get("/world/history")
async def get_action_history(orchestrator = Depends(get_orchestrator)) -> list:
    history = orchestrator.get_action_history()
    return [
        {
            "npc_id": action.npc_id,
            "action_type": action.action_type,
            "message": action.message,
            "success": action.success
        }
        for action in history
    ]


@router.post("/world/reset")
async def reset_simulation(orchestrator = Depends(get_orchestrator)) -> dict:
    orchestrator.reset_simulation()
    return {"message": "Simulation reset successfully", "world_state": orchestrator.get_world_state()}


@router.get("/npc/{npc_id}")
async def get_npc_state(npc_id: str, orchestrator = Depends(get_orchestrator)) -> dict:
    state = orchestrator.get_world_state()
    npc = state.npcs.get(npc_id)
    
    if not npc:
        raise HTTPException(status_code=404, detail=f"NPC {npc_id} not found")
    
    return npc.dict()


@router.get("/npcs/all")
async def get_all_npcs(orchestrator = Depends(get_orchestrator)) -> list:
    state = orchestrator.get_world_state()
    return [npc.dict() for npc in state.npcs.values()]


@router.get("/events")
async def get_recent_events(limit: int = 10, orchestrator = Depends(get_orchestrator)) -> list[str]:
    state = orchestrator.get_world_state()
    return state.events[-limit:]
