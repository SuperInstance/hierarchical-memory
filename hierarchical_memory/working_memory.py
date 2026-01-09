"""
Working Memory Module
====================

Implements short-term working memory with:
- Limited capacity (20 items)
- Temporal decay (30 minutes)
- Priority-based eviction
- Fast access and manipulation
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from collections import OrderedDict
import heapq

from .memory_types import Memory, MemoryType


class WorkingMemory:
    """
    Working Memory: Current cognitive workspace (20 items, 30-min decay)

    Neuroscience: Maintains ~7±2 items (extended to 20 for AI utility)
    Decay: Items fade after 30 minutes unless reinforced
    """

    def __init__(self, capacity: int = 20, decay_minutes: int = 30):
        self.capacity = capacity
        self.decay_duration = timedelta(minutes=decay_minutes)

        # Memory storage with access tracking
        self._memories: OrderedDict[str, Memory] = OrderedDict()
        self._access_count: Dict[str, int] = {}

    def add(self, content: str, importance: float = 5.0,
            emotional_valence: float = 0.0, **kwargs) -> Memory:
        """
        Add item to working memory, evicting lowest priority if full.

        Args:
            content: Memory content
            importance: Priority score (1-10)
            emotional_valence: Emotional charge (-1 to +1)

        Returns:
            Created memory object
        """
        # Check capacity and evict if necessary
        if len(self._memories) >= self.capacity:
            self._evict_lowest_priority()

        # Create memory
        memory = Memory(
            id=Memory.generate_id(content, datetime.now()),
            content=content,
            memory_type=MemoryType.WORKING,
            timestamp=datetime.now(),
            importance=importance,
            emotional_valence=emotional_valence,
            **kwargs
        )

        # Add to working memory
        self._memories[memory.id] = memory
        self._access_count[memory.id] = 1

        return memory

    def get(self, memory_id: str) -> Optional[Memory]:
        """
        Retrieve memory by ID, updating access count.

        Args:
            memory_id: Memory identifier

        Returns:
            Memory object or None if not found/expired
        """
        memory = self._memories.get(memory_id)

        if memory is None:
            return None

        # Check if decayed
        if self._is_decayed(memory):
            self.remove(memory_id)
            return None

        # Update access count
        self._access_count[memory_id] += 1
        memory.access_count += 1
        memory.last_accessed = datetime.now()

        # Move to end (most recently used)
        self._memories.move_to_end(memory_id)

        return memory

    def get_all(self, decayed: bool = False) -> List[Memory]:
        """
        Get all memories, optionally filtering out decayed ones.

        Args:
            decayed: Include decayed memories

        Returns:
            List of memory objects
        """
        memories = list(self._memories.values())

        if not decayed:
            memories = [m for m in memories if not self._is_decayed(m)]

        return memories

    def remove(self, memory_id: str) -> bool:
        """
        Remove memory from working memory.

        Args:
            memory_id: Memory identifier

        Returns:
            True if removed, False if not found
        """
        if memory_id in self._memories:
            del self._memories[memory_id]
            del self._access_count[memory_id]
            return True
        return False

    def update(self, memory_id: str, **updates) -> Optional[Memory]:
        """
        Update memory attributes.

        Args:
            memory_id: Memory identifier
            **updates: Attributes to update (content, importance, etc.)

        Returns:
            Updated memory or None if not found
        """
        memory = self.get(memory_id)

        if memory is None:
            return None

        for key, value in updates.items():
            if hasattr(memory, key):
                setattr(memory, key, value)

        return memory

    def clear(self):
        """Clear all memories from working memory"""
        self._memories.clear()
        self._access_count.clear()

    def cleanup_decayed(self) -> int:
        """
        Remove all decayed memories.

        Returns:
            Number of memories removed
        """
        decayed_ids = [
            mid for mid, mem in self._memories.items()
            if self._is_decayed(mem)
        ]

        for memory_id in decayed_ids:
            self.remove(memory_id)

        return len(decayed_ids)

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get working memory statistics.

        Returns:
            Statistics dictionary
        """
        memories = self.get_all()

        return {
            "total_items": len(self._memories),
            "active_items": len(memories),
            "decayed_items": len(self._memories) - len(memories),
            "capacity_utilization": len(self._memories) / self.capacity,
            "average_importance": sum(m.importance for m in memories) / len(memories) if memories else 0.0,
            "total_accesses": sum(self._access_count.values()),
        }

    def _evict_lowest_priority(self):
        """
        Evict lowest priority memory based on:
        1. Decay status (evict decayed first)
        2. Importance score
        3. Access count
        """
        if not self._memories:
            return

        # Priority: (is_decayed, -importance, -access_count)
        # Lower tuple = higher eviction priority
        priorities = []
        for memory_id, memory in self._memories.items():
            is_decayed = self._is_decayed(memory)
            priority = (
                int(not is_decayed),  # Evict decayed first (0 < 1)
                -memory.importance,    # Lower importance = evict first
                -self._access_count[memory_id]  # Lower access = evict first
            )
            priorities.append((priority, memory_id))

        # Sort by priority and remove lowest
        priorities.sort()
        _, to_remove = priorities[0]
        self.remove(to_remove)

    def _is_decayed(self, memory: Memory) -> bool:
        """
        Check if memory has decayed.

        Args:
            memory: Memory object

        Returns:
            True if decayed
        """
        age = datetime.now() - memory.timestamp
        return age > self.decay_duration

    def __len__(self) -> int:
        """Return number of memories in working memory"""
        return len(self._memories)

    def __contains__(self, memory_id: str) -> bool:
        """Check if memory ID exists in working memory"""
        return memory_id in self._memories
