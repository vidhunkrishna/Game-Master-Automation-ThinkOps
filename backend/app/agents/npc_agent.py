"""NPC Decision Agent - Makes goal-driven action decisions."""
import asyncio
from typing import Dict, Any, Optional
from app.models.world import WorldState, NPCState, NPCAction
from app.services.npc_memory_manager import NPCMemoryManager


class NPCDecisionAgent:
    """
    Goal-driven NPC agent that uses behavior tree logic and memory
    to decide actions based on world state and past interactions.
    """

    def __init__(self, memory_manager: Optional[NPCMemoryManager] = None):
        """Initialize NPC decision agent."""
        self.memory_manager = memory_manager
        self.decision_rules = self._setup_rules()
        # previous_decisions now stores the last chosen action key (string)
        self.previous_decisions: Dict[str, str] = {}
        self.decision_rules = self._setup_rules()
        # previous_decisions now stores the last chosen action key (string)
        self.previous_decisions: Dict[str, str] = {}
    
    def _setup_rules(self) -> Dict[str, callable]:
        """Define decision-making rules for different goals."""
        return {
            "find_food": self._decide_find_food,
            "protect_area": self._decide_protect_area,
            "explore": self._decide_explore,
            "survive": self._decide_survive,
        }
    
    async def decide_action(self, npc: NPCState, world_state: WorldState) -> NPCAction:
        """
        Decide action using behavior tree logic:
        1. Check danger level
        2. Check health
        3. Check memory of player actions
        4. Check mood
        5. Default to patrol
        """
        print("Behavior tree decision executed")
        
        # Behavior Tree Logic
        chosen_action = self._evaluate_behavior_tree(npc, world_state)
        
        # Apply repetition penalty
        previous = self.previous_decisions.get(npc.id)
        if previous and previous == chosen_action:
            # If same action as last time, sometimes choose alternative
            alternatives = ["patrol", "rest", "idle"]
            if chosen_action in alternatives:
                alternatives.remove(chosen_action)
            chosen_action = alternatives[0] if alternatives else "idle"
        
        self.previous_decisions[npc.id] = chosen_action
        
        reasoning = f"Behavior tree selected: {chosen_action}"
        
        return NPCAction(
            npc_id=npc.id,
            action_type=chosen_action,
            target="none",
            priority=1.0,
            expected_outcome=f"Executing {chosen_action}",
            reasoning=reasoning,
        )
    
    def _evaluate_behavior_tree(self, npc: NPCState, world_state: WorldState) -> str:
        """Evaluate behavior tree nodes in priority order."""
        
        # 1. High Danger Check
        if world_state.danger_level > 70:
            return "defend"
        
        # 2. Low Health Check
        if npc.health < 30:
            return "retreat"
        
        # 3. Memory-based hostility check
        if self.memory_manager and self.memory_manager.has_memory_of_action(npc.id, "player_attack"):
            return "hostile"
        
        # 4. Memory-based friendliness check
        if self.memory_manager and self.memory_manager.has_memory_of_action(npc.id, "player_trade"):
            if npc.mood_level > 60:
                return "assist"
        
        # 5. Mood-based social behavior
        if npc.mood_level > 60:
            return "assist"
        
        # 6. Default patrol behavior
        return "patrol"
    
    def _generate_candidate_actions(self, npc: NPCState, world_state: WorldState) -> list[NPCAction]:
        """Generate possible actions based on NPC state and goal."""
        actions = []
        
        # Health-based actions
        if npc.health < 30:
            actions.append(NPCAction(
                npc_id=npc.id,
                action_type="rest",
                target="none",
                priority=0.0,
                expected_outcome="Recover health",
                reasoning="Low health requires rest"
            ))
        
        # Goal-based actions
        goal_action_generator = self.decision_rules.get(npc.goal)
        if goal_action_generator:
            actions.extend(goal_action_generator(npc, world_state))
        
        # Danger-based actions
        if world_state.danger_level > 70:
            actions.append(NPCAction(
                npc_id=npc.id,
                action_type="flee",
                target="none",
                priority=0.0,
                expected_outcome="Escape danger",
                reasoning="High danger level requires escape"
            ))
        
        # Default idle action
        if not actions:
            actions.append(NPCAction(
                npc_id=npc.id,
                action_type="idle",
                target="none",
                priority=0.0,
                expected_outcome="Wait",
                reasoning="No immediate threats or goals"
            ))
        
        return actions
    
    def _decide_find_food(self, npc: NPCState, world_state: WorldState) -> list[NPCAction]:
        """Generate actions for food-seeking goal."""
        actions = []
        
        actions.append(NPCAction(
            npc_id=npc.id,
            action_type="move",
            target="food_source",
            priority=0.0,
            expected_outcome="Find food",
            reasoning="Moving to search for food sources"
        ))
        
        # Look for other NPCs to trade with
        for other_npc_id in world_state.npcs.keys():
            if other_npc_id != npc.id:
                actions.append(NPCAction(
                    npc_id=npc.id,
                    action_type="trade",
                    target=other_npc_id,
                    priority=0.0,
                    expected_outcome="Obtain food",
                    reasoning=f"Attempt to trade with {other_npc_id}"
                ))
        
        return actions
    
    def _decide_protect_area(self, npc: NPCState, world_state: WorldState) -> list[NPCAction]:
        """Generate actions for area protection goal."""
        actions = []
        
        # If danger is high, attack potential threats
        if world_state.danger_level > 50:
            actions.append(NPCAction(
                npc_id=npc.id,
                action_type="attack",
                target="threat",
                priority=0.0,
                expected_outcome="Eliminate threat",
                reasoning="Protecting area from threats"
            ))
        else:
            # Patrol area
            actions.append(NPCAction(
                npc_id=npc.id,
                action_type="move",
                target="patrol_route",
                priority=0.0,
                expected_outcome="Cover patrol area",
                reasoning="Patrolling to maintain security"
            ))
        
        return actions
    
    def _decide_explore(self, npc: NPCState, world_state: WorldState) -> list[NPCAction]:
        """Generate actions for exploration goal."""
        actions = []
        
        actions.append(NPCAction(
            npc_id=npc.id,
            action_type="move",
            target="new_location",
            priority=0.0,
            expected_outcome="Discover new areas",
            reasoning="Exploring new regions of the world"
        ))
        
        return actions
    
    def _decide_survive(self, npc: NPCState, world_state: WorldState) -> list[NPCAction]:
        """Generate actions for survival goal."""
        actions = []
        
        if npc.health < 50:
            actions.append(NPCAction(
                npc_id=npc.id,
                action_type="rest",
                target="none",
                priority=0.0,
                expected_outcome="Recover health",
                reasoning="Must survive - prioritizing health"
            ))
        else:
            actions.append(NPCAction(
                npc_id=npc.id,
                action_type="move",
                target="safe_zone",
                priority=0.0,
                expected_outcome="Reach safety",
                reasoning="Seeking safe location"
            ))
        
        return actions
    
    def _score_action(self, action: NPCAction, npc: NPCState, world_state: WorldState) -> float:
        """
        Calculate utility score for an action (0-100).
        Considers health, mood, world state, and action appropriateness.
        """
        score = 50.0  # Base score
        
        # Health-related scoring
        if npc.health < 30 and action.action_type == "rest":
            score += 30.0  # High priority for rest when health is low
        elif npc.health < 50 and action.action_type in ["flee", "rest"]:
            score += 15.0
        elif npc.health > 80 and action.action_type == "rest":
            score -= 20.0  # Less priority if already healthy
        
        # Mood-related scoring
        if npc.mood_level < 30 and action.action_type == "trade":
            score += 20.0  # Trading improves mood
        elif npc.mood == "scared" and action.action_type == "flee":
            score += 25.0
        
        # Goal alignment
        if action.action_type == "move" and npc.goal in ["explore", "find_food"]:
            score += 15.0
        elif action.action_type == "attack" and npc.goal == "protect_area":
            score += 20.0
        
        # Danger level consideration
        if world_state.danger_level > 70:
            if action.action_type in ["flee", "rest"]:
                score += 20.0
            elif action.action_type == "attack":
                score += 10.0
        
        # Time of day consideration
        if world_state.time_of_day == "night":
            if action.action_type == "rest":
                score += 10.0
            elif action.action_type == "explore":
                score -= 15.0
        
        # Repetition penalty (avoid doing same action twice)
        previous_action = self.previous_decisions.get(npc.id)
        if previous_action and previous_action == action.action_type:
            score -= 10.0
        
        # Clamp score between 0 and 100
        return max(0.0, min(100.0, score))
