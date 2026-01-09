"""
Memory Consolidation Pipeline
Transfers memories from short-term to long-term storage.

Based on systems consolidation theory - memories are gradually
transferred from hippocampus to neocortex during sleep/rest.
"""

import time
import numpy as np
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum

from ..core.working import WorkingMemory
from ..core.episodic import EpisodicMemory, EpisodicEvent
from ..core.semantic import SemanticMemory


class ConsolidationStatus(Enum):
    """Status of consolidation process."""
    PENDING = "pending"
    CONSOLIDATING = "consolidating"
    COMPLETE = "complete"
    FAILED = "failed"


@dataclass
class ConsolidationTask:
    """A consolidation task."""
    source_tier: str  # "working", "episodic"
    target_tier: str  # "episodic", "semantic"
    item_id: str
    priority: float
    status: ConsolidationStatus = ConsolidationStatus.PENDING
    timestamp: float = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()


class ConsolidationPipeline:
    """
    Memory consolidation pipeline.

    Features:
    - Priority-based consolidation (importance, emotional valence)
    - Surprise-based triggering (KL divergence)
    - Batch consolidation for efficiency
    - Sleep/rest-based consolidation cycles
    """

    def __init__(
        self,
        working_memory: WorkingMemory,
        episodic_memory: EpisodicMemory,
        semantic_memory: SemanticMemory,
        consolidation_threshold: float = 0.7,
        batch_size: int = 10
    ):
        """
        Initialize consolidation pipeline.

        Args:
            working_memory: Working memory instance
            episodic_memory: Episodic memory instance
            semantic_memory: Semantic memory instance
            consolidation_threshold: Importance threshold for consolidation
            batch_size: Number of items to consolidate per batch
        """
        self.working_memory = working_memory
        self.episodic_memory = episodic_memory
        self.semantic_memory = semantic_memory
        self.consolidation_threshold = consolidation_threshold
        self.batch_size = batch_size
        self._queue: List[ConsolidationTask] = []
        self._consolidation_count = 0

    def add_to_queue(
        self,
        source_tier: str,
        target_tier: str,
        item_id: str,
        priority: float
    ):
        """
        Add item to consolidation queue.

        Args:
            source_tier: Source memory tier
            target_tier: Target memory tier
            item_id: Item identifier
            priority: Consolidation priority (0-1)
        """
        task = ConsolidationTask(
            source_tier=source_tier,
            target_tier=target_tier,
            item_id=item_id,
            priority=priority
        )
        self._queue.append(task)

    def prioritize_queue(self):
        """Sort consolidation queue by priority."""
        self._queue.sort(key=lambda t: t.priority, reverse=True)

    def consolidate_next_batch(self) -> int:
        """
        Consolidate next batch of items.

        Returns:
            Number of items consolidated
        """
        self.prioritize_queue()

        batch = self._queue[:self.batch_size]
        consolidated = 0

        for task in batch:
            if task.priority >= self.consolidation_threshold:
                success = self._consolidate(task)
                if success:
                    task.status = ConsolidationStatus.COMPLETE
                    consolidated += 1
                else:
                    task.status = ConsolidationStatus.FAILED

        # Remove processed tasks
        self._queue = self._queue[consolidated:]
        self._consolidation_count += consolidated

        return consolidated

    def _consolidate(self, task: ConsolidationTask) -> bool:
        """
        Consolidate a single item.

        Args:
            task: Consolidation task

        Returns:
            True if consolidation succeeded
        """
        try:
            if task.source_tier == "working" and task.target_tier == "episodic":
                return self._consolidate_working_to_episodic(task)
            elif task.source_tier == "episodic" and task.target_tier == "semantic":
                return self._consolidate_episodic_to_semantic(task)
            else:
                return False
        except Exception:
            return False

    def _consolidate_working_to_episodic(self, task: ConsolidationTask) -> bool:
        """
        Consolidate from working memory to episodic memory.

        Args:
            task: Consolidation task

        Returns:
            True if consolidation succeeded
        """
        # Retrieve from working memory
        content = self.working_memory.get(task.item_id)
        if content is None:
            return False

        # Convert to episodic event
        # In production, would extract more context
        event_id = self.episodic_memory.add(
            content=str(content),
            importance=task.priority,
            context={"source": "working_memory"}
        )

        # Remove from working memory after consolidation
        self.working_memory.remove(task.item_id)

        return event_id is not None

    def _consolidate_episodic_to_semantic(self, task: ConsolidationTask) -> bool:
        """
        Consolidate from episodic to semantic memory.

        Args:
            task: Consolidation task

        Returns:
            True if consolidation succeeded
        """
        # Retrieve episodic event
        event = self.episodic_memory.get(task.item_id)
        if event is None:
            return False

        # Extract concept from event
        # In production, would use NLP to extract concepts
        concept_name = event.content.split()[0] if event.content else "unknown"

        # Add to semantic memory
        success = self.semantic_memory.add_concept(
            name=concept_name,
            attributes={
                "episodic_source": task.item_id,
                "importance": event.importance,
                "emotional_valence": event.emotional_valence
            }
        )

        return success

    def trigger_consolidation_by_surprise(
        self,
        current_state: np.ndarray,
        expected_state: np.ndarray
    ) -> float:
        """
        Trigger consolidation based on surprise (KL divergence).

        Args:
            current_state: Current observation
            expected_state: Expected observation

        Returns:
            Surprise score
        """
        # Calculate KL divergence (simplified)
        surprise = self._calculate_kl_divergence(current_state, expected_state)

        # If surprised, consolidate high-priority items
        if surprise > 0.5:
            # Add working memory items to queue
            for key in list(self.working_memory.items().keys())[:5]:
                self.add_to_queue("working", "episodic", key, surprise)

        return surprise

    def _calculate_kl_divergence(
        self,
        p: np.ndarray,
        q: np.ndarray
    ) -> float:
        """
        Calculate KL divergence between two distributions.

        Args:
            p: First distribution
            q: Second distribution

        Returns:
            KL divergence score
        """
        # Add small epsilon to avoid division by zero
        epsilon = 1e-10
        p = p + epsilon
        q = q + epsilon

        # Normalize
        p = p / np.sum(p)
        q = q / np.sum(q)

        # Calculate KL divergence
        kl = np.sum(p * np.log(p / q))

        return float(kl)

    def simulate_sleep_consolidation(self, duration_hours: float = 8.0) -> int:
        """
        Simulate sleep-based consolidation.

        During sleep, memories are replayed and consolidated.

        Args:
            duration_hours: Sleep duration in hours

        Returns:
            Number of items consolidated
        """
        # Sleep consolidates multiple batches
        batches = int(duration_hours * 2)  # 2 batches per hour
        total_consolidated = 0

        for _ in range(batches):
            # Auto-generate consolidation tasks from working memory
            for key, content in list(self.working_memory.items().items())[:3]:
                self.add_to_queue("working", "episodic", key, 0.8)

            # Consolidate batch
            consolidated = self.consolidate_next_batch()
            total_consolidated += consolidated

        return total_consolidated

    def get_queue_size(self) -> int:
        """Get current queue size."""
        return len(self._queue)

    def get_consolidation_stats(self) -> Dict[str, Any]:
        """
        Get consolidation statistics.

        Returns:
            Dictionary of statistics
        """
        status_counts = {status.value: 0 for status in ConsolidationStatus}
        for task in self._queue:
            status_counts[task.status.value] += 1

        return {
            "queue_size": len(self._queue),
            "total_consolidated": self._consolidation_count,
            "status_distribution": status_counts,
            "avg_priority": np.mean([t.priority for t in self._queue]) if self._queue else 0
        }

    def clear_queue(self):
        """Clear consolidation queue."""
        self._queue.clear()


def create_consolidation_pipeline(
    working_memory: WorkingMemory,
    episodic_memory: EpisodicMemory,
    semantic_memory: SemanticMemory,
    consolidation_threshold: float = 0.7,
    batch_size: int = 10
) -> ConsolidationPipeline:
    """
    Factory function to create a consolidation pipeline.

    Args:
        working_memory: Working memory instance
        episodic_memory: Episodic memory instance
        semantic_memory: Semantic memory instance
        consolidation_threshold: Importance threshold for consolidation
        batch_size: Number of items to consolidate per batch

    Returns:
        Configured ConsolidationPipeline instance
    """
    return ConsolidationPipeline(
        working_memory=working_memory,
        episodic_memory=episodic_memory,
        semantic_memory=semantic_memory,
        consolidation_threshold=consolidation_threshold,
        batch_size=batch_size
    )
