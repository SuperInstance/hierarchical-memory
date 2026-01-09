"""
Working Memory Module
Capacity-limited short-term memory with priority-based eviction.

Based on cognitive science research showing working memory capacity of 7±2 items
(Miller, 1956) and later refined to 4±1 items (Cowan, 2001).
"""

import time
from typing import List, Dict, Any, Optional
from collections import OrderedDict
from dataclasses import dataclass, field


@dataclass
class MemoryItem:
    """A single item in working memory."""
    content: Any
    importance: float = 0.5
    timestamp: float = field(default_factory=time.time)
    access_count: int = 0

    def __post_init__(self):
        """Validate importance score."""
        if not 0 <= self.importance <= 1:
            raise ValueError("Importance must be between 0 and 1")


class WorkingMemory:
    """
    Working memory with limited capacity and priority-based eviction.

    Features:
    - Default capacity: 20 items (configurable)
    - Time-based decay: 30 minutes half-life
    - Priority-based eviction (LRU + importance)
    - Importance boosting for frequently accessed items
    """

    def __init__(
        self,
        capacity: int = 20,
        decay_half_life: float = 1800.0,  # 30 minutes in seconds
        importance_threshold: float = 0.3
    ):
        """
        Initialize working memory.

        Args:
            capacity: Maximum number of items (default: 20)
            decay_half_life: Time in seconds for importance to halve (default: 1800)
            importance_threshold: Minimum importance to prevent eviction (default: 0.3)
        """
        if capacity <= 0:
            raise ValueError("Capacity must be positive")
        if decay_half_life <= 0:
            raise ValueError("Decay half-life must be positive")

        self.capacity = capacity
        self.decay_half_life = decay_half_life
        self.importance_threshold = importance_threshold
        self._items: OrderedDict[str, MemoryItem] = OrderedDict()

    def add(self, key: str, content: Any, importance: float = 0.5) -> bool:
        """
        Add an item to working memory.

        Args:
            key: Unique identifier for the item
            content: The content to store
            importance: Initial importance score (0-1)

        Returns:
            True if added successfully, False if evicted
        """
        if not key:
            raise ValueError("Key cannot be empty")

        # If key exists, update and move to end (most recently used)
        if key in self._items:
            self._items[key].content = content
            self._items[key].importance = importance
            self._items[key].timestamp = time.time()
            self._items.move_to_end(key)
            return True

        # Check capacity and evict if necessary
        if len(self._items) >= self.capacity:
            evicted = self._evict()
            if not evicted:
                return False

        # Add new item
        self._items[key] = MemoryItem(content=content, importance=importance)
        return True

    def get(self, key: str, boost: float = 0.05) -> Optional[Any]:
        """
        Retrieve an item and boost its importance.

        Args:
            key: Identifier for the item
            boost: Amount to boost importance (default: 0.05)

        Returns:
            The item content, or None if not found
        """
        if key not in self._items:
            return None

        item = self._items[key]
        item.access_count += 1
        item.importance = min(1.0, item.importance + boost)
        item.timestamp = time.time()
        self._items.move_to_end(key)  # Mark as recently used

        return item.content

    def remove(self, key: str) -> bool:
        """Remove an item from working memory."""
        if key in self._items:
            del self._items[key]
            return True
        return False

    def _evict(self) -> bool:
        """
        Evict least important item using LRU + importance scoring.

        Returns:
            True if eviction succeeded
        """
        if not self._items:
            return False

        # Apply decay to all items
        self._decay()

        # Find least important item
        # Priority = importance (recently accessed items boosted via get())
        min_key = next(iter(self._items))
        min_score = self._calculate_priority(min_key)

        for key in list(self._items.keys())[1:]:
            score = self._calculate_priority(key)
            if score < min_score:
                min_key = key
                min_score = score

        # Don't evict if above threshold
        if min_score >= self.importance_threshold:
            return False

        del self._items[min_key]
        return True

    def _calculate_priority(self, key: str) -> float:
        """Calculate priority score for eviction."""
        item = self._items[key]

        # Time decay: importance decreases with age
        age = time.time() - item.timestamp
        decay_factor = 0.5 ** (age / self.decay_half_life)

        # Priority = decayed importance
        return item.importance * decay_factor

    def _decay(self):
        """Apply time-based decay to all items."""
        current_time = time.time()
        for key, item in self._items.items():
            age = current_time - item.timestamp
            decay_factor = 0.5 ** (age / self.decay_half_life)
            item.importance *= decay_factor
            item.timestamp = current_time

    def clear(self):
        """Clear all items from working memory."""
        self._items.clear()

    def items(self) -> Dict[str, Any]:
        """Get all items as a dictionary."""
        return {k: v.content for k, v in self._items.items()}

    def __len__(self) -> int:
        """Return current number of items."""
        return len(self._items)

    def __contains__(self, key: str) -> bool:
        """Check if key exists in working memory."""
        return key in self._items

    def __repr__(self) -> str:
        """String representation of working memory."""
        return f"WorkingMemory(capacity={self.capacity}, items={len(self._items)})"


def create_working_memory(
    capacity: int = 20,
    decay_half_life: float = 1800.0,
    importance_threshold: float = 0.3
) -> WorkingMemory:
    """
    Factory function to create a working memory instance.

    Args:
        capacity: Maximum number of items
        decay_half_life: Time in seconds for importance to halve
        importance_threshold: Minimum importance to prevent eviction

    Returns:
        Configured WorkingMemory instance
    """
    return WorkingMemory(
        capacity=capacity,
        decay_half_life=decay_half_life,
        importance_threshold=importance_threshold
    )
