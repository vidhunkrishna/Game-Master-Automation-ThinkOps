"""NPC Memory Manager - Stores and manages NPC memories of player interactions."""
from typing import Dict, List, Any


class NPCMemoryManager:
    """
    Manages memory for each NPC, storing past player interactions.
    Memory format: {npc_id: [{"action": "player_attack", "time": timestamp}, ...]}
    """

    def __init__(self):
        """Initialize memory manager with empty memory store."""
        self.npc_memories: Dict[str, List[Dict[str, Any]]] = {}

    def add_memory(self, npc_id: str, action: str, timestamp: int) -> None:
        """Add a memory entry for an NPC."""
        if npc_id not in self.npc_memories:
            self.npc_memories[npc_id] = []
        
        memory_entry = {
            "action": action,
            "time": timestamp
        }
        
        self.npc_memories[npc_id].append(memory_entry)
        print(f"NPC memory updated for {npc_id}: {action}")

    def get_recent_memory(self, npc_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent memories for an NPC, limited to the most recent entries."""
        if npc_id not in self.npc_memories:
            return []
        
        memories = self.npc_memories[npc_id]
        # Sort by time (most recent first) and limit
        sorted_memories = sorted(memories, key=lambda x: x["time"], reverse=True)
        return sorted_memories[:limit]

    def get_memory_for_action(self, npc_id: str, action: str) -> List[Dict[str, Any]]:
        """Get all memories of a specific action type for an NPC."""
        if npc_id not in self.npc_memories:
            return []
        
        return [mem for mem in self.npc_memories[npc_id] if mem["action"] == action]

    def update_memory_after_player_action(self, player_action: str, current_time: int) -> None:
        """Update memory for all NPCs after a player action."""
        # This should be called by the Head Orchestrator Agent
        for npc_id in self.npc_memories.keys():
            self.add_memory(npc_id, player_action, current_time)

    def has_memory_of_action(self, npc_id: str, action: str) -> bool:
        """Check if NPC has memory of a specific action."""
        memories = self.get_memory_for_action(npc_id, action)
        return len(memories) > 0

    def get_memory_summary(self, npc_id: str) -> Dict[str, int]:
        """Get a summary of action types remembered by the NPC."""
        if npc_id not in self.npc_memories:
            return {}
        
        summary = {}
        for memory in self.npc_memories[npc_id]:
            action = memory["action"]
            summary[action] = summary.get(action, 0) + 1
        
        return summary