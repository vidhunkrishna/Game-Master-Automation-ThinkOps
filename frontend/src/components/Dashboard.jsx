import React, { useEffect, useState, useCallback } from "react";
import { useGame } from "../context/GameContext";
import styles from "./Dashboard.module.css";

const Dashboard = () => {
  const {
    worldState,
    storyEvent,
    riskAssessment,
    playerClassification,
    loading,
    error,
    tickCount,
    fetchWorldState,
    processTick,
    resetSimulation,
    sendPlayerAction,
  } = useGame();

  useEffect(() => {
    fetchWorldState();
  }, [fetchWorldState]);

  if (error) {
    return <div className={styles.error}>Error: {error}</div>;
  }

  // pipeline animation state
  const stages = [
    "Player Action",
    "Orchestrator Agent",
    "NPC Decision Agent",
    "Narrative Agent",
    "Intelligence Agent",
    "World Update",
  ];
  const [pipelineIndex, setPipelineIndex] = useState(-1);
  const [highlightedEventIdx, setHighlightedEventIdx] = useState(null);

  // when a new story event arrives, highlight it in feed
  useEffect(() => {
    if (storyEvent && storyEvent.description && worldState?.events) {
      const idx = worldState.events.length - 1;
      setHighlightedEventIdx(idx);
      const timer = setTimeout(() => setHighlightedEventIdx(null), 3000);
      return () => clearTimeout(timer);
    }
  }, [storyEvent, worldState]);

  const animatePipeline = useCallback(() => {
    stages.forEach((_, i) => {
      setTimeout(() => {
        setPipelineIndex(i);
      }, i * 300);
    });
    setTimeout(() => setPipelineIndex(-1), stages.length * 300);
  }, [stages]);

  const handlePlayerAction = async (action) => {
    animatePipeline();
    await sendPlayerAction(action);
  };

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

        <section className={styles.playerActions}>
          <h2>🎮 Player Actions</h2>
          <div>
            <button
              className={styles.actionBtn}
              onClick={() => handlePlayerAction("explore_forest")}
              disabled={loading}
            >
              Explore Forest
            </button>
            <button
              className={styles.actionBtn}
              onClick={() => handlePlayerAction("attack_village")}
              disabled={loading}
            >
              Attack Village
            </button>
            <button
              className={styles.actionBtn}
              onClick={() => handlePlayerAction("trade_market")}
              disabled={loading}
            >
              Trade Market
            </button>
            <button
              className={styles.actionBtn}
              onClick={() => handlePlayerAction("sneak_into_castle")}
              disabled={loading}
            >
              Sneak Into Castle
            </button>
          </div>
        </section>

        <section className={styles.aiEvent}>
          <h2>📜 AI Story Event</h2>
          {storyEvent ? (
            <>
              <p>{storyEvent.description}</p>
              <p>
                <strong>Severity:</strong>{" "}
                <span
                  className={`${styles.severity} ${storyEvent.severity ? styles[storyEvent.severity] : ""}`}
                >
                  {" "}
                  {storyEvent.severity}
                </span>
              </p>
            </>
          ) : (
            <p>No recent story event.</p>
          )}
        </section>

        <section className={styles.riskAnalysis}>
          <h2>⚠️ AI Risk Analysis</h2>
          {riskAssessment ? (
            <>
              <p>
                <strong>Risk Level:</strong>{" "}
                {riskAssessment.risk_level.toUpperCase()}
              </p>
              <p>
                <strong>Danger Level:</strong> {riskAssessment.danger_level}%
              </p>
              <div className={styles.progressBar}>
                <div
                  className={styles.progressFill}
                  style={{ width: `${riskAssessment.danger_level}%` }}
                ></div>
              </div>
              <p>
                <strong>Confidence:</strong>{" "}
                {(riskAssessment.confidence * 100).toFixed(0)}%
              </p>
            </>
          ) : (
            <p>No analysis available.</p>
          )}
        </section>

        <section className={styles.playerAnalysis}>
          <h2>🧠 Player Behavior Analysis</h2>
          {playerClassification ? (
            <p>
              {playerClassification.charAt(0).toUpperCase() +
                playerClassification.slice(1)}
            </p>
          ) : (
            <p>Unknown</p>
          )}
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
                .map((event, idx) => {
                  // because we reversed, compute original index
                  const originalIdx = worldState.events.length - 1 - idx;
                  const isNew = originalIdx === highlightedEventIdx;
                  return (
                    <div
                      key={idx}
                      className={`${styles.eventItem} ${isNew ? styles.new : ""}`}
                    >
                      {isNew ? "NEW EVENT: " + event : event}
                    </div>
                  );
                })}
          </div>
        </section>

        <section className={styles.pipeline}>
          {stages.map((label, idx) => (
            <div
              key={idx}
              className={`${styles.stage} ${idx === pipelineIndex ? styles.active : ""}`}
            >
              {label} {idx < stages.length - 1 && "→"}
            </div>
          ))}
        </section>
      </div>
    </div>
  );
};

export default Dashboard;
