import axios from "axios";

// primary base URL for backend (no suffix)
const API_BASE = "http://127.0.0.1:8000";
// prefix for endpoints that sit under /api
const API_PREFIX = `${API_BASE}/api`;

export const gameAPI = {
  // World state endpoints
  getWorldState: () => axios.get(`${API_PREFIX}/world/state`),
  getWorldSummary: () => axios.get(`${API_PREFIX}/world/state/summary`),

  // Simulation control
  processTick: () => axios.post(`${API_PREFIX}/world/tick`),
  resetSimulation: () => axios.post(`${API_PREFIX}/world/reset`),

  // NPC endpoints
  getAllNPCs: () => axios.get(`${API_PREFIX}/npcs/all`),
  getNPC: (npcId) => axios.get(`${API_PREFIX}/npc/${npcId}`),

  // History and events
  getActionHistory: () => axios.get(`${API_PREFIX}/world/history`),
  getRecentEvents: (limit = 10) =>
    axios.get(`${API_PREFIX}/events?limit=${limit}`),
  // Player/AI interactions (no /api prefix)
  playerAction: (payload) =>
    axios.post(`${API_BASE}/agent/player_action`, payload),
};

export default gameAPI;
