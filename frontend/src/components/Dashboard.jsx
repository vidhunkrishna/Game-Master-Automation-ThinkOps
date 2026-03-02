import React, { useEffect } from "react";
import { useGame } from "../context/GameContext";
import styles from "./Dashboard.module.css";

const Dashboard = () => {
  const {
    worldState,
    loading,
    error,
    tickCount,
    fetchWorldState,
    processTick,
    resetSimulation,
  } = useGame();

  useEffect(() => {
    fetchWorldState();
  }, [fetchWorldState]);

  if (error) {
    return <div className={styles.error}>Error: {error}</div>;
  }

  if (!worldState) {
    return <div className={styles.loading}>Loading...</div>;
  }

  return (
    <div className={styles.dashboard}>
      <header className={styles.header}>
        <h1>Game Master Dashboard</h1>
        <div className={styles.controls}>
          <button
            onClick={processTick}
            disabled={loading}
            className={styles.primaryBtn}
          >
            {loading ? "Processing..." : "Next Tick"}
          </button>
          <button
            onClick={resetSimulation}
            disabled={loading}
            className={styles.secondaryBtn}
          >
            Reset
          </button>
        </div>
      </header>

      <div className={styles.mainContent}>
        <section className={styles.worldState}>
          <h2>World State</h2>
          <div className={styles.stateGrid}>
            <div className={styles.stateItem}>
              <label>Simulation Time:</label>
              <span className={styles.value}>{worldState.time}</span>
            </div>
            <div className={styles.stateItem}>
              <label>Time of Day:</label>
              <span className={styles.value}>{worldState.time_of_day}</span>
            </div>
            <div className={styles.stateItem}>
              <label>Danger Level:</label>
              <span
                className={`${styles.value} ${worldState.danger_level > 70 ? styles.danger : ""}`}
              >
                {worldState.danger_level.toFixed(1)}%
              </span>
            </div>
            <div className={styles.stateItem}>
              <label>Weather:</label>
              <span className={styles.value}>{worldState.weather}</span>
            </div>
            <div className={styles.stateItem}>
              <label>Total Ticks:</label>
              <span className={styles.value}>{tickCount}</span>
            </div>
          </div>
        </section>

        <section className={styles.npcs}>
          <h2>
            NPCs ({worldState.npcs ? Object.keys(worldState.npcs).length : 0})
          </h2>
          <div className={styles.npcList}>
            {worldState.npcs &&
              Object.values(worldState.npcs).map((npc) => (
                <div key={npc.id} className={styles.npcCard}>
                  <h3>{npc.name}</h3>
                  <div className={styles.npcStats}>
                    <div className={styles.stat}>
                      <span className={styles.label}>Health:</span>
                      <div className={styles.statBar}>
                        <div
                          className={styles.statFill}
                          style={{
                            width: `${npc.health}%`,
                            backgroundColor:
                              npc.health > 60
                                ? "#4CAF50"
                                : npc.health > 30
                                  ? "#FF9800"
                                  : "#F44336",
                          }}
                        ></div>
                      </div>
                      <span className={styles.statValue}>
                        {npc.health.toFixed(0)}%
                      </span>
                    </div>

                    <div className={styles.stat}>
                      <span className={styles.label}>Mood:</span>
                      <div className={styles.statBar}>
                        <div
                          className={styles.statFill}
                          style={{
                            width: `${npc.mood_level}%`,
                            backgroundColor:
                              npc.mood_level > 60 ? "#2196F3" : "#9C27B0",
                          }}
                        ></div>
                      </div>
                      <span className={styles.statValue}>
                        {npc.mood} ({npc.mood_level.toFixed(0)}%)
                      </span>
                    </div>

                    <div className={styles.info}>
                      <p>
                        <strong>Goal:</strong> {npc.goal}
                      </p>
                      <p>
                        <strong>Last Action:</strong> {npc.last_action}
                      </p>
                      <p>
                        <strong>Position:</strong> ({npc.position_x.toFixed(0)},{" "}
                        {npc.position_y.toFixed(0)})
                      </p>
                    </div>
                  </div>
                </div>
              ))}
          </div>
        </section>

        <section className={styles.events}>
          <h2>Recent Events</h2>
          <div className={styles.eventList}>
            {worldState.events &&
              worldState.events
                .slice()
                .reverse()
                .map((event, idx) => (
                  <div key={idx} className={styles.eventItem}>
                    {event}
                  </div>
                ))}
          </div>
        </section>
      </div>
    </div>
  );
};

export default Dashboard;
