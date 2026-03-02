import axios from "axios";

const API_BASE = "http://localhost:8000/api";

export const gameAPI = {
  // World state endpoints
  getWorldState: () => axios.get(`${API_BASE}/world/state`),
  getWorldSummary: () => axios.get(`${API_BASE}/world/state/summary`),

  // Simulation control
  processTick: () => axios.post(`${API_BASE}/world/tick`),
  resetSimulation: () => axios.post(`${API_BASE}/world/reset`),

  // NPC endpoints
  getAllNPCs: () => axios.get(`${API_BASE}/npcs/all`),
  getNPC: (npcId) => axios.get(`${API_BASE}/npc/${npcId}`),

  // History and events
  getActionHistory: () => axios.get(`${API_BASE}/world/history`),
  getRecentEvents: (limit = 10) =>
    axios.get(`${API_BASE}/events?limit=${limit}`),
};

export default gameAPI;
