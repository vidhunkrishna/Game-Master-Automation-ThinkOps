import React, { createContext, useContext, useState, useCallback } from "react";
import gameAPI from "../api/gameAPI";

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

  const value = {
    worldState,
    recentEvents,
    actionHistory,
    loading,
    error,
    tickCount,
    fetchWorldState,
    fetchEvents,
    processTick,
    resetSimulation,
  };

  return <GameContext.Provider value={value}>{children}</GameContext.Provider>;
};
