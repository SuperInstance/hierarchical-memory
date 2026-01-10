"""
Hierarchical Memory System - Core Module
========================================

Core memory architecture implementing 6-tier hierarchical memory system
inspired by cognitive neuroscience and memory consolidation research.

Memory Tiers:
- WORKING: Current attention/context (seconds to minutes)
- MID_TERM: Session buffer (1-6 hours)
- LONG_TERM: Consolidated storage (1+ weeks)
- EPISODIC: Specific events "what-where-when"
- SEMANTIC: Consolidated patterns & facts
- PROCEDURAL: Skills & learned behaviors
"""

import json
import hashlib
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
import math
import numpy as np
from collections import defaultdict
from pathlib import Path


# ============================================================================
# MEMORY TYPES & ENUMS
# ============================================================================

class MemoryType(Enum):
    """Hierarchical memory tiers (inspired by neuroscience)"""
    WORKING = "working"              # Current attention (LLM context)
    MID_TERM = "mid_term"            # Session buffer (1-6 hours)
    LONG_TERM = "long_term"          # Consolidated storage (1+ weeks)
    EPISODIC = "episodic"            # Specific events "what-where-when"
    SEMANTIC = "semantic"            # Consolidated patterns & facts
    PROCEDURAL = "procedural"        # Skills & learned behaviors


class MemoryImportance(Enum):
    """Importance scoring (affects consolidation priority)"""
    FORGOTTEN = 1.0     # Low priority
    ROUTINE = 3.0       # Normal daily memory
    NOTABLE = 6.0       # Worth remembering
    SIGNIFICANT = 8.0   # Life-changing
    CORE_IDENTITY = 10.0 # Defines who they are


# ============================================================================
# MEMORY DATA STRUCTURES
# ============================================================================

@dataclass
class Memory:
    """Individual memory unit"""
    id: str
    content: str                          # What happened/was learned
    memory_type: MemoryType
    timestamp: datetime

    # Metadata
    importance: float = 5.0                # 1-10 scale
    emotional_valence: float = 0.0         # -1 (bad) to +1 (good)
    participants: List[str] = field(default_factory=list)  # Who was involved
    location: str = ""                    # Where it happened

    # Consolidation tracking
    access_count: int = 0                 # Times retrieved (boosts importance)
    last_accessed: Optional[datetime] = None
    consolidated: bool = False            # Has it moved to semantic?
    consolidation_source_ids: List[str] = field(default_factory=list)

    # Relationship to other memories
    related_memory_ids: List[str] = field(default_factory=list)
    contradicts_memory_ids: List[str] = field(default_factory=list)

    # For temporal landmarks
    is_temporal_landmark: bool = False
    landmark_type: Optional[str] = None   # "first", "peak_emotion", "transition", etc

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            "id": self.id,
            "content": self.content,
            "memory_type": self.memory_type.value,
            "timestamp": self.timestamp.isoformat(),
            "importance": self.importance,
            "emotional_valence": self.emotional_valence,
            "participants": self.participants,
            "location": self.location,
            "access_count": self.access_count,
            "last_accessed": self.last_accessed.isoformat() if self.last_accessed else None,
            "consolidated": self.consolidated,
            "consolidation_source_ids": self.consolidation_source_ids,
            "is_temporal_landmark": self.is_temporal_landmark,
            "landmark_type": self.landmark_type,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Memory":
        """Create from dictionary"""
        data = data.copy()
        data["memory_type"] = MemoryType(data["memory_type"])
        data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        if data.get("last_accessed"):
            data["last_accessed"] = datetime.fromisoformat(data["last_accessed"])
        return cls(**data)


@dataclass
class TemporalLandmark:
    """Anchor points in autobiographical memory (like memories form clusters around them)"""
    id: str
    memory_id: str
    landmark_type: str  # "first", "peak_emotion", "transition", "social", "achievement"
    importance_boost: float = 2.0
    related_memory_ids: List[str] = field(default_factory=list)
    narrative_summary: str = ""


@dataclass
class AutobiographicalNarrative:
    """Life story constructed from memories and temporal landmarks"""
    character_id: str
    narrative: str                          # Coherent life story text
    key_themes: List[str] = field(default_factory=list)
    core_identity_traits: Dict[str, float] = field(default_factory=dict)
    generated_at: datetime = field(default_factory=datetime.now)
    memory_ids_used: List[str] = field(default_factory=list)
    coherence_score: float = 0.0  # 0-1: how coherent is the narrative?


