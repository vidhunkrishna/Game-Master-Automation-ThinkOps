import React, { createContext, useContext, useState, useCallback } from "react";
import gameAPI from "../api/gameAPI";

// base URL for backend calls (without /api prefix)
const API_BASE = "http://115.247.219.102:8000";

const GameContext = createContext();

export const useGame = () => {
  const context = useContext(GameContext);
  if (!context) {
    throw new Error("useGame must be used within GameProvider");
  }
  return context;
};

export const GameProvider = ({ children }) => {
  const [worldState, setWorldState] = useState(null);
  const [recentEvents, setRecentEvents] = useState([]);
  const [actionHistory, setActionHistory] = useState([]);
  const [storyEvent, setStoryEvent] = useState(null);
  const [riskAssessment, setRiskAssessment] = useState(null);
  const [playerClassification, setPlayerClassification] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [tickCount, setTickCount] = useState(0);

  const fetchWorldState = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await gameAPI.getWorldState();
      setWorldState(response.data);
    } catch (err) {
      setError(err.message);
      console.error("Error fetching world state:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchEvents = useCallback(async () => {
    try {
      const response = await gameAPI.getRecentEvents(10);
      setRecentEvents(response.data);
    } catch (err) {
      console.error("Error fetching events:", err);
    }
  }, []);

  const processTick = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await gameAPI.processTick();
      // backend may return either raw world state or an object containing world_state
      const data =
        response.data && response.data.world_state
          ? response.data.world_state
          : response.data;
      setWorldState(data);
      setTickCount((prev) => prev + 1);
      await fetchEvents();
    } catch (err) {
      setError(err.message);
      console.error("Error processing tick:", err);
    } finally {
      setLoading(false);
    }
  }, [fetchEvents]);

  const resetSimulation = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await gameAPI.resetSimulation();
      setWorldState(response.data.world_state);
      setTickCount(0);
      setRecentEvents([]);
      setActionHistory([]);
    } catch (err) {
      setError(err.message);
      console.error("Error resetting simulation:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  const sendPlayerAction = useCallback(async (action) => {
    try {
      setLoading(true);
      setError(null);
      const payload = {
        player_id: "player_1",
        action,
        type: "movement",
      };
      const response = await fetch(`${API_BASE}/agent/player_action`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!response.ok) {
        throw new Error(`Server error ${response.status}`);
      }
      const data = await response.json();
      // update world state if backend provides summary or new state
      if (data.world_state_summary) {
        setWorldState((prev) => ({
          ...(prev || {}),
          ...data.world_state_summary,
        }));
      }
      // update AI panels
      setStoryEvent(data.story_event || null);
      setRiskAssessment(data.risk_assessment || null);
      setPlayerClassification(
        data.player_type ? data.player_type.classification : null,
      );
      // append story event to world events & recent events for feed
      if (data.story_event && data.story_event.description) {
        const desc = data.story_event.description;
        setWorldState((prev) => {
          if (!prev) return prev;
          return {
            ...prev,
            events: prev.events ? [...prev.events, desc] : [desc],
          };
        });
        setRecentEvents((prev) => [...prev, desc]);
      }
      // record action history
      setActionHistory((prev) => [...prev, { player_id: "player_1", action }]);
    } catch (err) {
      setError(err.message);
      console.error("Error sending player action:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  const value = {
    worldState,
    recentEvents,
    actionHistory,
    storyEvent,
    riskAssessment,
    playerClassification,
    loading,
    error,
    tickCount,
    fetchWorldState,
    fetchEvents,
    processTick,
    resetSimulation,
    sendPlayerAction,
  };

  return <GameContext.Provider value={value}>{children}</GameContext.Provider>;
};
