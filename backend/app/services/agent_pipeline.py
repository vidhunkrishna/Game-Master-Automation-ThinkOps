"""Agent Pipeline - Orchestrates all agents for player action processing."""
from typing import Dict, Any, List, Optional
from app.agents.npc_agent import NPCDecisionAgent
from app.agents.narrative_agent import NarrativeAgent
from app.agents.intelligence_agent import IntelligenceAgent
from app.services.world_state_manager import WorldStateManager
from app.database.db import db_manager
from app.models.world import WorldState, NPCState


class AgentPipeline:
    """
    Orchestrates all agents to process player actions and generate responses.
    Coordinates NPC decisions, narrative events, and intelligence analysis.
    """

    def __init__(
        self,
        orchestrator_agent=None,
        world_state_manager: Optional[WorldStateManager] = None,
    ):
        """
        Initialize agent pipeline.

        Args:
            orchestrator_agent: HeadOrchestratorAgent instance
            world_state_manager: WorldStateManager instance
        """
        self.orchestrator = orchestrator_agent
        self.world_state_manager = world_state_manager or WorldStateManager()
        self.npc_agent = NPCDecisionAgent()
        self.narrative_agent = NarrativeAgent()
        self.intelligence_agent = IntelligenceAgent()
        
        # Store player action history for behavior analysis
        self.player_action_history: Dict[str, List[Dict[str, Any]]] = {}

    async def process_player_action(self, player_action: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a player action through the entire agent pipeline.

        Args:
            player_action: Dictionary with player_id, action, and optional parameters

        Returns:
            dict: Pipeline result with NPC actions, story event, player type, and risk level
        """
        try:
            player_id = player_action.get("player_id", "player_1")
            action = player_action.get("action", "idle")

            # Step 1: Track player action history
            if player_id not in self.player_action_history:
                self.player_action_history[player_id] = []
            self.player_action_history[player_id].append({
                "action": action,
                "type": player_action.get("type", "other"),
            })

            # Step 2: Fetch current world state
            if self.orchestrator:
                world_state = self.orchestrator.world_state
            else:
                world_state_dict = self.world_state_manager.get_world_state()
                # Convert to WorldState object
                world_state = self._dict_to_world_state(world_state_dict)

            # Step 3: Get NPC decisions
            npc_actions = []
            for npc_id, npc in world_state.npcs.items():
                npc_action = await self.npc_agent.decide_action(npc, world_state)
                npc_actions.append(npc_action.model_dump())

            # Step 4: Predict player behavior type
            player_features = self.intelligence_agent.extract_player_features_from_history(
                self.player_action_history[player_id]
            )
            player_type_result = self.intelligence_agent.predict_player_type(player_features)
            player_type = player_type_result.get("player_type", "neutral")

            # Step 5: Predict risk level
            world_features = self.intelligence_agent.extract_world_features_from_state(
                self._world_state_to_dict(world_state)
            )
            risk_result = self.intelligence_agent.predict_risk_level(world_features)
            risk_level = risk_result.get("risk_level", "medium")

            # Step 6: Generate narrative event directly using the raw action
            # This allows the narrative agent to produce dynamic, action-specific events
            story_event = self.narrative_agent.generate_event(world_state, action)

            # Save event to database
            db_manager.save_event(story_event)

            # Step 7: Update world state
            if self.orchestrator:
                await self.orchestrator.process_tick()
            
            # Log event in database
            self.world_state_manager.log_event(story_event)
            
            # Update risk analytics
            avg_health = self._calculate_avg_npc_health(world_state)
            self.world_state_manager.update_risk_level(
                tick=world_state.time,
                danger_level=world_state.danger_level,
                risk_level=risk_level,
                weather=world_state.weather,
                avg_npc_health=avg_health,
                event_count=len(world_state.events),
            )

            # Build response
            response = {
                "success": True,
                "player_id": player_id,
                "player_action": action,
                "world_time": world_state.time,
                "npc_actions": npc_actions,
                "story_event": story_event,
                "player_type": {
                    "classification": player_type,
                    "confidence": player_type_result.get("confidence", 0.0),
                    "probabilities": player_type_result.get("all_probabilities", {}),
                },
                "risk_assessment": {
                    "risk_level": risk_level,
                    "danger_level": world_state.danger_level,
                    "confidence": risk_result.get("confidence", 0.75),
                },
                "world_state_summary": {
                    "danger_level": world_state.danger_level,
                    "time_of_day": world_state.time_of_day,
                    "weather": world_state.weather,
                    "npc_count": len(world_state.npcs),
                    "avg_npc_health": avg_health,
                },
            }

            # Save world state and NPC states to database
            db_manager.save_world_state(world_state)
            db_manager.save_npc_states(world_state.npcs)

            return response

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "player_id": player_action.get("player_id", "unknown"),
            }

    def _determine_event_type(self, action: str, risk_level: str) -> str:
        """
        Determine narrative event type based on player action and risk level.

        Args:
            action: Player action string
            risk_level: Current risk level

        Returns:
            str: Event type (conflict, exploration, social, environmental)
        """
        action_lower = action.lower()

        if "attack" in action_lower or "fight" in action_lower or "raid" in action_lower:
            return "conflict"
        elif "explore" in action_lower or "scout" in action_lower or "search" in action_lower:
            return "exploration"
        elif "trade" in action_lower or "talk" in action_lower or "interact" in action_lower:
            return "social"
        elif risk_level == "high":
            return "environmental"
        else:
            return "social"

    def _dict_to_world_state(self, world_dict: Dict[str, Any]) -> WorldState:
        """
        Convert dictionary to WorldState object.

        Args:
            world_dict: World state dictionary

        Returns:
            WorldState: Pydantic WorldState object
        """
        npcs = {}
        for npc_id, npc_data in world_dict.get("npcs", {}).items():
            npcs[npc_id] = NPCState(
                id=npc_data.get("id", npc_id),
                name=npc_data.get("name", "NPC"),
                health=float(npc_data.get("health", 100)),
                mood=npc_data.get("mood", "neutral"),
                mood_level=float(npc_data.get("mood_level", 50)),
                position_x=float(npc_data.get("position_x", 0)),
                position_y=float(npc_data.get("position_y", 0)),
                goal=npc_data.get("goal", "idle"),
                last_action=npc_data.get("last_action", "idle"),
            )

        return WorldState(
            time=world_dict.get("time", 0),
            time_of_day=world_dict.get("time_of_day", "morning"),
            danger_level=float(world_dict.get("danger_level", 20.0)),
            weather=world_dict.get("weather", "sunny"),
            npcs=npcs,
            events=world_dict.get("events", []),
        )

    def _world_state_to_dict(self, world_state: WorldState) -> Dict[str, Any]:
        """
        Convert WorldState object to dictionary.

        Args:
            world_state: WorldState object

        Returns:
            dict: World state dictionary
        """
        npcs_dict = {}
        for npc_id, npc in world_state.npcs.items():
            npcs_dict[npc_id] = {
                "id": npc.id,
                "name": npc.name,
                "health": npc.health,
                "mood": npc.mood,
                "mood_level": npc.mood_level,
                "position_x": npc.position_x,
                "position_y": npc.position_y,
                "goal": npc.goal,
                "last_action": npc.last_action,
            }

        return {
            "time": world_state.time,
            "time_of_day": world_state.time_of_day,
            "danger_level": world_state.danger_level,
            "weather": world_state.weather,
            "npcs": npcs_dict,
            "events": world_state.events,
        }

    def _calculate_avg_npc_health(self, world_state: WorldState) -> float:
        """
        Calculate average NPC health.

        Args:
            world_state: Current world state

        Returns:
            float: Average health
        """
        if not world_state.npcs:
            return 75.0

        total_health = sum(npc.health for npc in world_state.npcs.values())
        return total_health / len(world_state.npcs)

    def get_player_history(self, player_id: str) -> List[Dict[str, Any]]:
        """
        Get action history for a specific player.

        Args:
            player_id: Player identifier

        Returns:
            list: Action history
        """
        return self.player_action_history.get(player_id, [])

    def reset_player_history(self, player_id: str) -> Dict[str, Any]:
        """
        Reset action history for a player.

        Args:
            player_id: Player identifier

        Returns:
            dict: Reset result
        """
        if player_id in self.player_action_history:
            del self.player_action_history[player_id]
            return {
                "success": True,
                "message": f"History reset for {player_id}",
            }
        return {
            "success": False,
            "message": f"No history found for {player_id}",
        }
