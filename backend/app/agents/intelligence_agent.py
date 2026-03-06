"""Intelligence Agent - Machine learning for player behavior and risk prediction."""
from typing import Dict, List, Optional
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
import numpy as np


class IntelligenceAgent:
    """
    Uses machine learning models to classify player behavior and predict
    risk levels in the game world.
    """

    # Player behavior classes
    PLAYER_BEHAVIORS = ["aggressive", "explorer", "trader", "neutral"]
    
    # Risk level classes
    RISK_LEVELS = ["low", "medium", "high"]

    def __init__(self):
        """Initialize intelligence agent with ML models."""
        self.player_behavior_model: Optional[LogisticRegression] = None
        self.risk_prediction_model: Optional[DecisionTreeClassifier] = None
        self.player_behavior_classes = self.PLAYER_BEHAVIORS
        self.risk_level_classes = self.RISK_LEVELS

    def train_behavior_model(self, X: List[List[float]], y: List[str]) -> Dict[str, any]:
        """
        Train the player behavior classification model.

        Args:
            X: List of feature vectors (e.g., [action_count, resource_gathered, npc_interactions])
            y: List of behavior labels (aggressive, explorer, trader, neutral)

        Returns:
            dict: Training results with model accuracy
        """
        if not X or not y:
            return {"error": "No training data provided"}

        try:
            # Convert labels to numeric
            label_to_idx = {label: idx for idx, label in enumerate(self.player_behavior_classes)}
            y_numeric = np.array([label_to_idx.get(label, 0) for label in y])

            # Train model
            self.player_behavior_model = LogisticRegression(
                max_iter=1000,
                random_state=42,
                multi_class="multinomial",
            )
            self.player_behavior_model.fit(X, y_numeric)

            # Calculate accuracy (training accuracy)
            accuracy = self.player_behavior_model.score(X, y_numeric)

            return {
                "success": True,
                "model": "player_behavior",
                "accuracy": float(accuracy),
                "classes": self.player_behavior_classes,
                "samples": len(X),
            }
        except Exception as e:
            return {"error": str(e), "model": "player_behavior"}

    def predict_player_type(self, player_features: List[float]) -> Dict[str, any]:
        """
        Predict player behavior type based on features.

        Args:
            player_features: List of numeric features (e.g., [actions, resources, interactions])

        Returns:
            dict: Predicted player type with confidence
        """
        if self.player_behavior_model is None:
            return {
                "error": "Model not trained",
                "prediction": "neutral",
                "confidence": 0.0,
            }

        try:
            # Predict
            prediction_idx = self.player_behavior_model.predict([player_features])[0]
            predicted_class = self.player_behavior_classes[prediction_idx]

            # Get confidence (probability)
            probabilities = self.player_behavior_model.predict_proba([player_features])[0]
            confidence = float(np.max(probabilities))

            return {
                "success": True,
                "player_type": predicted_class,
                "confidence": confidence,
                "all_probabilities": {
                    self.player_behavior_classes[i]: float(probabilities[i])
                    for i in range(len(self.player_behavior_classes))
                },
            }
        except Exception as e:
            return {"error": str(e), "prediction": "neutral", "confidence": 0.0}

    def train_risk_model(self, X: List[List[float]], y: List[str]) -> Dict[str, any]:
        """
        Train the risk level prediction model.

        Args:
            X: List of feature vectors (e.g., [danger_level, npc_health, resource_scarcity])
            y: List of risk level labels (low, medium, high)

        Returns:
            dict: Training results with model accuracy
        """
        if not X or not y:
            return {"error": "No training data provided"}

        try:
            # Convert labels to numeric
            label_to_idx = {label: idx for idx, label in enumerate(self.risk_level_classes)}
            y_numeric = np.array([label_to_idx.get(label, 0) for label in y])

            # Train model
            self.risk_prediction_model = DecisionTreeClassifier(
                max_depth=5,
                random_state=42,
            )
            self.risk_prediction_model.fit(X, y_numeric)

            # Calculate accuracy
            accuracy = self.risk_prediction_model.score(X, y_numeric)

            return {
                "success": True,
                "model": "risk_prediction",
                "accuracy": float(accuracy),
                "classes": self.risk_level_classes,
                "samples": len(X),
            }
        except Exception as e:
            return {"error": str(e), "model": "risk_prediction"}

    def predict_risk_level(self, world_features: List[float]) -> Dict[str, any]:
        """
        Predict risk level in the world based on features.

        Args:
            world_features: List of numeric features (e.g., [danger_level, npc_count, health_avg])

        Returns:
            dict: Predicted risk level with confidence
        """
        if self.risk_prediction_model is None:
            # Fallback to heuristic if model not trained
            # Assume features: [danger_level, ...]
            danger_level = world_features[0] if world_features else 50.0
            if danger_level > 60:
                predicted_risk = "high"
            elif danger_level > 30:
                predicted_risk = "medium"
            else:
                predicted_risk = "low"

            return {
                "success": True,
                "risk_level": predicted_risk,
                "confidence": 0.75,
                "method": "heuristic",
            }

        try:
            # Predict
            prediction_idx = self.risk_prediction_model.predict([world_features])[0]
            predicted_risk = self.risk_level_classes[prediction_idx]

            # Get confidence
            predictions = self.risk_prediction_model.predict_proba([world_features])[0]
            confidence = float(np.max(predictions))

            return {
                "success": True,
                "risk_level": predicted_risk,
                "confidence": confidence,
                "all_probabilities": {
                    self.risk_level_classes[i]: float(predictions[i])
                    for i in range(len(self.risk_level_classes))
                },
            }
        except Exception as e:
            return {
                "error": str(e),
                "risk_level": "medium",
                "confidence": 0.5,
            }

    def extract_player_features_from_history(
        self, player_actions: List[Dict[str, any]]
    ) -> List[float]:
        """
        Extract player behavior features from action history.

        Args:
            player_actions: List of player action dictionaries

        Returns:
            List[float]: Feature vector for behavior prediction
        """
        if not player_actions:
            return [0.0, 0.0, 0.0, 0.0]

        action_count = len(player_actions)
        
        # Count action types
        aggressive_actions = sum(
            1 for a in player_actions if a.get("type") in ["attack", "raid", "fight"]
        )
        exploration_actions = sum(
            1 for a in player_actions if a.get("type") in ["explore", "scout", "search"]
        )
        trade_actions = sum(
            1 for a in player_actions if a.get("type") in ["trade", "exchange", "barter"]
        )

        return [
            float(aggressive_actions),
            float(exploration_actions),
            float(trade_actions),
            float(action_count),
        ]

    def extract_world_features_from_state(self, world_state: Dict[str, any]) -> List[float]:
        """
        Extract world features from world state for risk prediction.

        Args:
            world_state: World state dictionary

        Returns:
            List[float]: Feature vector for risk prediction
        """
        danger_level = world_state.get("danger_level", 50.0)
        npc_count = len(world_state.get("npcs", {}))
        
        # Calculate average NPC health
        npcs = world_state.get("npcs", {})
        health_values = [npc.get("health", 50) for npc in npcs.values()]
        avg_health = sum(health_values) / len(health_values) if health_values else 50.0

        # Event count (can indicate activity level)
        event_count = len(world_state.get("events", []))

        return [
            float(danger_level),
            float(npc_count),
            float(avg_health),
            float(event_count),
        ]
