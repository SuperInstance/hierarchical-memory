"""
Hierarchical Memory System - Consolidation Module
=================================================

Advanced memory consolidation algorithms inspired by neuroscience:
- Episodic to semantic consolidation (hippocampus → neocortex)
- Reflection consolidation (default mode network)
- Cluster-based pattern extraction
- Adaptive consolidation timing
- Incremental consolidation

Consolidation is the process of stabilizing a memory trace after the initial
acquisition. This system mimics biological memory consolidation through
multiple algorithms.
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict
import numpy as np
import hashlib

try:
    from sklearn.cluster import DBSCAN
    from sklearn.feature_extraction.text import TfidfVectorizer
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    DBSCAN = None
    TfidfVectorizer = None

from .core import Memory, MemoryType, TemporalLandmark, HierarchicalMemory


# ============================================================================
# CONSOLIDATION STRATEGY INTERFACE
# ============================================================================

class ConsolidationStrategy:
    """Base class for consolidation strategies"""

    def should_consolidate(self, memory_system: HierarchicalMemory) -> bool:
        """Determine if consolidation should happen"""
        raise NotImplementedError

    def select_memories(self, memory_system: HierarchicalMemory) -> List[Memory]:
        """Select memories to consolidate"""
        raise NotImplementedError

    def consolidate(self, memories: List[Memory],
                    memory_system: HierarchicalMemory) -> List[Memory]:
        """Perform consolidation, returns new semantic memories"""
        raise NotImplementedError


# ============================================================================
# REFLECTION CONSOLIDATION
# ============================================================================

class ReflectionConsolidation(ConsolidationStrategy):
    """
    Immediate reflection consolidation (insights phase).
    Triggered when importance accumulator reaches threshold.
    Mimics the default mode network synthesizing meaning.

    This creates high-level "meta-memories" about patterns in recent experiences.
    """

    def __init__(self, threshold: float = 150.0):
        self.threshold = threshold

    def should_consolidate(self, memory_system: HierarchicalMemory) -> bool:
        """Check if importance threshold reached"""
        return memory_system.importance_accumulator >= self.threshold

    def select_memories(self, memory_system: HierarchicalMemory) -> List[Memory]:
        """Select recent important memories"""
        cutoff = datetime.now() - timedelta(hours=24)
        return [
            m for m in memory_system.memories.values()
            if m.timestamp > cutoff and m.importance >= 6.0
        ][:100]

    def consolidate(self, memories: List[Memory],
                    memory_system: HierarchicalMemory) -> List[Memory]:
        """Generate reflection from memories"""
        if not memories:
            return []

        reflection_content = self._generate_reflection(memories)

        # Create semantic memory
        memory_id = hashlib.md5(
            f"reflection_{memory_system.character_id}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]

        reflection = Memory(
            id=memory_id,
            content=reflection_content,
            memory_type=MemoryType.SEMANTIC,
            timestamp=datetime.now(),
            importance=8.0,
            emotional_valence=np.mean([m.emotional_valence for m in memories]),
            consolidated=True,
            consolidation_source_ids=[m.id for m in memories]
        )

        # Reset accumulator
        memory_system.importance_accumulator = 0.0
        memory_system.last_reflection_time = datetime.now()

        return [reflection]

    def _generate_reflection(self, memories: List[Memory]) -> str:
        """Generate reflection/insight from memories"""
        topics = defaultdict(list)

        for mem in memories:
            # Extract main topic (first few words)
            words = mem.content.split()[:3]
            topic = " ".join(words)
            topics[topic].append(mem.content)

        reflection_parts = []
        for topic, contents in sorted(
            topics.items(),
            key=lambda x: len(x[1]),
            reverse=True
        )[:3]:
            reflection_parts.append(
                f"I notice I've been focused on: {topic} ({len(contents)} experiences)"
            )

        return "\n".join(reflection_parts) if reflection_parts else "Recent reflections on my experiences."


# ============================================================================
# EPISODIC TO SEMANTIC CONSOLIDATION
# ============================================================================

class EpisodicToSemanticConsolidation(ConsolidationStrategy):
    """
    Sleep-like consolidation: Episodic → Semantic (hours/days to weeks).
    Extracts patterns from multiple episodic memories into semantic knowledge.
    Mimics hippocampus → neocortex transfer during sleep.

    Clusters similar episodic memories and extracts general patterns.
    """

    def __init__(self, consolidation_window_hours: int = 24,
                 min_cluster_size: int = 3,
                 similarity_threshold: float = 0.85):
        self.consolidation_window_hours = consolidation_window_hours
        self.min_cluster_size = min_cluster_size
        self.similarity_threshold = similarity_threshold

    def should_consolidate(self, memory_system: HierarchicalMemory) -> bool:
        """Check if enough time has passed since last consolidation"""
        hours_since = (
            datetime.now() - memory_system.last_consolidation_time
        ).total_seconds() / 3600

        if hours_since < self.consolidation_window_hours:
            return False

        # Check for unconsolidated episodic memories older than 24h
        unconsolidated = [
            m for m in memory_system.memories.values()
            if not m.consolidated
            and m.memory_type == MemoryType.EPISODIC
            and (datetime.now() - m.timestamp).total_seconds() > 86400
        ]

        return len(unconsolidated) >= self.min_cluster_size

    def select_memories(self, memory_system: HierarchicalMemory) -> List[Memory]:
        """Select unconsolidated episodic memories"""
        return [
            m for m in memory_system.memories.values()
            if not m.consolidated
            and m.memory_type == MemoryType.EPISODIC
            and (datetime.now() - m.timestamp).total_seconds() > 86400
        ]

    def consolidate(self, memories: List[Memory],
                    memory_system: HierarchicalMemory) -> List[Memory]:
        """Cluster and extract patterns"""
        if len(memories) < self.min_cluster_size:
            return []

        # Cluster similar memories
        if SKLEARN_AVAILABLE:
            clusters = self._cluster_with_sklearn(memories)
        else:
            clusters = self._cluster_simple(memories)

        # Create semantic memories from clusters
        consolidated = []
        for cluster in clusters:
            if len(cluster) >= self.min_cluster_size:
                semantic = self._extract_pattern(cluster, memory_system)
                if semantic:
                    consolidated.append(semantic)

        # Update consolidation time
        memory_system.last_consolidation_time = datetime.now()

        return consolidated

    def _cluster_simple(self, memories: List[Memory]) -> List[List[Memory]]:
        """Simple clustering based on word overlap"""
        clusters = []
        used = set()

        for i, mem1 in enumerate(memories):
            if i in used:
                continue

            cluster = [mem1]
            used.add(i)

            for j, mem2 in enumerate(memories[i+1:], start=i+1):
                if j in used:
                    continue

                similarity = self._calculate_similarity(mem1.content, mem2.content)
                if similarity >= self.similarity_threshold:
                    cluster.append(mem2)
                    used.add(j)

            clusters.append(cluster)

        return clusters

    def _cluster_with_sklearn(self, memories: List[Memory]) -> List[List[Memory]]:
        """Cluster using TF-IDF and DBSCAN"""
        try:
            texts = [m.content for m in memories]
            vectorizer = TfidfVectorizer(max_features=100)
            vectors = vectorizer.fit_transform(texts).toarray()

            clustering = DBSCAN(eps=0.5, min_samples=self.min_cluster_size)
            labels = clustering.fit_predict(vectors)

            clusters = []
            for label in set(labels):
                if label == -1:  # Noise
                    continue
                cluster = [m for i, m in enumerate(memories) if labels[i] == label]
                if len(cluster) >= self.min_cluster_size:
                    clusters.append(cluster)

            return clusters

        except Exception:
            return self._cluster_simple(memories)

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity using word overlap"""
        words1 = set(w.lower() for w in text1.split() if len(w) > 2)
        words2 = set(w.lower() for w in text2.split() if len(w) > 2)

        if not words1 or not words2:
            return 0.0

        intersection = len(words1 & words2)
        union = len(words1 | words2)

        return intersection / union if union > 0 else 0.0

    def _extract_pattern(self, cluster: List[Memory],
                         memory_system: HierarchicalMemory) -> Optional[Memory]:
        """Extract semantic pattern from cluster"""
        # Extract common themes
        word_freq = defaultdict(int)
        for mem in cluster:
            words = mem.content.lower().split()
            for word in words:
                if len(word) > 3:
                    word_freq[word] += 1

        # Find common words (across at least 50% of memories)
        threshold = len(cluster) // 2
        common_words = [
            word for word, freq in word_freq.items()
            if freq >= threshold
        ][:5]

        if not common_words:
            return None

        # Create semantic memory
        pattern_content = (
            f"Pattern: Based on {len(cluster)} experiences, "
            f"I consistently encounter situations involving {', '.join(common_words)}. "
            f"This appears to be a recurring pattern in my life."
        )

        memory_id = hashlib.md5(
            f"pattern_{cluster[0].id}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]

        semantic = Memory(
            id=memory_id,
            content=pattern_content,
            memory_type=MemoryType.SEMANTIC,
            timestamp=datetime.now(),
            importance=np.mean([m.importance for m in cluster]),
            emotional_valence=np.mean([m.emotional_valence for m in cluster]),
            consolidated=True,
            consolidation_source_ids=[m.id for m in cluster]
        )

        # Mark originals as consolidated
        for mem in cluster:
            mem.consolidated = True

        return semantic


# ============================================================================
# CLUSTER-BASED CONSOLIDATION
# ============================================================================

class ClusterBasedConsolidation(ConsolidationStrategy):
    """
    Consolidate memories by clustering similar ones using TF-IDF.

    Example:
    - "Fought goblin near river"
    - "Defeated goblin by bridge"
    - "Killed goblin at water crossing"
    -> "Encounters with goblins near water are common"
    """

    def __init__(self, min_cluster_size: int = 3):
        self.min_cluster_size = min_cluster_size

    def should_consolidate(self, memory_system: HierarchicalMemory) -> bool:
        """Consolidate when we have enough unconsolidated memories"""
        unconsolidated = [
            m for m in memory_system.memories.values()
            if not m.consolidated and m.memory_type == MemoryType.EPISODIC
        ]
        return len(unconsolidated) >= self.min_cluster_size * 3

    def select_memories(self, memory_system: HierarchicalMemory) -> List[Memory]:
        """Select all unconsolidated episodic memories"""
        return [
            m for m in memory_system.memories.values()
            if not m.consolidated and m.memory_type == MemoryType.EPISODIC
        ]

    def consolidate(self, memories: List[Memory],
                    memory_system: HierarchicalMemory) -> List[Memory]:
        """Cluster and consolidate memories"""
        if len(memories) < self.min_cluster_size:
            return []

        # Use the episodic to semantic consolidation
        strategy = EpisodicToSemanticConsolidation(
            min_cluster_size=self.min_cluster_size
        )
        return strategy.consolidate(memories, memory_system)


# ============================================================================
# ADAPTIVE CONSOLIDATION
# ============================================================================

class AdaptiveConsolidation(ConsolidationStrategy):
    """
    Learns optimal consolidation timing from experience.

    Tracks:
    - When consolidation helps retrieval
    - When consolidation loses important details
    - Optimal batch sizes and intervals
    """

    def __init__(self):
        self.consolidation_history: List[Dict] = []
        self.retrieval_quality_before: Dict[str, float] = {}
        self.retrieval_quality_after: Dict[str, float] = {}

        # Learned parameters
        self.optimal_batch_size = 20
        self.optimal_interval_hours = 24
        self.last_consolidation: Optional[datetime] = None

    def should_consolidate(self, memory_system: HierarchicalMemory) -> bool:
        """Consolidate based on learned timing"""
        if self.last_consolidation is None:
            # First time - use default
            return len([
                m for m in memory_system.memories.values()
                if not m.consolidated and m.memory_type == MemoryType.EPISODIC
            ]) >= self.optimal_batch_size

        hours_since = (datetime.now() - self.last_consolidation).total_seconds() / 3600

        if hours_since < self.optimal_interval_hours:
            return False

        unconsolidated = [
            m for m in memory_system.memories.values()
            if not m.consolidated and m.memory_type == MemoryType.EPISODIC
        ]

        return len(unconsolidated) >= self.optimal_batch_size

    def select_memories(self, memory_system: HierarchicalMemory) -> List[Memory]:
        """Select batch of optimal size"""
        unconsolidated = [
            m for m in memory_system.memories.values()
            if not m.consolidated and m.memory_type == MemoryType.EPISODIC
        ]

        # Sort by importance (consolidate less important first)
        unconsolidated.sort(key=lambda m: m.importance)

        return unconsolidated[:self.optimal_batch_size]

    def consolidate(self, memories: List[Memory],
                    memory_system: HierarchicalMemory) -> List[Memory]:
        """Consolidate and track quality"""
        # Record before state
        timestamp = datetime.now().isoformat()
        self.retrieval_quality_before[timestamp] = self._assess_quality(memories)

        # Perform consolidation
        strategy = ClusterBasedConsolidation(min_cluster_size=3)
        consolidated = strategy.consolidate(memories, memory_system)

        # Record after state
        self.retrieval_quality_after[timestamp] = self._assess_quality(consolidated)

        # Update learned parameters
        self._update_parameters()

        self.last_consolidation = datetime.now()

        # Log
        self.consolidation_history.append({
            "timestamp": timestamp,
            "input_count": len(memories),
            "output_count": len(consolidated),
            "quality_change": self.retrieval_quality_after[timestamp] - self.retrieval_quality_before[timestamp]
        })

        return consolidated

    def _assess_quality(self, memories: List[Memory]) -> float:
        """Assess memory quality based on importance and recency"""
        if not memories:
            return 0.0

        scores = []
        for m in memories:
            age_hours = (datetime.now() - m.timestamp).total_seconds() / 3600
            recency_factor = 0.995 ** age_hours
            score = m.importance * recency_factor
            scores.append(score)

        return np.mean(scores)

    def _update_parameters(self):
        """Learn from consolidation history"""
        if len(self.consolidation_history) < 5:
            return

        # Calculate average improvement
        improvements = [
            entry["quality_change"]
            for entry in self.consolidation_history
            if "quality_change" in entry
        ]

        if improvements:
            avg_improvement = np.mean(improvements)

            # If consolidation helps, consolidate more often
            if avg_improvement > 0:
                self.optimal_interval_hours = max(12, self.optimal_interval_hours * 0.95)
            else:
                # If it hurts, consolidate less often
                self.optimal_interval_hours = min(72, self.optimal_interval_hours * 1.05)

    def get_learned_parameters(self) -> Dict[str, Any]:
        """Get learned consolidation parameters"""
        return {
            "optimal_batch_size": self.optimal_batch_size,
            "optimal_interval_hours": self.optimal_interval_hours,
            "consolidations_performed": len(self.consolidation_history),
            "avg_quality_change": np.mean([
                e.get("quality_change", 0)
                for e in self.consolidation_history
            ]) if self.consolidation_history else 0.0
        }


# ============================================================================
# INCREMENTAL CONSOLIDATION
# ============================================================================

class IncrementalConsolidation(ConsolidationStrategy):
    """
    Consolidate continuously in small batches.
    Don't wait for big batch - process memories as they come.
    """

    def __init__(self, batch_size: int = 5):
        self.batch_size = batch_size

    def should_consolidate(self, memory_system: HierarchicalMemory) -> bool:
        """Always ready to consolidate if we have a small batch"""
        unconsolidated = [
            m for m in memory_system.memories.values()
            if not m.consolidated and m.memory_type == MemoryType.EPISODIC
        ]
        return len(unconsolidated) >= self.batch_size

    def select_memories(self, memory_system: HierarchicalMemory) -> List[Memory]:
        """Select next batch (oldest first)"""
        unconsolidated = [
            m for m in memory_system.memories.values()
            if not m.consolidated and m.memory_type == MemoryType.EPISODIC
        ]

        unconsolidated.sort(key=lambda m: m.timestamp)
        return unconsolidated[:self.batch_size]

    def consolidate(self, memories: List[Memory],
                    memory_system: HierarchicalMemory) -> List[Memory]:
        """Quick consolidation of small batch"""
        if len(memories) < 2:
            return []

        groups = self._group_by_similarity(memories)

        consolidated = []
        for group in groups:
            if len(group) >= 2:
                merged = self._quick_merge(group, memory_system)
                if merged:
                    consolidated.append(merged)

        return consolidated

    def _group_by_similarity(self, memories: List[Memory]) -> List[List[Memory]]:
        """Group memories by shared keywords"""
        groups = []
        used = set()

        for i, m1 in enumerate(memories):
            if i in used:
                continue

            group = [m1]
            words1 = set(m1.content.lower().split())

            for j, m2 in enumerate(memories[i+1:], start=i+1):
                if j in used:
                    continue

                words2 = set(m2.content.lower().split())
                overlap = len(words1 & words2) / len(words1 | words2) if (words1 | words2) else 0

                if overlap > 0.3:  # 30% word overlap
                    group.append(m2)
                    used.add(j)

            used.add(i)
            groups.append(group)

        return groups

    def _quick_merge(self, memories: List[Memory],
                     memory_system: HierarchicalMemory) -> Optional[Memory]:
        """Quick merge of similar memories"""
        memories.sort(key=lambda m: m.importance, reverse=True)
        base = memories[0]

        content = f"Learned: {base.content} (from {len(memories)} similar experiences)"

        memory_id = hashlib.md5(
            f"incremental_{base.id}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]

        semantic = Memory(
            id=memory_id,
            content=content,
            memory_type=MemoryType.SEMANTIC,
            timestamp=datetime.now(),
            importance=base.importance,
            consolidated=True,
            consolidation_source_ids=[m.id for m in memories]
        )

        # Mark originals as consolidated
        for m in memories:
            m.consolidated = True

        return semantic


# ============================================================================
# CONSOLIDATION MANAGER
# ============================================================================

@dataclass
class ConsolidationResult:
    """Result of consolidation operation"""
    triggered: bool
    strategy: str
    input_count: int = 0
    output_count: int = 0
    new_memories: List[Memory] = field(default_factory=list)
    duration_seconds: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class ConsolidationEngine:
    """
    Main consolidation engine that orchestrates different strategies.

    Supports multiple consolidation strategies:
    - reflection: Immediate insights from recent experiences
    - episodic_semantic: Pattern extraction from episodic memories
    - cluster: TF-IDF based clustering
    - adaptive: Self-timing consolidation
    - incremental: Small-batch continuous consolidation
    """

    def __init__(self):
        self.strategies: Dict[str, ConsolidationStrategy] = {
            "reflection": ReflectionConsolidation(),
            "episodic_semantic": EpisodicToSemanticConsolidation(),
            "cluster": ClusterBasedConsolidation(),
            "adaptive": AdaptiveConsolidation(),
            "incremental": IncrementalConsolidation(),
        }
        self.default_strategy = "episodic_semantic"
        self.consolidation_log: List[ConsolidationResult] = []

    def consolidate(self,
                    memory_system: HierarchicalMemory,
                    strategy: Optional[str] = None,
                    force: bool = False) -> ConsolidationResult:
        """
        Run consolidation with specified or default strategy.

        Args:
            memory_system: The memory system to consolidate
            strategy: Strategy name (None = use default)
            force: Force consolidation even if should_consolidate returns False

        Returns:
            ConsolidationResult with details of the operation
        """
        import time
        start_time = time.time()

        strategy_name = strategy or self.default_strategy
        consolidation_strategy = self.strategies.get(strategy_name)

        if not consolidation_strategy:
            return ConsolidationResult(
                triggered=False,
                strategy=strategy_name,
                metadata={"error": f"Unknown strategy: {strategy_name}"}
            )

        # Check if should consolidate
        if not force and not consolidation_strategy.should_consolidate(memory_system):
            return ConsolidationResult(
                triggered=False,
                strategy=strategy_name,
                metadata={"reason": "Consolidation conditions not met"}
            )

        # Select memories
        memories_to_consolidate = consolidation_strategy.select_memories(memory_system)

        if not memories_to_consolidate:
            return ConsolidationResult(
                triggered=False,
                strategy=strategy_name,
                metadata={"reason": "No memories to consolidate"}
            )

        # Perform consolidation
        new_memories = consolidation_strategy.consolidate(
            memories_to_consolidate,
            memory_system
        )

        # Add new semantic memories to system
        for sem in new_memories:
            if sem.id not in memory_system.memories:
                memory_system.memories[sem.id] = sem

        # Record result
        duration = time.time() - start_time
        result = ConsolidationResult(
            triggered=True,
            strategy=strategy_name,
            input_count=len(memories_to_consolidate),
            output_count=len(new_memories),
            new_memories=new_memories,
            duration_seconds=duration,
        )

        self.consolidation_log.append(result)

        return result

    def consolidate_all(self,
                        memory_system: HierarchicalMemory,
                        force: bool = False) -> List[ConsolidationResult]:
        """
        Run all consolidation strategies in sequence.
        Useful for periodic maintenance.
        """
        results = []
        for strategy_name in self.strategies:
            result = self.consolidate(memory_system, strategy_name, force)
            results.append(result)

        return results

    def get_stats(self) -> Dict[str, Any]:
        """Get consolidation statistics"""
        if not self.consolidation_log:
            return {"message": "No consolidations yet"}

        total_consolidated = sum(r.input_count for r in self.consolidation_log if r.triggered)
        total_semantic = sum(r.output_count for r in self.consolidation_log if r.triggered)

        compression_ratio = total_consolidated / total_semantic if total_semantic > 0 else 0

        strategy_usage = defaultdict(int)
        for result in self.consolidation_log:
            if result.triggered:
                strategy_usage[result.strategy] += 1

        avg_duration = np.mean([
            r.duration_seconds for r in self.consolidation_log if r.triggered
        ]) if self.consolidation_log else 0

        return {
            "total_consolidations": len([r for r in self.consolidation_log if r.triggered]),
            "total_memories_consolidated": total_consolidated,
            "total_semantic_created": total_semantic,
            "compression_ratio": compression_ratio,
            "strategy_usage": dict(strategy_usage),
            "avg_duration_seconds": avg_duration,
        }


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def consolidate_reflection(memory_system: HierarchicalMemory,
                           threshold: float = 150.0) -> Optional[Memory]:
    """Run reflection consolidation."""
    engine = ConsolidationEngine()
    result = engine.consolidate(memory_system, "reflection", force=True)
    return result.new_memories[0] if result.new_memories else None


def consolidate_episodic_to_semantic(memory_system: HierarchicalMemory,
                                     min_cluster_size: int = 3) -> List[Memory]:
    """Run episodic to semantic consolidation."""
    engine = ConsolidationEngine()
    result = engine.consolidate(
        memory_system,
        "episodic_semantic",
        force=True
    )
    return result.new_memories
