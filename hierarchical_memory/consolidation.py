"""
Memory Consolidation Module
===========================

Implements knowledge consolidation with:
- KL divergence surprise detection
- Pattern extraction from episodic memories
- Episodic to semantic transfer
- Temporal landmark detection
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import numpy as np
import math

from .memory_types import Memory, MemoryType
from .episodic_memory import EpisodicMemory
from .semantic_memory import SemanticMemory


class ConsolidationEngine:
    """
    Memory Consolidation: Transfers episodic → semantic knowledge

    Neuroscience: Sleep-like process where hippocampal memories are
    integrated into neocortical semantic memory. Triggered by:
    - Importance accumulation
    - Surprise (novelty detection via KL divergence)
    - Temporal patterns
    """

    def __init__(self,
                 episodic_memory: EpisodicMemory,
                 semantic_memory: SemanticMemory):
        self.episodic = episodic_memory
        self.semantic = semantic_memory

        # Consolidation state
        self.importance_accumulator = 0.0
        self.last_consolidation = datetime.now()

        # Parameters
        self.CONSOLIDATION_INTERVAL_HOURS = 24
        self.IMPORTANCE_THRESHOLD = 150.0
        self.SURPRISE_THRESHOLD = 0.5
        self.PATTERN_SIMILARITY_THRESHOLD = 0.7

    def calculate_surprise(self, new_memory: Memory,
                          baseline_distribution: Dict[str, float]) -> float:
        """
        Calculate surprise using KL divergence.

        Args:
            new_memory: New memory to evaluate
            baseline_distribution: Baseline topic distribution

        Returns:
            Surprise score (higher = more surprising)
        """
        # Extract topic distribution from memory
        new_dist = self._extract_topic_distribution(new_memory.content)

        # Calculate KL divergence
        surprise = self._kl_divergence(new_dist, baseline_distribution)

        return surprise

    def _kl_divergence(self, dist_p: Dict[str, float],
                      dist_q: Dict[str, float]) -> float:
        """
        Calculate Kullback-Leibler divergence: D(P||Q)

        Measures how much distribution P differs from baseline Q.
        Higher values = more surprising / novel.
        """
        # Ensure both distributions have same keys
        all_keys = set(dist_p.keys()) | set(dist_q.keys())

        # Smooth with small epsilon to avoid log(0)
        epsilon = 1e-10

        divergence = 0.0

        for key in all_keys:
            p = dist_p.get(key, epsilon)
            q = dist_q.get(key, epsilon)

            # KL divergence formula
            if p > 0 and q > 0:
                divergence += p * math.log(p / q)

        return divergence

    def _extract_topic_distribution(self, text: str) -> Dict[str, float]:
        """
        Extract simple topic distribution from text.

        Args:
            text: Input text

        Returns:
            Topic probability distribution
        """
        words = text.lower().split()
        word_counts = defaultdict(int)

        for word in words:
            if len(word) > 3:  # Ignore short words
                word_counts[word] += 1

        # Convert to probabilities
        total = sum(word_counts.values())

        if total == 0:
            return {"unknown": 1.0}

        return {word: count / total for word, count in word_counts.items()}

    def should_consolidate(self) -> Tuple[bool, str]:
        """
        Check if consolidation should be triggered.

        Returns:
            (should_consolidate, reason) tuple
        """
        # Check time threshold
        hours_since = (datetime.now() - self.last_consolidation).total_seconds() / 3600
        if hours_since >= self.CONSOLIDATION_INTERVAL_HOURS:
            return True, f"Time threshold: {hours_since:.1f}h since last consolidation"

        # Check importance accumulator
        if self.importance_accumulator >= self.IMPORTANCE_THRESHOLD:
            return True, f"Importance threshold: {self.importance_accumancer:.1f} accumulated"

        return False, "Thresholds not met"

    def consolidate(self,
                   min_cluster_size: int = 3,
                   force: bool = False) -> Dict[str, Any]:
        """
        Perform consolidation from episodic to semantic memory.

        Args:
            min_cluster_size: Minimum similar memories to form pattern
            force: Force consolidation regardless of thresholds

        Returns:
            Consolidation results
        """
        should_trigger, reason = self.should_consolidate()

        if not should_trigger and not force:
            return {
                "triggered": False,
                "reason": reason,
            }

        # Get unconsolidated episodic memories
        unconsolidated = self._get_unconsolidated_memories()

        if len(unconsolidated) < min_cluster_size:
            return {
                "triggered": False,
                "reason": f"Insufficient unconsolidated memories: {len(unconsolidated)}",
            }

        # Cluster similar memories
        clusters = self._cluster_memories(unconsolidated)

        # Extract patterns from clusters
        patterns_created = 0
        memories_consolidated = 0

        for cluster in clusters:
            if len(cluster) >= min_cluster_size:
                # Extract pattern
                pattern = self._extract_pattern(cluster)

                # Store as semantic memory
                self.semantic.store_fact(
                    fact=pattern,
                    source_memory_ids=[m.id for m in cluster]
                )

                patterns_created += 1
                memories_consolidated += len(cluster)

                # Mark as consolidated
                for memory in cluster:
                    memory.consolidated = True

        # Reset accumulator
        self.importance_accumulator = 0.0
        self.last_consolidation = datetime.now()

        return {
            "triggered": True,
            "patterns_created": patterns_created,
            "memories_consolidated": memories_consolidated,
            "clusters_found": len(clusters),
        }

    def _get_unconsolidated_memories(self) -> List[Memory]:
        """Get unconsolidated episodic memories older than 24h"""
        cutoff = datetime.now() - timedelta(hours=24)

        return [
            m for m in self.episodic._memories.values()
            if not m.consolidated and m.timestamp < cutoff
        ]

    def _cluster_memories(self, memories: List[Memory]) -> List[List[Memory]]:
        """Cluster memories by content similarity"""
        if not memories:
            return []

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

                if similarity >= self.PATTERN_SIMILARITY_THRESHOLD:
                    cluster.append(mem2)
                    used.add(j)

            clusters.append(cluster)

        return clusters

    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate simple word-overlap similarity"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        if not words1 or not words2:
            return 0.0

        intersection = len(words1 & words2)
        union = len(words1 | words2)

        return intersection / union if union > 0 else 0.0

    def _extract_pattern(self, cluster: List[Memory]) -> str:
        """Extract common pattern from memory cluster"""
        # Find common words
        word_counts = defaultdict(int)

        for memory in cluster:
            words = set(w.lower() for w in memory.content.split() if len(w) > 3)
            for word in words:
                word_counts[word] += 1

        # Get most common words
        top_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:5]

        pattern_words = [word for word, _ in top_words]

        return f"Pattern: Experiences involving {', '.join(pattern_words)}"

    def get_consolidation_stats(self) -> Dict[str, Any]:
        """Get consolidation statistics"""
        total_episodic = len(self.episodic._memories)
        consolidated_count = sum(
            1 for m in self.episodic._memories.values()
            if m.consolidated
        )

        return {
            "importance_accumulator": self.importance_accumulator,
            "last_consolidation": self.last_consolidation.isoformat(),
            "hours_since_consolidation": (datetime.now() - self.last_consolidation).total_seconds() / 3600,
            "episodic_count": total_episodic,
            "consolidated_count": consolidated_count,
            "consolidation_ratio": consolidated_count / total_episodic if total_episodic > 0 else 0.0,
        }
