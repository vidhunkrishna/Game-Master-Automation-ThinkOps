"""Narrative Agent - Generates dynamic story events."""
import uuid
import random
import os
import requests
import json
from typing import Optional
from app.models.world import WorldState
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class NarrativeAgent:
    """
    Generates context-aware story events based on world state and player actions.
    Uses procedural event pools with randomness so outcomes vary each time.
    """

    def __init__(self):
        """Initialize narrative agent with event pools."""
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.ollama_url = "http://localhost:11434/api/generate"
        self.event_templates = self._setup_templates()
        # procedural action-specific pools
        self.explore_events = [
            "A scout finds unusual footprints near ancient ruins.",
            "A hidden waterfall reveals a cave entrance.",
            "A rare herb with healing properties is discovered.",
            "A mysterious shrine is uncovered deep in the forest.",
            "A wandering traveler shares rumors about hidden treasure."
        ]
        self.dangerous_explore_events = [
            "A venomous serpent strikes from the undergrowth.",
            "An ambush by bandits forces the party to flee.",
            "A sudden sinkhole appears beneath the explorers' feet.",
        ]
        self.combat_events = [
            "Village defenders mobilize to repel the attack.",
            "A fire spreads through the outer buildings.",
            "Hidden militia forces counterattack unexpectedly.",
            "Civilians flee while guards secure the main gate."
        ]
        self.trade_events = [
            "A merchant offers a rare artifact at a high price.",
            "A caravan arrives with exotic goods.",
            "A dispute erupts between rival traders.",
            "A new trade opportunity appears in the market."
        ]
        self.stealth_events = [
            "A guard patrol nearly discovers the intruder.",
            "A hidden passage is found beneath the castle walls.",
            "A secret document is uncovered in the archives.",
            "A suspicious servant begins searching the corridors."
        ]
        self.severity_levels = ["low", "medium", "high"]

    def generate_ollama_story(self, world_state: WorldState, action: str) -> str:
        """Generate a story event using Ollama LLM."""
        print("Ollama narrative generated")
        
        prompt = f"""You are an AI narrative engine for a simulation game.

Generate ONE short fantasy story event in ONE sentence with a maximum of 20 words based on the following world state.

Player Action: {action}
World Time: {world_state.time}
Time of Day: {world_state.time_of_day}
Weather: {world_state.weather}
Danger Level: {world_state.danger_level}
NPC Count: {len(world_state.npcs)}

Output only the single sentence event."""
        
        payload = {
            "model": "phi3",
            "prompt": prompt,
            "stream": False
        }
        
        try:
            response = requests.post(self.ollama_url, json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()
            description = data.get("response", "")
            # safe cleanup: strip, capitalize, word-limit
            if description:
                description = description.strip()
                # capitalize first letter
                description = description[0].upper() + description[1:]
                description = " ".join(description.split()[:20])
            return description
        except Exception as e:
            print(f"Ollama failed — using fallback event: {e}")
            return None

    def generate_llm_story(self, world_state: WorldState, action: str) -> str:
        """Generate a story event using OpenAI LLM (fallback)."""
        print("[NarrativeAgent] Generating story using OpenAI fallback")
        prompt = f"""You are an AI narrative engine for a dynamic simulation game.
Generate ONE short fantasy story event in ONE sentence with a maximum of 20 words based on the following world state.

Player Action: {action}
World Time: {world_state.time}
Time of Day: {world_state.time_of_day}
Weather: {world_state.weather}
Danger Level: {world_state.danger_level}
NPC Count: {len(world_state.npcs)}

Output only the single sentence event."""        
        messages = [
            {"role": "system", "content": "You are an AI narrative generator that creates dynamic game events."},
            {"role": "user", "content": prompt}
        ]
        
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=80,
            temperature=0.9
        )
        return response.choices[0].message.content.strip()

    def _setup_templates(self) -> dict:
        """Define event templates and narrative patterns."""
        return {
            "conflict": self._generate_conflict_event,
            "exploration": self._generate_exploration_event,
            "social": self._generate_social_event,
            "environmental": self._generate_environmental_event,
        }

    def generate_event(
        self, world_state: WorldState, event_type: str = "exploration"
    ) -> dict:
        """
        Generate a context-aware story event.

        Args:
            world_state: Current world state
            event_type: Either a specific player action (explore_forest, attack_village,
                        trade_market, sneak_into_castle) or a generic category (conflict,
                        exploration, social, environmental).

        Returns:
            dict: Event dictionary with id, description, severity, event_type, and timestamp
        """
        # if we recognize a player action, use procedural pools
        action = event_type.lower()
        if action in [
            "explore_forest",
            "attack_village",
            "trade_market",
            "sneak_into_castle",
        ]:
            return self._generate_action_event(world_state, action)
        # otherwise fall back to old template system
        generator = self.event_templates.get(action, self._generate_exploration_event)
        return generator(world_state)

    def _generate_conflict_event(self, world_state: WorldState) -> dict:
        """Generate a conflict-type story event."""
        npc_list = list(world_state.npcs.keys())
        affected_npcs = npc_list[:2] if len(npc_list) >= 2 else npc_list

        severity_map = {
            "high": "high" if world_state.danger_level > 60 else "medium",
            "medium": "medium" if world_state.danger_level > 30 else "low",
        }
        severity = severity_map.get("medium", "low")

        conflict_descriptions = [
            f"A tense standoff erupts between {len(affected_npcs)} NPCs over scarce resources.",
            f"Competition intensifies as NPCs vie for control in the {world_state.weather} weather.",
            f"Ideological differences spark debate among the settlement inhabitants.",
        ]

        return {
            "event_id": str(uuid.uuid4()),
            "description": conflict_descriptions[
                len(affected_npcs) % len(conflict_descriptions)
            ],
            "severity": severity,
            "affected_npcs": affected_npcs,
            "event_type": "conflict",
            "timestamp": world_state.time,
        }

    def _generate_exploration_event(self, world_state: WorldState) -> dict:
        """Generate an exploration-type story event."""
        npc_list = list(world_state.npcs.keys())
        affected_npcs = [npc_list[0]] if npc_list else []

        severity = "low"

        exploration_descriptions = [
            "A scout discovers a hidden cache of supplies in an unexplored region.",
            "Ancient ruins are uncovered, revealing fragments of forgotten history.",
            "New territory opens up for settlement and resource gathering.",
            "Strange markings suggest previous civilizations once thrived here.",
        ]

        return {
            "event_id": str(uuid.uuid4()),
            "description": exploration_descriptions[world_state.time % len(exploration_descriptions)],
            "severity": severity,
            "affected_npcs": affected_npcs,
            "event_type": "exploration",
            "timestamp": world_state.time,
        }

    def _generate_social_event(self, world_state: WorldState) -> dict:
        """Generate a social interaction-type story event."""
        npc_list = list(world_state.npcs.keys())
        affected_npcs = npc_list[:3] if len(npc_list) >= 3 else npc_list

        severity = "low"

        social_descriptions = [
            "A celebration lifts the spirits of the entire community.",
            "NPCs gather to share knowledge and strengthen bonds.",
            "A mentor takes a younger community member under their wing.",
            "Trade negotiations begin between different groups.",
        ]

        return {
            "event_id": str(uuid.uuid4()),
            "description": social_descriptions[
                sum(len(npc) for npc in affected_npcs) % len(social_descriptions)
            ],
            "severity": severity,
            "affected_npcs": affected_npcs,
            "event_type": "social",
            "timestamp": world_state.time,
        }

    def _generate_environmental_event(self, world_state: WorldState) -> dict:
        """Generate an environmental-type story event."""
        npc_list = list(world_state.npcs.keys())
        affected_npcs = npc_list

        # Severity based on weather and danger level
        if world_state.danger_level > 70 or "storm" in world_state.weather.lower():
            severity = "high"
        elif world_state.danger_level > 40:
            severity = "medium"
        else:
            severity = "low"

        environmental_descriptions = [
            f"A sudden weather shift brings {world_state.weather} conditions across the land.",
            f"Environmental hazards increase as danger levels rise to {world_state.danger_level}.",
            f"Natural resources become {'scarce' if world_state.danger_level > 50 else 'abundant'} due to current conditions.",
            f"Seasonal changes affect the availability of food and shelter.",
        ]

        return {
            "event_id": str(uuid.uuid4()),
            "description": environmental_descriptions[
                int(world_state.danger_level) % len(environmental_descriptions)
            ],
            "severity": severity,
            "affected_npcs": affected_npcs,
            "event_type": "environmental",
            "timestamp": world_state.time,
        }
    
    def _generate_action_event(self, world_state: WorldState, action: str) -> dict:
        """Generate a dynamic event based on the specific player action."""
        npc_list = list(world_state.npcs.keys())
        affected_npcs = random.sample(npc_list, min(len(npc_list), 2)) if npc_list else []

        # choose severity randomly
        severity = random.choice(self.severity_levels)

        # select description based on action and world state
        try:
            ollama_description = self.generate_ollama_story(world_state, action)
            if ollama_description:
                description = ollama_description
            else:
                raise Exception("Ollama returned empty response")
        except Exception as e:
            print(f"Ollama failed — using fallback event: {e}")
            if action == "explore_forest":
                description = random.choice(self.explore_events)
            elif action == "attack_village":
                description = random.choice(self.combat_events)
            elif action == "trade_market":
                description = random.choice(self.trade_events)
            elif action == "sneak_into_castle":
                description = random.choice(self.stealth_events)
            else:
                # fallback to generic exploration if unknown
                description = random.choice(self.explore_events)

        # modify based on time of day
        if world_state.time_of_day == "night":
            description += " The darkness makes the situation more tense."

        # influence severity based on NPC mood
        if world_state.npcs:
            # calculate average mood level
            avg_mood = sum(npc.mood_level for npc in world_state.npcs.values()) / len(world_state.npcs)
            if avg_mood < 30:
                severity = "high"
            elif avg_mood > 70:
                severity = "low"
            else:
                severity = random.choice(self.severity_levels)
        else:
            severity = random.choice(self.severity_levels)

        # clean up description length and stray characters
        description = description.strip()
        # limit to first 20 words
        description = " ".join(description.split()[:20])
        # only drop stray leading 's ' or 'S ' if it appears exactly
        if description.startswith(("s ", "S ")):
            description = description[2:].strip()
        # ensure first letter uppercase for presentation
        if description:
            description = description[0].upper() + description[1:]

        return {
            "event_id": str(uuid.uuid4()),
            "description": description,
            "severity": severity,
            "affected_npcs": affected_npcs,
            "event_type": action,
            "timestamp": world_state.time,
        }
