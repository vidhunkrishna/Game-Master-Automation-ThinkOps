"""Head Orchestrator Agent - World Governor."""
import asyncio
from typing import Dict, Any
from app.models.world import WorldState, NPCState, NPCAction, ActionResult
from app.agents.npc_agent import NPCDecisionAgent
from datetime import datetime


class HeadOrchestratorAgent:
    """
    Maintains global world state and coordinates agent communication.
    Handles simulation ticks and manages persistent memory.
    """
    
    def __init__(self):
        """Initialize orchestrator with default world state."""
        self.world_state = self._initialize_world_state()
        self.npc_agent = NPCDecisionAgent()
        self.tick_count = 0
        self.action_history: list[ActionResult] = []
        self.max_history_size = 100
        # structured event log for external consumption
        self.event_log: list[str] = []
        
    def _initialize_world_state(self) -> WorldState:
        """Initialize the world with default state and NPCs."""
        initial_npcs = {
            "npc_1": NPCState(
                id="npc_1",
                name="Trader Bob",
                health=95.0,
                mood="happy",
                mood_level=75.0,
                position_x=10.0,
                position_y=20.0,
                goal="find_food",
                last_action="idle"
            ),
            "npc_2": NPCState(
                id="npc_2",
                name="Guard Alice",
                health=100.0,
                mood="neutral",
                mood_level=50.0,
                position_x=50.0,
                position_y=50.0,
                goal="protect_area",
                last_action="patrol"
            ),
            "npc_3": NPCState(
                id="npc_3",
                name="Scout Charlie",
                health=80.0,
                mood="neutral",
                mood_level=60.0,
                position_x=30.0,
                position_y=40.0,
                goal="explore",
                last_action="idle"
            ),
        }
        
        return WorldState(
            time=0,
            time_of_day="morning",
            danger_level=20.0,
            weather="sunny",
            npcs=initial_npcs,
            events=["Simulation started"]
        )
    
    async def process_tick(self) -> dict:
        """
        Execute one simulation tick:
        1. Update time and environmental factors
        2. Request decisions from NPC agent
        3. Apply actions to world state
        4. Return updated world state
        """
        self.tick_count += 1
        
        # Update time and environment
        self._update_environment()
        
        # Process each NPC's decision
        last_action = None
        last_reason = ""
        for npc_id, npc in self.world_state.npcs.items():
            action = await self.npc_agent.decide_action(npc, self.world_state)

            # action is expected to be NPCAction per updated agent
            last_action = action.action_type
            last_reason = action.reasoning or action.expected_outcome
            log_line = f"[Time {self.world_state.time}] {npc.name} chose {action.action_type} because {last_reason}"
            self.event_log.append(log_line)

            result = self._apply_action(action)
            self.action_history.append(result)
        
        # Maintain history size
        if len(self.action_history) > self.max_history_size:
            self.action_history = self.action_history[-self.max_history_size:]
        
        # return enhanced structure with logging for compatibility
        return {
            "world_state": self.world_state,
            "last_action": last_action,
            "reason": last_reason,
            "events": self.event_log,
        }
    
    def _update_environment(self) -> None:
        """Update global environmental factors."""
        time_cycle = self.world_state.time % 24
        
        # Update time of day
        if time_cycle < 6:
            self.world_state.time_of_day = "night"
        elif time_cycle < 12:
            self.world_state.time_of_day = "morning"
        elif time_cycle < 18:
            self.world_state.time_of_day = "afternoon"
        else:
            self.world_state.time_of_day = "evening"
        
        # Gradually reduce danger if high
        if self.world_state.danger_level > 20:
            self.world_state.danger_level -= 1.0
        
        # Simulate passive health recovery
        for npc in self.world_state.npcs.values():
            if npc.health < 100 and npc.last_action == "idle":
                npc.health = min(100.0, npc.health + 2.0)
            
            # Mood stabilization
            if npc.mood_level < 50:
                npc.mood_level += 1.0
            elif npc.mood_level > 75:
                npc.mood_level -= 0.5
        
        self.world_state.time += 1
    
    def _apply_action(self, action: NPCAction) -> ActionResult:
        """Apply an NPC action to the world state."""
        npc = self.world_state.npcs.get(action.npc_id)
        
        if not npc:
            return ActionResult(
                success=False,
                npc_id=action.npc_id,
                action_type=action.action_type,
                world_state_changes={},
                message="NPC not found"
            )
        
        changes: Dict[str, Any] = {}
        
        if action.action_type == "move":
            npc.position_x += 5.0
            npc.position_y += 3.0
            changes["position"] = {"x": npc.position_x, "y": npc.position_y}
            message = f"{npc.name} moved to ({npc.position_x}, {npc.position_y})"
            
        elif action.action_type == "rest":
            npc.health = min(100.0, npc.health + 10.0)
            npc.mood_level = min(100.0, npc.mood_level + 5.0)
            changes["health"] = npc.health
            changes["mood_level"] = npc.mood_level
            message = f"{npc.name} rested and recovered health"
            
        elif action.action_type == "attack":
            npc.health -= 5.0
            self.world_state.danger_level += 10.0
            changes["health"] = npc.health
            changes["danger_level"] = self.world_state.danger_level
            message = f"{npc.name} attacked {action.target}"
            
        elif action.action_type == "flee":
            npc.position_x -= 10.0
            npc.position_y -= 10.0
            npc.mood = "scared"
            npc.mood_level = 20.0
            changes["position"] = {"x": npc.position_x, "y": npc.position_y}
            changes["mood"] = "scared"
            message = f"{npc.name} fled from danger"
            
        elif action.action_type == "trade":
            npc.mood = "happy"
            npc.mood_level = 80.0
            changes["mood"] = "happy"
            message = f"{npc.name} traded with {action.target}"
        
        elif action.action_type == "search_food":
            npc.mood_level = min(100.0, npc.mood_level + 5.0)
            npc.health = min(100.0, npc.health + 2.0)
            changes["mood_level"] = npc.mood_level
            changes["health"] = npc.health
            message = f"{npc.name} searched for food"
        
        elif action.action_type == "patrol":
            npc.position_x += 2.0
            npc.position_y += 2.0
            self.world_state.danger_level = max(0.0, self.world_state.danger_level - 3.0)
            changes["position"] = {"x": npc.position_x, "y": npc.position_y}
            changes["danger_level"] = self.world_state.danger_level
            message = f"{npc.name} patrolled the area"
            
        else:  # idle
            message = f"{npc.name} remained idle"
        
        npc.last_action = action.action_type
        self.world_state.events.append(message)
        
        # Keep only last 20 events
        if len(self.world_state.events) > 20:
            self.world_state.events = self.world_state.events[-20:]
        
        return ActionResult(
            success=True,
            npc_id=action.npc_id,
            action_type=action.action_type,
            world_state_changes=changes,
            message=message
        )
    
    def get_world_state(self) -> WorldState:
        """Get current world state."""
        return self.world_state
    
    def get_action_history(self) -> list[ActionResult]:
        """Get recent action history."""
        return self.action_history[-10:]  # Return last 10 actions
    
    def reset_simulation(self) -> None:
        """Reset simulation to initial state."""
        self.world_state = self._initialize_world_state()
        self.tick_count = 0
        self.action_history = []
