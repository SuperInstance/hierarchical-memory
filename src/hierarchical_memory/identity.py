"""
Hierarchical Memory System - Identity Persistence Module
========================================================

Identity persistence and drift tracking system.

Maintains consistent character identity while allowing growth through:
- Core trait stability (very slow change)
- Temporal trait adaptation (faster change)
- Drift detection and alerting
- Identity coherence measurement
- Personality snapshot history

Based on:
- Psychological continuity theory
- Personality stability research
- Identity drift detection in LLM agents
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime
from collections import defaultdict
import numpy as np

from .core import Memory, HierarchicalMemory


# ============================================================================
# IDENTITY DATA STRUCTURES
# ============================================================================

@dataclass
class PersonalitySnapshot:
    """Snapshot of personality state at a point in time"""
    timestamp: str
    core_traits: Dict[str, float]
    temporal_traits: Dict[str, float]
    drift_score: float
    reason: str = ""


@dataclass
class IdentityReport:
    """Comprehensive identity health report"""
    character_id: str
    timestamp: str
    coherence_index: float  # 0-1, >0.7 healthy, <0.4 needs intervention
    personality_stability: float  # 0-1
    memory_retention: float  # 0-1
    drift_score: float  # 0-1, lower is better
    core_traits: Dict[str, float]
    temporal_traits: Dict[str, float]
    recommendations: List[str] = field(default_factory=list)


# ============================================================================
# IDENTITY PERSISTENCE
# ============================================================================

class IdentityPersistence:
    """
    Maintains consistent identity while allowing growth.

    Uses two-tier personality model:
    1. Core traits: Change very slowly (identity foundation)
    2. Temporal traits: Adapt to experiences (mood, context)

    Example:
        >>> identity = IdentityPersistence("agent_001", core_traits={
        ...     "openness": 0.7,
        ...     "conscientiousness": 0.8
        ... })
        >>> identity.update_from_experience(emotional_valence=0.5)
        >>> report = identity.get_report()
    """

    # Big Five traits (default)
    DEFAULT_CORE_TRAITS = {
        "openness": 0.5,          # Open to new experiences
        "conscientiousness": 0.5, # Organized, disciplined
        "extraversion": 0.5,      # Social, outgoing
        "agreeableness": 0.5,     # Cooperative, friendly
        "neuroticism": 0.5,       # Emotional stability (low = stable)
    }

    # Configuration
    CORE_LEARNING_RATE = 0.001    # Very slow core change
    TEMPORAL_LEARNING_RATE = 0.1  # Faster temporal change
    DRIFT_THRESHOLD = 0.15        # Alert if drift > 15%
    DRIFT_INTERVENTION = 0.25     # Critical intervention threshold

    def __init__(self,
                 character_id: str,
                 core_traits: Optional[Dict[str, float]] = None,
                 config: Optional[Dict[str, float]] = None):
        """
        Initialize identity persistence system.

        Args:
            character_id: Unique identifier
            core_traits: Initial core personality traits (0-1 scale)
            config: Configuration overrides
        """
        self.character_id = character_id

        # Core identity (locked, changes very slowly)
        self.core_traits = {**self.DEFAULT_CORE_TRAITS, **(core_traits or {})}

        # Temporal state (changes more frequently)
        self.temporal_traits = self.core_traits.copy()

        # Personality evolution history
        self.snapshot_history: List[PersonalitySnapshot] = []
        self.baseline_embedding: Optional[np.ndarray] = None

        # Drift detection (EWMA smoothing)
        self.drift_ewma = 0.0
        self.drift_lambda = 0.3  # Exponential smoothing factor

        # Configuration
        self.config = {**{
            "core_learning_rate": self.CORE_LEARNING_RATE,
            "temporal_learning_rate": self.TEMPORAL_LEARNING_RATE,
            "drift_threshold": self.DRIFT_THRESHOLD,
            "drift_intervention": self.DRIFT_INTERVENTION,
        }, **(config or {})}

    # ======================================================================
    # IDENTITY UPDATES
    # ======================================================================

    def update_from_experience(self,
                               emotional_valence: float = 0.0,
                               social_context: bool = False,
                               novelty: float = 0.0,
                               confidence: float = 1.0):
        """
        Update temporal traits based on experience.

        Args:
            emotional_valence: -1 (bad) to 1 (good) experience
            social_context: Was this a social interaction?
            novelty: How novel was the experience (0-1)
            confidence: Confidence in the update (0-1)
        """
        # Calculate behavior-like "embedding" from experience
        behavior_vector = self._experience_to_vector(
            emotional_valence, social_context, novelty
        )

        # Initialize baseline if needed
        if self.baseline_embedding is None:
            self.baseline_embedding = behavior_vector

        # Calculate drift
        drift = self._calculate_drift(behavior_vector)

        # Update EWMA drift tracker
        self.drift_ewma = self.drift_lambda * drift + (1 - self.drift_lambda) * self.drift_ewma

        # Update temporal traits based on experience
        for trait_name in self.temporal_traits:
            delta = self._trait_delta_from_experience(
                trait_name,
                emotional_valence,
                social_context,
                novelty,
                confidence
            )
            self.temporal_traits[trait_name] = np.clip(
                self.temporal_traits[trait_name] + delta,
                0.0, 1.0
            )

        # Slowly drift core traits (much slower)
        if drift > 0.1:  # Only if significant drift
            for trait in self.core_traits:
                delta = (
                    (self.temporal_traits[trait] - self.core_traits[trait]) *
                    self.config["core_learning_rate"]
                )
                self.core_traits[trait] = np.clip(
                    self.core_traits[trait] + delta,
                    0.0, 1.0
                )

    def update_from_memory(self, memory: Memory):
        """
        Update identity based on a memory.

        Args:
            memory: Memory to update from
        """
        self.update_from_experience(
            emotional_valence=memory.emotional_valence,
            social_context=len(memory.participants) >= 2,
            novelty=0.5 if memory.importance > 6.0 else 0.2,
            confidence=memory.importance / 10.0
        )

    def update_from_memories(self, memories: List[Memory]):
        """
        Update identity from multiple memories.

        Args:
            memories: List of memories to learn from
        """
        for memory in memories:
            self.update_from_memory(memory)

    # ======================================================================
    # DRIFT TRACKING
    # ======================================================================

    def get_drift_score(self) -> float:
        """
        Get current identity drift (0-1).
        Lower is better (more stable).
        """
        return max(0.0, min(1.0, self.drift_ewma))

    def is_drift_warning(self) -> bool:
        """Check if drift exceeds warning threshold."""
        return self.get_drift_score() > self.config["drift_threshold"]

    def is_drift_critical(self) -> bool:
        """Check if drift exceeds critical threshold."""
        return self.get_drift_score() > self.config["drift_intervention"]

    def get_reinforcement_prompt(self) -> str:
        """
        Generate a prompt to reinforce core identity.
        Use when drift is detected.
        """
        traits_str = ", ".join([
            f"{k}: {v:.1f}"
            for k, v in self.core_traits.items()
        ])

        return (
            f"Remember who you are fundamentally. "
            f"Your core identity traits are: {traits_str}. "
            f"These define you. Growth means becoming more authentically yourself, not someone else."
        )

    # ======================================================================
    # IDENTITY COHERENCE
    # ======================================================================

    def get_coherence_index(self,
                           recent_memories: Optional[List[Memory]] = None,
                           window_days: int = 30) -> float:
        """
        Calculate Identity Coherence Index (ICI).
        Ranges: >0.7 healthy | 0.4-0.7 monitor | <0.4 intervention

        Args:
            recent_memories: Recent memories to consider
            window_days: Time window for memory retention

        Returns:
            Coherence score 0-1
        """
        # Personality stability: how much have core traits changed?
        trait_changes = np.mean([
            abs(self.temporal_traits.get(k, 0) - v)
            for k, v in self.core_traits.items()
        ])
        personality_stability = 1.0 - trait_changes

        # Memory retention (if memories provided)
        if recent_memories:
            memory_retention = min(len(recent_memories) / 10.0, 1.0)
        else:
            memory_retention = 0.7  # Default

        # Drift score (invert for contribution to coherence)
        drift_score = self.get_drift_score()
        drift_contribution = 1.0 - drift_score

        # Composite ICI
        ICI = (
            0.35 * personality_stability +
            0.35 * memory_retention +
            0.30 * drift_contribution
        )

        return max(0.0, min(1.0, ICI))

    # ======================================================================
    # SNAPSHOTS
    # ======================================================================

    def snapshot(self, reason: str = "") -> PersonalitySnapshot:
        """
        Save personality state snapshot.

        Args:
            reason: Reason for the snapshot

        Returns:
            The created snapshot
        """
        snapshot = PersonalitySnapshot(
            timestamp=datetime.now().isoformat(),
            core_traits=self.core_traits.copy(),
            temporal_traits=self.temporal_traits.copy(),
            drift_score=self.get_drift_score(),
            reason=reason
        )

        self.snapshot_history.append(snapshot)
        return snapshot

    def get_recent_snapshots(self, count: int = 5) -> List[PersonalitySnapshot]:
        """Get recent snapshots."""
        return self.snapshot_history[-count:]

    def compare_snapshots(self,
                         snapshot1: Optional[PersonalitySnapshot] = None,
                         snapshot2: Optional[PersonalitySnapshot] = None) -> Dict[str, float]:
        """
        Compare two snapshots.

        Args:
            snapshot1: First snapshot (default: oldest)
            snapshot2: Second snapshot (default: newest)

        Returns:
            Dict of trait changes
        """
        if not self.snapshot_history:
            return {}

        snap1 = snapshot1 or self.snapshot_history[0]
        snap2 = snapshot2 or self.snapshot_history[-1]

        changes = {}
        for trait in snap1.core_traits:
            changes[trait] = snap2.core_traits.get(trait, 0) - snap1.core_traits[trait]

        return changes

    # ======================================================================
    # REPORTS
    # ======================================================================

    def get_report(self,
                   recent_memories: Optional[List[Memory]] = None) -> IdentityReport:
        """
        Generate comprehensive identity health report.

        Args:
            recent_memories: Recent memories for coherence calculation

        Returns:
            IdentityReport with full analysis
        """
        coherence = self.get_coherence_index(recent_memories)

        # Personality stability
        trait_changes = [
            abs(self.temporal_traits.get(k, 0) - v)
            for k, v in self.core_traits.items()
        ]
        personality_stability = 1.0 - np.mean(trait_changes)

        # Memory retention
        memory_retention = min(len(recent_memories) / 10.0, 1.0) if recent_memories else 0.7

        # Drift
        drift = self.get_drift_score()

        # Recommendations
        recommendations = []
        if coherence < 0.4:
            recommendations.append("CRITICAL: Identity coherence low. Consider reinforcing core identity.")
        elif coherence < 0.7:
            recommendations.append("WARNING: Identity coherence below optimal. Monitor closely.")

        if drift > self.config["drift_intervention"]:
            recommendations.append("CRITICAL: High identity drift detected.")
        elif drift > self.config["drift_threshold"]:
            recommendations.append("WARNING: Identity drift above threshold.")

        if not recommendations:
            recommendations.append("Identity health is good.")

        return IdentityReport(
            character_id=self.character_id,
            timestamp=datetime.now().isoformat(),
            coherence_index=coherence,
            personality_stability=personality_stability,
            memory_retention=memory_retention,
            drift_score=drift,
            core_traits=self.core_traits.copy(),
            temporal_traits=self.temporal_traits.copy(),
            recommendations=recommendations
        )

    # ======================================================================
    # PRIVATE METHODS
    # ======================================================================

    def _experience_to_vector(self,
                              emotional_valence: float,
                              social_context: bool,
                              novelty: float) -> np.ndarray:
        """Convert experience to a behavior-like vector."""
        return np.array([
            emotional_valence,
            1.0 if social_context else 0.0,
            novelty,
            # Add trait-influenced dimensions
            self.temporal_traits.get("openness", 0.5) * novelty,
            self.temporal_traits.get("extraversion", 0.5) * (1.0 if social_context else 0.0),
        ])

    def _calculate_drift(self, current_embedding: np.ndarray) -> float:
        """Calculate drift from baseline using cosine distance."""
        if self.baseline_embedding is None:
            return 0.0

        # Ensure same shape
        if current_embedding.shape != self.baseline_embedding.shape:
            return 0.0

        # Cosine similarity
        dot_product = np.dot(current_embedding, self.baseline_embedding)
        norm1 = np.linalg.norm(current_embedding)
        norm2 = np.linalg.norm(self.baseline_embedding)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        cosine_sim = dot_product / (norm1 * norm2)
        drift = 1.0 - cosine_sim  # 0 = same, 1 = opposite

        return np.clip(drift, 0.0, 1.0)

    def _trait_delta_from_experience(self,
                                     trait_name: str,
                                     emotional_valence: float,
                                     social_context: bool,
                                     novelty: float,
                                     confidence: float) -> float:
        """Calculate trait change from experience."""
        base_delta = np.random.normal(0, 0.02) * confidence

        # Trait-specific responses
        if trait_name == "neuroticism":
            # Negative experiences increase neuroticism
            base_delta += -emotional_valence * 0.05 * confidence
        elif trait_name == "extraversion":
            # Social context increases extraversion
            base_delta += (0.05 if social_context else -0.02) * confidence
        elif trait_name == "openness":
            # Novel experiences increase openness
            base_delta += novelty * 0.05 * confidence
        elif trait_name == "agreeableness":
            # Positive experiences increase agreeableness
            base_delta += emotional_valence * 0.03 * confidence
        elif trait_name == "conscientiousness":
            # Not strongly affected by single experiences
            base_delta *= 0.5

        return base_delta * self.config["temporal_learning_rate"]

    def reset_temporal_traits(self):
        """Reset temporal traits to core traits (recentering)."""
        self.temporal_traits = self.core_traits.copy()
        self.drift_ewma = 0.0


# ============================================================================
# IDENTITY DRIFT TRACKER
# ============================================================================

class IdentityDriftTracker:
    """
    Tracks identity drift over time for monitoring and intervention.

    Provides:
    - Drift history
    - Trend analysis
    - Anomaly detection
    - Intervention triggers
    """

    def __init__(self, character_id: str):
        self.character_id = character_id
        self.drift_history: List[Tuple[str, float]] = []  # (timestamp, drift)
        self.intervention_history: List[Tuple[str, str]] = []  # (timestamp, reason)

    def record_drift(self, drift_score: float, reason: str = ""):
        """Record a drift measurement."""
        self.drift_history.append((datetime.now().isoformat(), drift_score))

        # Check for intervention
        if drift_score > 0.25:
            self.intervention_history.append((
                datetime.now().isoformat(),
                f"Critical drift: {drift_score:.2f} - {reason}"
            ))

    def get_trend(self, window: int = 10) -> str:
        """Get drift trend over recent measurements."""
        recent = [d for _, d in self.drift_history[-window:]]
        if len(recent) < 2:
            return "insufficient_data"

        slope = np.polyfit(range(len(recent)), recent, 1)[0]

        if slope > 0.01:
            return "increasing"
        elif slope < -0.01:
            return "decreasing"
        else:
            return "stable"

    def get_stats(self) -> Dict[str, Any]:
        """Get drift statistics."""
        if not self.drift_history:
            return {"message": "No drift measurements yet"}

        drifts = [d for _, d in self.drift_history]

        return {
            "mean_drift": np.mean(drifts),
            "max_drift": np.max(drifts),
            "min_drift": np.min(drifts),
            "current_drift": drifts[-1],
            "trend": self.get_trend(),
            "interventions": len(self.intervention_history),
        }


# ============================================================================
# INTEGRATION WITH HIERARCHICAL MEMORY
# ============================================================================

def attach_identity_system(memory_system: HierarchicalMemory,
                          core_traits: Optional[Dict[str, float]] = None) -> IdentityPersistence:
    """
    Attach an identity persistence system to a memory system.

    Args:
        memory_system: The HierarchicalMemory instance
        core_traits: Initial core traits

    Returns:
        IdentityPersistence instance
    """
    identity = IdentityPersistence(
        character_id=memory_system.character_id,
        core_traits=core_traits
    )

    # Learn from existing memories
    existing_memories = list(memory_system.memories.values())
    if existing_memories:
        identity.update_from_memories(existing_memories[:50])  # Learn from top 50

    return identity
