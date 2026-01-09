"""
Episodic Memory Module
======================

Implements experience-based memory with:
- Timestamp storage
- Emotional tagging
- Importance scoring
- Spatial context (location)
- Social context (participants)
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from collections import defaultdict
import numpy as np

from .memory_types import Memory, MemoryType, MemoryImportance


class EpisodicMemory:
    """
    Episodic Memory: "What-where-when" experiences

    Neuroscience: Autobiographical events with spatial, temporal,
    and emotional context. Forms the basis for semantic knowledge.
    """

    def __init__(self):
        self._memories: Dict[str, Memory] = {}
        self._by_time: List[tuple[datetime, str]] = []  # For temporal queries
        self._by_location: Dict[str, List[str]] = defaultdict(list)
        self._by_participants: Dict[str, List[str]] = defaultdict(list)

    def store(self, content: str,
              importance: float = 5.0,
              emotional_valence: float = 0.0,
              participants: List[str] = None,
              location: str = "",
              timestamp: Optional[datetime] = None) -> Memory:
        """
        Store a new episodic memory.

        Args:
            content: What happened
            importance: How important (1-10)
            emotional_valence: Emotional charge (-1 to +1)
            participants: Who was involved
            location: Where it happened
            timestamp: When it happened (default: now)

        Returns:
            Created memory object
        """
        if timestamp is None:
            timestamp = datetime.now()

        memory = Memory(
            id=Memory.generate_id(content, timestamp),
            content=content,
            memory_type=MemoryType.EPISODIC,
            timestamp=timestamp,
            importance=importance,
            emotional_valence=emotional_valence,
            participants=participants or [],
            location=location
        )

        self._memories[memory.id] = memory
        self._by_time.append((timestamp, memory.id))

        # Index by location
        if location:
            self._by_location[location].append(memory.id)

        # Index by participants
        for participant in (participants or []):
            self._by_participants[participant].append(memory.id)

        return memory

    def retrieve(self, memory_id: str) -> Optional[Memory]:
        """
        Retrieve memory by ID.

        Args:
            memory_id: Memory identifier

        Returns:
            Memory object or None
        """
        memory = self._memories.get(memory_id)

        if memory:
            memory.access_count += 1
            memory.last_accessed = datetime.now()

        return memory

    def search_by_time(self,
                      start_time: Optional[datetime] = None,
                      end_time: Optional[datetime] = None,
                      limit: int = 10) -> List[Memory]:
        """
        Retrieve memories within time range.

        Args:
            start_time: Start of time range
            end_time: End of time range
            limit: Maximum results

        Returns:
            List of memories in time range
        """
        results = []

        for timestamp, memory_id in sorted(self._by_time, reverse=True):
            if start_time and timestamp < start_time:
                continue
            if end_time and timestamp > end_time:
                continue

            memory = self._memories[memory_id]
            results.append(memory)

            if len(results) >= limit:
                break

        return results

    def search_by_location(self, location: str,
                          radius_km: float = 0.0,
                          limit: int = 10) -> List[Memory]:
        """
        Retrieve memories at or near a location.

        Args:
            location: Location name
            radius_km: Search radius (not implemented for text locations)
            limit: Maximum results

        Returns:
            List of memories at location
        """
        memory_ids = self._by_location.get(location, [])
        results = [self._memories[mid] for mid in memory_ids[:limit]]

        # Sort by importance
        results.sort(key=lambda m: m.importance, reverse=True)

        return results

    def search_by_participants(self, participants: List[str],
                              limit: int = 10) -> List[Memory]:
        """
        Retrieve memories involving specific participants.

        Args:
            participants: List of participant names
            limit: Maximum results

        Returns:
            List of memories with participants
        """
        memory_id_counts = defaultdict(int)

        for participant in participants:
            for memory_id in self._by_participants.get(participant, []):
                memory_id_counts[memory_id] += 1

        # Sort by number of matching participants
        sorted_ids = sorted(
            memory_id_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]

        return [self._memories[mid] for mid, _ in sorted_ids]

    def search_by_emotion(self,
                         min_valence: float = -1.0,
                         max_valence: float = 1.0,
                         limit: int = 10) -> List[Memory]:
        """
        Retrieve memories within emotional range.

        Args:
            min_valence: Minimum emotional valence
            max_valence: Maximum emotional valence
            limit: Maximum results

        Returns:
            List of memories with emotions in range
        """
        results = [
            m for m in self._memories.values()
            if min_valence <= m.emotional_valence <= max_valence
        ]

        # Sort by emotional intensity (absolute valence)
        results.sort(key=lambda m: abs(m.emotional_valence), reverse=True)

        return results[:limit]

    def search_by_importance(self,
                            min_importance: float = 0.0,
                            limit: int = 10) -> List[Memory]:
        """
        Retrieve memories above importance threshold.

        Args:
            min_importance: Minimum importance score
            limit: Maximum results

        Returns:
            List of memories above threshold
        """
        results = [
            m for m in self._memories.values()
            if m.importance >= min_importance
        ]

        results.sort(key=lambda m: m.importance, reverse=True)

        return results[:limit]

    def get_recent(self, hours: int = 24, limit: int = 10) -> List[Memory]:
        """
        Get recent memories.

        Args:
            hours: Hours back to search
            limit: Maximum results

        Returns:
            List of recent memories
        """
        cutoff = datetime.now() - timedelta(hours=hours)

        return self.search_by_time(start_time=cutoff, limit=limit)

    def get_emotional_summary(self) -> Dict[str, Any]:
        """
        Get summary of emotional content in episodic memory.

        Returns:
            Emotional statistics
        """
        if not self._memories:
            return {
                "total_memories": 0,
                "average_valence": 0.0,
                "positive_count": 0,
                "negative_count": 0,
                "neutral_count": 0,
            }

        valences = [m.emotional_valence for m in self._memories.values()]

        positive = sum(1 for v in valences if v > 0.3)
        negative = sum(1 for v in valences if v < -0.3)
        neutral = len(valences) - positive - negative

        return {
            "total_memories": len(self._memories),
            "average_valence": np.mean(valences),
            "positive_count": positive,
            "negative_count": negative,
            "neutral_count": neutral,
            "most_positive": max(self._memories.values(), key=lambda m: m.emotional_valence).content if valences else None,
            "most_negative": min(self._memories.values(), key=lambda m: m.emotional_valence).content if valences else None,
        }

    def get_location_history(self) -> Dict[str, int]:
        """
        Get frequency of memories by location.

        Returns:
            Location counts
        """
        counts = defaultdict(int)

        for memory in self._memories.values():
            if memory.location:
                counts[memory.location] += 1

        return dict(sorted(counts.items(), key=lambda x: x[1], reverse=True))

    def get_participant_network(self) -> Dict[str, Dict[str, int]]:
        """
        Get social network from co-participation in memories.

        Returns:
            Adjacency dict of co-occurrence counts
        """
        network = defaultdict(lambda: defaultdict(int))

        for memory in self._memories.values():
            participants = memory.participants

            # Count co-occurrences
            for i, p1 in enumerate(participants):
                for p2 in participants[i+1:]:
                    network[p1][p2] += 1
                    network[p2][p1] += 1

        # Convert to regular dict
        return {k: dict(v) for k, v in network.items()}

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get episodic memory statistics.

        Returns:
            Statistics dictionary
        """
        emotional_summary = self.get_emotional_summary()

        return {
            "total_memories": len(self._memories),
            "unique_locations": len(self._by_location),
            "unique_participants": len(self._by_participants),
            **emotional_summary,
        }

    def __len__(self) -> int:
        """Return number of episodic memories"""
        return len(self._memories)
