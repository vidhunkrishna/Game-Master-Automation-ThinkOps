# Multi-Agent Game Master System

A full-stack autonomous multi-agent simulation system built with FastAPI and React. This system demonstrates agent coordination, decision-making, and world state management.

## Architecture Overview

```
┌─────────────────────────────────────┐
│      Frontend (React + Vite)        │
│  - Dashboard with World State       │
│  - NPC Status Panels                │
│  - Event Timeline                   │
│  - Tick Control                     │
└────────────────┬────────────────────┘
                 │ HTTP/REST
┌────────────────▼────────────────────┐
│   Backend (FastAPI)                 │
│  ┌──────────────────────────────┐  │
│  │ Head Orchestrator Agent      │  │
│  │  - World State Management    │  │
│  │  - Simulation Loop           │  │
│  │  - Event Coordination        │  │
│  └──────────────────────────────┘  │
│  ┌──────────────────────────────┐  │
│  │ NPC Decision Agent           │  │
│  │  - Goal-Driven Decisions     │  │
│  │  - Utility Scoring           │  │
│  │  - Rule-Based Logic          │  │
│  └──────────────────────────────┘  │
└─────────────────────────────────────┘
```

## Folder Structure

```
Agent/
├── backend/
│   ├── requirements.txt              # Python dependencies
│   ├── run.sh                        # Startup script
│   └── app/
│       ├── __init__.py
│       ├── main.py                   # FastAPI app & entry point
│       ├── agents/
│       │   ├── __init__.py
│       │   ├── orchestrator.py       # Head Orchestrator (World Governor)
│       │   └── npc_agent.py          # NPC Decision Agent
│       ├── models/
│       │   ├── __init__.py
│       │   └── world.py              # Pydantic models for world state
│       └── routes/
│           ├── __init__.py
│           └── world.py              # REST API endpoints
│
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   ├── index.html
│   └── src/
│       ├── main.jsx
│       ├── App.jsx
│       ├── index.css
│       ├── api/
│       │   └── gameAPI.js            # API client with axios
│       ├── context/
│       │   └── GameContext.jsx       # Global state management
│       └── components/
│           ├── Dashboard.jsx         # Main dashboard component
│           └── Dashboard.module.css  # Styling
│
└── README.md
```

## Backend Implementation

### 1. **Head Orchestrator Agent** (`orchestrator.py`)

Maintains the global world state and orchestrates the simulation.

**Key Features:**

- World state initialization with 3 default NPCs
- Simulation tick processing
- Environmental updates (time, danger, health recovery)
- Action application to world state
- Action history tracking
- Persistent in-memory state

**World State Structure:**

```python
{
  "time": 0,                    # Simulation tick count
  "time_of_day": "morning",     # Cyclic 24-tick day/night
  "danger_level": 20.0,         # 0-100
  "weather": "sunny",
  "npcs": {...},
  "events": [...]
}
```

### 2. **NPC Decision Agent** (`npc_agent.py`)

Makes goal-driven decisions for each NPC using utility scoring.

**Decision Process:**

1. Generate candidate actions based on NPC goal
2. Score each action using utility function
3. Consider health, mood, danger level, time of day
4. Select action with highest score
5. Apply reputation/habit penalties

**Action Types:**

- `move` - Change position
- `rest` - Recover health and mood
- `attack` - Engage threat (increases danger)
- `flee` - Escape from danger
- `trade` - Interact with other NPCs
- `idle` - No action

**Utility Scoring Factors:**