# ============================================================================
# CORE MEMORY SYSTEM
# ============================================================================

class HierarchicalMemory:
    """
    Main hierarchical memory system implementing 6-tier architecture.

    Features:
    - Memory storage with tier management
    - Importance-based retrieval
    - Temporal landmark detection
    - Access count boosting
    - Persistent storage (JSON)
    - Memory relationship tracking

    Example:
        >>> memory = HierarchicalMemory(character_id="agent_001")
        >>> memory.store("Met the team to discuss Q1 goals",
        ...              importance=7.0,
        ...              emotional_valence=0.5,
        ...              participants=["Alice", "Bob"])
        >>> relevant = memory.retrieve("team meeting", top_k=5)
    """

    # Default configuration
    DEFAULT_CONFIG = {
        "max_working_memories": 10,
        "max_mid_term_memories": 100,
        "recency_decay_rate": 0.995,      # Per hour
        "reflection_threshold": 150.0,
        "consolidation_window_hours": 24,
        "temporal_landmark_threshold": 0.6,
    }

    def __init__(self,
                 character_id: str,
                 storage_path: Optional[Union[str, Path]] = None,
                 config: Optional[Dict[str, Any]] = None):
        """
        Initialize hierarchical memory system.

        Args:
            character_id: Unique identifier for this character/entity
            storage_path: Path for persistent storage (None = in-memory only)
            config: Configuration overrides
        """
        self.character_id = character_id
        self.storage_path = Path(storage_path) if storage_path else None
        self.config = {**self.DEFAULT_CONFIG, **(config or {})}

        # Memory storage
        self.memories: Dict[str, Memory] = {}
        self.temporal_landmarks: Dict[str, TemporalLandmark] = {}
        self.autobiographical_narratives: List[AutobiographicalNarrative] = []

        # Consolidation tracking
        self.importance_accumulator: float = 0.0
        self.last_reflection_time: datetime = datetime.now()
        self.last_consolidation_time: datetime = datetime.now()

        # Load existing data if available
        if self.storage_path:
            self._load()

    # ======================================================================
    # MEMORY STORAGE
    # ======================================================================

    def store(self,
              content: str,
              memory_type: Union[MemoryType, str] = MemoryType.EPISODIC,
              importance: float = 5.0,
              emotional_valence: float = 0.0,
              participants: Optional[List[str]] = None,
              location: str = "",
              metadata: Optional[Dict[str, Any]] = None) -> Memory:
        """
        Store a new memory.

        Args:
            content: What happened/was learned
            memory_type: Type tier (MemoryType enum or string)
            importance: 1-10 scale, affects retrieval and consolidation
            emotional_valence: -1 (bad) to +1 (good)
            participants: List of who was involved
            location: Where it happened
            metadata: Additional metadata to store

        Returns:
            The created Memory object
        """
        if isinstance(memory_type, str):
            memory_type = MemoryType(memory_type)

        memory_id = self._generate_memory_id(content)

        memory = Memory(
            id=memory_id,
            content=content,
            memory_type=memory_type,
            timestamp=datetime.now(),
            importance=importance,
            emotional_valence=emotional_valence,
            participants=participants or [],
            location=location,
        )

        self.memories[memory_id] = memory

        # Update importance accumulator
        self.importance_accumulator += importance

        # Check for temporal landmarks
        self._check_temporal_landmark(memory)

        # Manage tier capacity
        self._manage_tier_capacity(memory_type)

        # Auto-save if enabled
        if self.storage_path:
            self._save()

        return memory

    def store_working(self, content: str, **kwargs) -> Memory:
        """Store in working memory (current attention)."""
        return self.store(content, MemoryType.WORKING, **kwargs)

    def store_mid_term(self, content: str, **kwargs) -> Memory:
        """Store in mid-term memory (session buffer)."""
        return self.store(content, MemoryType.MID_TERM, **kwargs)

    def store_episodic(self, content: str, **kwargs) -> Memory:
        """Store as episodic memory (specific event)."""
        return self.store(content, MemoryType.EPISODIC, **kwargs)

    def store_semantic(self, content: str, **kwargs) -> Memory:
        """Store as semantic memory (fact/pattern)."""
        return self.store(content, MemoryType.SEMANTIC, **kwargs)

    def store_procedural(self, content: str, **kwargs) -> Memory:
        """Store as procedural memory (skill)."""
        return self.store(content, MemoryType.PROCEDURAL, **kwargs)

    # ======================================================================
    # MEMORY RETRIEVAL
    # ======================================================================

    def retrieve(self,
                 query: str,
                 top_k: int = 10,
                 memory_type: Optional[Union[MemoryType, str]] = None,
                 α_recency: float = 1.0,
                 α_importance: float = 1.0,
                 α_relevance: float = 1.0) -> List[Memory]:
        """
        Retrieve memories with weighted scoring.

        Args:
            query: Search query text
            top_k: Maximum number of results
            memory_type: Filter by memory type (None = all)
            α_recency: Weight for recency (how much to prioritize recent)
            α_importance: Weight for importance
            α_relevance: Weight for semantic relevance

        Returns:
            List of retrieved memories
        """
        if isinstance(memory_type, str):
            memory_type = MemoryType(memory_type)

        # Filter by type if specified
        memories = list(self.memories.values())
        if memory_type:
            memories = [m for m in memories if m.memory_type == memory_type]

        # Score each memory
        results = []
        current_time = datetime.now()

        for memory in memories:
            # Recency score (exponential decay per hour)
            hours_ago = (current_time - memory.timestamp).total_seconds() / 3600
            recency = self.config["recency_decay_rate"] ** hours_ago

            # Importance score (normalized)
            importance = memory.importance / 10.0

            # Relevance score (word overlap)
            relevance = self._calculate_relevance(query, memory.content)

            # Combined score
            total_weight = α_recency + α_importance + α_relevance
            score = (
                α_recency * recency +
                α_importance * importance +
                α_relevance * relevance
            ) / total_weight if total_weight > 0 else 0

            results.append((score, memory))

        # Sort by score and return top_k
        results.sort(reverse=True, key=lambda x: x[0])
        retrieved = [m for _, m in results[:top_k]]

        # Update access counts
        for memory in retrieved:
            memory.access_count += 1
            memory.last_accessed = datetime.now()
            # Slight importance boost on retrieval
            memory.importance = min(memory.importance * 1.05, 10.0)

        return retrieved

    def get_by_id(self, memory_id: str) -> Optional[Memory]:
        """Get a specific memory by ID."""
        return self.memories.get(memory_id)

    def get_memories_by_type(self, memory_type: Union[MemoryType, str]) -> List[Memory]:
        """Get all memories of a specific type."""
        if isinstance(memory_type, str):
            memory_type = MemoryType(memory_type)
        return [m for m in self.memories.values() if m.memory_type == memory_type]

    def get_recent(self, hours: int = 24, top_k: int = 10) -> List[Memory]:
        """Get recent memories within specified hours."""
        cutoff = datetime.now() - timedelta(hours=hours)
        recent = [m for m in self.memories.values() if m.timestamp > cutoff]
        recent.sort(key=lambda x: x.timestamp, reverse=True)
        return recent[:top_k]

    def get_important(self, threshold: float = 6.0, top_k: int = 10) -> List[Memory]:
        """Get memories above importance threshold."""
        important = [m for m in self.memories.values() if m.importance >= threshold]
        important.sort(key=lambda x: x.importance, reverse=True)
        return important[:top_k]

    # ======================================================================
    # TEMPORAL LANDMARKS
    # ======================================================================

    def get_temporal_landmarks(self) -> List[TemporalLandmark]:
        """Get all temporal landmarks, sorted by memory timestamp."""
        landmarks = list(self.temporal_landmarks.values())
        landmarks.sort(
            key=lambda tl: self.memories.get(tl.memory_id, Memory(
                id="", content="", memory_type=MemoryType.EPISODIC,
                timestamp=datetime.min
            )).timestamp
        )
        return landmarks

    def _check_temporal_landmark(self, memory: Memory):
        """
        Detect if memory qualifies as temporal landmark.
        Landmarks organize autobiographical memory into clusters.
        """
        score = 0.0
        landmark_type = None

        # FIRST: Check if this is first of its kind
        recent_similar = self._find_similar_memories(
            memory.content, hours_back=168, limit=3
        )
        if len(recent_similar) == 0:
            score += 0.3
            landmark_type = "first"

        # PEAK: Check emotional intensity
        if abs(memory.emotional_valence) > 0.7:
            score += 0.3
            if landmark_type is None:
                landmark_type = "peak_emotion"

        # TRANSITION: Check location change
        recent_locations = [
            m.location for m in list(self.memories.values())[-5:]
            if m.location
        ]
        if memory.location and memory.location not in recent_locations:
            score += 0.2
            if landmark_type is None:
                landmark_type = "transition"

        # SOCIAL: Check participant count
        if len(memory.participants) >= 3:
            score += 0.2
            if landmark_type is None:
                landmark_type = "social"

        # Create landmark if threshold exceeded
        threshold = self.config.get("temporal_landmark_threshold", 0.6)
        if score >= threshold:
            landmark_id = f"landmark_{memory.id}"
            landmark = TemporalLandmark(
                id=landmark_id,
                memory_id=memory.id,
                landmark_type=landmark_type or "significant",
                importance_boost=min(score * 2.0, 3.0)
            )
            self.temporal_landmarks[landmark_id] = landmark
            memory.is_temporal_landmark = True
            memory.landmark_type = landmark_type
            memory.importance = min(memory.importance + landmark.importance_boost, 10.0)

    # ======================================================================
    # AUTOBIOGRAPHICAL NARRATIVE
    # ======================================================================

    def generate_narrative(self) -> AutobiographicalNarrative:
        """
        Generate coherent life story from memories, landmarks, and themes.
        Implements autobiographical narrative identity theory.
        """
        # Get temporal landmarks
        landmarks = self.get_temporal_landmarks()

        # Get key memories
        key_memories = self.get_important(threshold=6.0, top_k=20)

        # Build narrative structure
        narrative_parts = []

        # Opening: Core traits
        core_traits = self._extract_core_traits()
        if core_traits:
            traits_str = ", ".join([f"{k}:{v:.1f}" for k, v in core_traits.items()])
            narrative_parts.append(f"I am fundamentally: {traits_str}")

        # Body: Key life events
        for landmark in landmarks[:5]:
            memory = self.memories.get(landmark.memory_id)
            if memory:
                narrative_parts.append(
                    f"* {landmark.landmark_type.upper()}: {memory.content[:150]}"
                )

        # Patterns: What I've learned
        semantic_memories = self.get_memories_by_type(MemoryType.SEMANTIC)
        if semantic_memories:
            narrative_parts.append("What I've learned:")
            for m in semantic_memories[:3]:
                narrative_parts.append(f"  - {m.content[:100]}")

        # Closing
        narrative_parts.append("I continue to grow and learn from my experiences.")

        narrative_text = "\n".join(narrative_parts)

        autobio = AutobiographicalNarrative(
            character_id=self.character_id,
            narrative=narrative_text,
            key_themes=self._extract_themes_from_memories(key_memories),
            core_identity_traits=core_traits,
            memory_ids_used=[m.id for m in key_memories],
            coherence_score=self._calculate_narrative_coherence(narrative_text, key_memories)
        )

        self.autobiographical_narratives.append(autobio)
        return autobio

    def get_narrative_context(self, limit: int = 500) -> str:
        """Get recent narrative for character context."""
        if not self.autobiographical_narratives:
            return "No autobiography generated yet."
        latest = self.autobiographical_narratives[-1]
        return latest.narrative[:limit]

    # ======================================================================
    # MEMORY RELATIONSHIPS
    # ======================================================================

    def relate_memories(self, memory_id_1: str, memory_id_2: str):
        """Mark two memories as related."""
        if memory_id_1 in self.memories and memory_id_2 in self.memories:
            if memory_id_2 not in self.memories[memory_id_1].related_memory_ids:
                self.memories[memory_id_1].related_memory_ids.append(memory_id_2)
            if memory_id_1 not in self.memories[memory_id_2].related_memory_ids:
                self.memories[memory_id_2].related_memory_ids.append(memory_id_1)

    def contradict_memories(self, memory_id_1: str, memory_id_2: str):
        """Mark two memories as contradictory."""
        if memory_id_1 in self.memories and memory_id_2 in self.memories:
            if memory_id_2 not in self.memories[memory_id_1].contradicts_memory_ids:
                self.memories[memory_id_1].contradicts_memory_ids.append(memory_id_2)
            if memory_id_1 not in self.memories[memory_id_2].contradicts_memory_ids:
                self.memories[memory_id_2].contradicts_memory_ids.append(memory_id_1)

    def get_related_memories(self, memory_id: str) -> List[Memory]:
        """Get memories related to the given memory."""
        if memory_id not in self.memories:
            return []
        related_ids = self.memories[memory_id].related_memory_ids
        return [self.memories[rid] for rid in related_ids if rid in self.memories]

    # ======================================================================
    # CONSOLIDATION TRIGGERS
    # ======================================================================

    def should_consolidate_reflection(self) -> bool:
        """Check if reflection consolidation should trigger."""
        return self.importance_accumulator >= self.config["reflection_threshold"]

    def should_consolidate_episodic(self) -> bool:
        """Check if episodic to semantic consolidation should trigger."""
        hours_since = (datetime.now() - self.last_consolidation_time).total_seconds() / 3600
        if hours_since < self.config["consolidation_window_hours"]:
            return False

        unconsolidated = [
            m for m in self.memories.values()
            if not m.consolidated
            and m.memory_type == MemoryType.EPISODIC
            and (datetime.now() - m.timestamp).total_seconds() > 86400
        ]
        return len(unconsolidated) >= 3

    # ======================================================================
    # PERSISTENCE
    # ======================================================================

    def save(self):
        """Save to persistent storage."""
        if self.storage_path:
            self._save()

    def load(self):
        """Load from persistent storage."""
        if self.storage_path:
            self._load()

    def _save(self):
        """Internal save method."""
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "character_id": self.character_id,
            "memories": [m.to_dict() for m in self.memories.values()],
            "temporal_landmarks": [asdict(tl) for tl in self.temporal_landmarks.values()],
            "autobiographical_narratives": [asdict(n) for n in self.autobiographical_narratives],
            "importance_accumulator": self.importance_accumulator,
            "last_reflection_time": self.last_reflection_time.isoformat(),
            "last_consolidation_time": self.last_consolidation_time.isoformat(),
            "config": self.config,
        }

        with open(self.storage_path, "w") as f:
            json.dump(data, f, indent=2)

    def _load(self):
        """Internal load method."""
        if not self.storage_path.exists():
            return

        try:
            with open(self.storage_path, "r") as f:
                data = json.load(f)

            self.memories = {
                m["id"]: Memory.from_dict(m)
                for m in data.get("memories", [])
            }

            self.temporal_landmarks = {
                tl["id"]: TemporalLandmark(**tl)
                for tl in data.get("temporal_landmarks", [])
            }

            self.autobiographical_narratives = [
                AutobiographicalNarrative(**n)
                for n in data.get("autobiographical_narratives", [])
            ]

            self.importance_accumulator = data.get("importance_accumulator", 0.0)

            if rt := data.get("last_reflection_time"):
                self.last_reflection_time = datetime.fromisoformat(rt)
            if ct := data.get("last_consolidation_time"):
                self.last_consolidation_time = datetime.fromisoformat(ct)

        except Exception as e:
            print(f"Error loading memory: {e}")

    def export(self) -> Dict[str, Any]:
        """Export all memory data as dictionary."""
        return {
            "character_id": self.character_id,
            "memories": [m.to_dict() for m in self.memories.values()],
            "temporal_landmarks": [asdict(tl) for tl in self.temporal_landmarks.values()],
            "autobiographical_narratives": [asdict(n) for n in self.autobiographical_narratives],
        }

    # ======================================================================
    # STATS & HEALTH
    # ======================================================================

    def get_stats(self) -> Dict[str, Any]:
        """Get memory system statistics."""
        memory_counts = defaultdict(int)
        for m in self.memories.values():
            memory_counts[m.memory_type.value] += 1

        consolidated = sum(1 for m in self.memories.values() if m.consolidated)

        avg_importance = 0.0
        if self.memories:
            avg_importance = np.mean([m.importance for m in self.memories.values()])

        return {
            "character_id": self.character_id,
            "total_memories": len(self.memories),
            "by_type": dict(memory_counts),
            "consolidated": consolidated,
            "unconsolidated": len(self.memories) - consolidated,
            "average_importance": avg_importance,
            "temporal_landmarks": len(self.temporal_landmarks),
            "narratives_generated": len(self.autobiographical_narratives),
            "importance_accumulator": self.importance_accumulator,
        }

    # ======================================================================
    # PRIVATE HELPER METHODS
    # ======================================================================

    def _generate_memory_id(self, content: str) -> str:
        """Generate unique memory ID."""
        seed = f"{self.character_id}{content}{datetime.now().isoformat()}"
        return hashlib.md5(seed.encode()).hexdigest()[:16]

    def _manage_tier_capacity(self, memory_type: MemoryType):
        """Evict old memories when tier is at capacity."""
        if memory_type == MemoryType.WORKING:
            max_memories = self.config.get("max_working_memories", 10)
            self._evict_from_tier(memory_type, max_memories)
        elif memory_type == MemoryType.MID_TERM:
            max_memories = self.config.get("max_mid_term_memories", 100)
            self._evict_from_tier(memory_type, max_memories)

    def _evict_from_tier(self, memory_type: MemoryType, max_count: int):
        """Evict least important memories from tier."""
        tier_memories = [m for m in self.memories.values() if m.memory_type == memory_type]
        if len(tier_memories) > max_count:
            # Sort by importance * recency
            tier_memories.sort(
                key=lambda m: m.importance * (0.5 if m.access_count == 0 else 1.0)
            )
            # Evict the least important
            to_evict = tier_memories[:-max_count]
            for m in to_evict:
                del self.memories[m.id]

    def _find_similar_memories(self, content: str, hours_back: int = 168,
                              limit: int = 5) -> List[Memory]:
        """Find memories similar to content."""
        cutoff = datetime.now() - timedelta(hours=hours_back)
        recent = [m for m in self.memories.values() if m.timestamp > cutoff]

        scored = [
            (self._calculate_relevance(content, m.content), m)
            for m in recent
        ]
        scored.sort(reverse=True, key=lambda x: x[0])
        return [m for _, m in scored[:limit] if m[0] > 0]

    def _calculate_relevance(self, text1: str, text2: str) -> float:
        """Simple relevance calculation (word overlap)."""
        words1 = set(w.lower() for w in text1.split() if len(w) > 2)
        words2 = set(w.lower() for w in text2.split() if len(w) > 2)

        if not words1 or not words2:
            return 0.0

        intersection = len(words1 & words2)
        union = len(words1 | words2)

        return intersection / union if union > 0 else 0.0

    def _extract_core_traits(self) -> Dict[str, float]:
        """Extract character core traits from memories."""
        traits = defaultdict(list)

        for mem in self.memories.values():
            if mem.importance >= 7.0:
                if mem.emotional_valence > 0.5:
                    traits["optimistic"].append(mem.emotional_valence)
                elif mem.emotional_valence < -0.5:
                    traits["cautious"].append(-mem.emotional_valence)

                if len(mem.participants) >= 2:
                    traits["social"].append(0.8)
                elif "alone" in mem.content.lower():
                    traits["introspective"].append(0.8)

        return {trait: np.mean(vals) for trait, vals in traits.items() if vals}

    def _extract_themes_from_memories(self, memories: List[Memory]) -> List[str]:
        """Extract themes/topics from memories."""
        themes = defaultdict(int)

        for mem in memories:
            words = set(w.lower() for w in mem.content.split() if len(w) > 4)
            for word in words:
                themes[word] += 1

        sorted_themes = sorted(themes.items(), key=lambda x: x[1], reverse=True)
        return [word for word, _ in sorted_themes[:5]]

    def _calculate_narrative_coherence(self, narrative: str,
                                       memories: List[Memory]) -> float:
        """Calculate how coherent the narrative is (0-1)."""
        words_in_narrative = set(narrative.lower().split())

        coherence_scores = []
        for mem in memories:
            words_in_memory = set(mem.content.lower().split())
            overlap = len(words_in_narrative & words_in_memory)
            if overlap > 0:
                coherence_scores.append(min(overlap / len(words_in_narrative), 1.0))

        return np.mean(coherence_scores) if coherence_scores else 0.5


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def create_memory_store(character_id: str,
                       storage_path: Optional[str] = None) -> HierarchicalMemory:
    """Convenience function to create a new memory store."""
    return HierarchicalMemory(character_id=character_id, storage_path=storage_path)