- Health status (low health → high rest priority)
- Mood level (impacts goal achievement)
- Goal alignment (actions matching NPC's goal score higher)
- Danger level (high danger increases flee/rest priority)
- Time of day (night favors rest over exploration)
- Action repetition penalty (avoid same action twice)

### 3. **REST API Endpoints**

```
# World State
GET  /api/world/state           # Current world state
POST /api/world/tick            # Process one simulation tick
GET  /api/world/state/summary   # Quick state summary
POST /api/world/reset           # Reset simulation

# NPCs
GET  /api/npcs/all              # All NPCs
GET  /api/npc/{npc_id}          # Specific NPC

# History
GET  /api/world/history         # Recent actions
GET  /api/events?limit=10       # Recent world events
```

## Frontend Implementation

### **State Management (GameContext)**

Uses React Context API for global state:

- `worldState` - Current simulation state
- `recentEvents` - Last 10 world events
- `tickCount` - Number of ticks processed
- `loading`, `error` - Async state

### **Dashboard Component**

Displays:

1. **World State Panel** - Time, danger level, weather
2. **NPC Cards** - Health/mood bars, goal, position
3. **Event Timeline** - Last 20 events in reverse order
4. **Control Buttons** - Next Tick, Reset
5. **Player Action Controls** - Buttons that trigger AI-driven events (explore, attack, trade, sneak).
6. **AI Story Event Panel** - Displays generated story description and severity, with color cues.
7. **ML Risk Analysis Panel** - Shows risk level, danger percentage bars and confidence scores.
8. **Player Behavior Analysis** - Classification of player behavior (Explorer, Aggressive, etc.).
9. **AI Decision Pipeline** - Horizontal visualization of the agent pipeline highlighting each stage during actions.

### **API Integration**

Axios client with convenience methods:

```javascript
gameAPI.getWorldState(); // Fetch current state
gameAPI.processTick(); // Advance simulation
gameAPI.getAllNPCs(); // Get all NPCs
gameAPI.resetSimulation(); // Reset to initial state
```

## Running the System

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API will be available at `http://localhost:8000`
Documentation at `http://localhost:8000/docs`

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend will be available at `http://localhost:5173`

### Access Points

- **Frontend Dashboard:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs

## Simulation Logic Example

### One Tick Flow

```
1. Orchestrator.process_tick()
   ├── Update environment
   │   ├── Progress time (0-23 hour cycle)
   │   ├── Update time_of_day based on time
   │   ├── Adjust danger_level (gradual decrease if > 20)
   │   └── Passive health recovery for idle NPCs
   │
   ├── For each NPC:
   │   ├── NPC Agent generates candidate actions
   │   ├── Score each action using utility function
   │   ├── Select highest-scoring action
   │   └── Orchestrator applies action to world state
   │
   └── Return updated world state
```

### Action Application

When an NPC action is applied:

1. Modify relevant world state (NPC position, health, mood)
2. Create event message
3. Track in action history
4. Apply secondary effects (e.g., attack increases danger)

## Scaling to More Agents

The system is designed for easy expansion:

### Add More Agent Types

1. **Create new agent class** in `backend/app/agents/`

   ```python
   class ResourceManagerAgent:
       async def manage_resources(self, world_state):
           # Logic for resource management
           pass
   ```

2. **Register in Orchestrator**

   ```python
   self.resource_agent = ResourceManagerAgent()
   ```

3. **Call in tick loop**
   ```python
   async def process_tick(self):
       # ... existing code ...
       resource_changes = await self.resource_agent.manage_resources(self.world_state)
       self._apply_resource_changes(resource_changes)
   ```

### Multi-Agent Communication

1. **Create message queue system** (use asyncio.Queue or Redis)

   ```python
   class MessageBroker:
       def __init__(self):
           self.queues = {}  # Per-agent message queues

       async def send(self, to_agent, message):
           await self.queues[to_agent].put(message)

       async def receive(self, agent_id):
           return await self.queues[agent_id].get()
   ```

2. **Add agent-to-agent communication**
   - Orchestrator broadcasts world state to all agents
   - Agents can request information from peers
   - Negotiation/conflict resolution via orchestrator

### Performance Optimization

1. **Async Processing**
   - Already uses async/await for I/O
   - Upgrade to concurrent agent processing:
     ```python
     tasks = [agent.decide() for agent in agents]
     results = await asyncio.gather(*tasks)
     ```

2. **State Sharding**
   - For many NPCs, partition state by region
   - Only process NPCs near each other

3. **Caching**
   - Cache world state digest
   - Only send deltas to frontend

4. **Database Backend**
   - Replace in-memory state with SQLAlchemy + PostgreSQL
   - Enables persistence and analytics
   - Multi-server deployment

### Database Schema (Future)

```python
class NPCModel(Base):
    __tablename__ = "npcs"
    id: str
    world_id: str
    health: float
    mood: str
    position_x: float
    position_y: float
    goal: str
    last_action: str
    created_at: datetime
    updated_at: datetime

class WorldStateModel(Base):
    __tablename__ = "world_states"
    id: str
    tick: int
    danger_level: float
    weather: str
    created_at: datetime

class EventModel(Base):
    __tablename__ = "events"
    id: str
    world_id: str
    tick: int
    description: str
    created_at: datetime
```

## Extending Functionality

### Add New NPC Goals

In `npc_agent.py`:

```python
def _decide_custom_goal(self, npc, world_state):
    actions = []
    # Define logic for new goal
    actions.append(NPCAction(...))
    return actions

# Register in __init__
self.decision_rules["custom_goal"] = self._decide_custom_goal
```

### Add New World State Properties

1. Update `WorldState` Pydantic model
2. Initialize in orchestrator
3. Update in `_update_environment()`
4. Use in decision scoring

### Add New Action Types

1. Create handler in `_apply_action()`
2. Define utility impact in scoring function
3. Add to NPC goal strategies

## Performance Metrics

Current system can handle:

- **NPCs:** 100+ concurrent agents
- **Tick Rate:** 10-50 ticks/second
- **Action History:** Last 100 actions
- **Event Log:** Last 20 world events

## Future Enhancements

1. **Dialogue System** - NPCs communicate via structured dialogue
2. **Learning** - NPCs adjust strategy based on past outcomes
3. **Procedural Generation** - Dynamic world/NPC creation
4. **Replay System** - Record and replay simulation
5. **Visualization** - 2D/3D rendering of world
6. **Networking** - Multiplayer agent coordination
7. **Persistence** - Save/load simulation state
8. **Analytics** - Behavior tracking and visualization

## License

MIT
