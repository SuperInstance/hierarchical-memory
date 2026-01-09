"""
Episodic Memory Module
Autobiographical memory for specific events and experiences.

Based on Tulving's episodic memory theory - memory for personal experiences
with temporal and spatial context.
"""

import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import numpy as np


@dataclass
class EpisodicEvent:
    """A single episodic memory event."""
    content: str
    timestamp: float = field(default_factory=time.time)
    emotional_valence: float = 0.0  # -1 (negative) to 1 (positive)
    importance: float = 0.5  # 0 to 1
    context: Dict[str, Any] = field(default_factory=dict)
    access_count: int = 0
    last_accessed: float = field(default_factory=time.time)

    def __post_init__(self):
        """Validate emotional valence and importance."""
        if not -1 <= self.emotional_valence <= 1:
            raise ValueError("Emotional valence must be between -1 and 1")
        if not 0 <= self.importance <= 1:
            raise ValueError("Importance must be between 0 and 1")


class EpisodicMemory:
    """
    Episodic memory for storing and retrieving personal experiences.

    Features:
    - Time-stamped events with emotional tagging
    - Importance scoring based on emotion, novelty, and significance
    - Contextual retrieval (time, emotion, context)
    - Decay based on importance and access frequency
    """

    def __init__(
        self,
        capacity: int = 1000,
        decay_rate: float = 0.1,
        emotion_boost: float = 0.2
    ):
        """
        Initialize episodic memory.

        Args:
            capacity: Maximum number of events (default: 1000)
            decay_rate: Rate at which importance decays (default: 0.1)
            emotion_boost: Boost for emotionally charged events (default: 0.2)
        """
        if capacity <= 0:
            raise ValueError("Capacity must be positive")
        if not 0 <= decay_rate <= 1:
            raise ValueError("Decay rate must be between 0 and 1")

        self.capacity = capacity
        self.decay_rate = decay_rate
        self.emotion_boost = emotion_boost
        self._events: List[EpisodicEvent] = []

    def add(
        self,
        content: str,
        emotional_valence: float = 0.0,
        importance: Optional[float] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Add an episodic event.

        Args:
            content: Description of the event
            emotional_valence: Emotional charge (-1 to 1)
            importance: Optional manual importance (0-1)
            context: Additional context (location, participants, etc.)

        Returns:
            Event ID (timestamp-based)
        """
        if not content:
            raise ValueError("Content cannot be empty")

        # Calculate importance if not provided
        if importance is None:
            importance = self._calculate_importance(emotional_valence, context)

        event = EpisodicEvent(
            content=content,
            emotional_valence=emotional_valence,
            importance=importance,
            context=context or {}
        )

        self._events.append(event)

        # Check capacity and evict if necessary
        if len(self._events) > self.capacity:
            self._evict()

        return str(event.timestamp)

    def get(self, event_id: str) -> Optional[EpisodicEvent]:
        """
        Retrieve an event by ID.

        Args:
            event_id: Timestamp-based event ID

        Returns:
            The event, or None if not found
        """
        try:
            timestamp = float(event_id)
            for event in self._events:
                if event.timestamp == timestamp:
                    event.access_count += 1
                    event.last_accessed = time.time()
                    return event
        except (ValueError, TypeError):
            pass
        return None

    def retrieve_by_time(
        self,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
        limit: int = 10
    ) -> List[EpisodicEvent]:
        """
        Retrieve events from a time range.

        Args:
            start_time: Start of time range (default: 24 hours ago)
            end_time: End of time range (default: now)
            limit: Maximum number of events to return

        Returns:
            List of events in chronological order
        """
        if start_time is None:
            start_time = time.time() - 86400  # 24 hours ago
        if end_time is None:
            end_time = time.time()

        events = [
            e for e in self._events
            if start_time <= e.timestamp <= end_time
        ]
        events.sort(key=lambda e: e.timestamp)

        return events[:limit]

    def retrieve_by_emotion(
        self,
        min_valence: float = -1.0,
        max_valence: float = 1.0,
        limit: int = 10
    ) -> List[EpisodicEvent]:
        """
        Retrieve events within emotional valence range.

        Args:
            min_valence: Minimum emotional valence
            max_valence: Maximum emotional valence
            limit: Maximum number of events to return

        Returns:
            List of events sorted by importance
        """
        events = [
            e for e in self._events
            if min_valence <= e.emotional_valence <= max_valence
        ]
        events.sort(key=lambda e: e.importance, reverse=True)

        return events[:limit]

    def retrieve_by_context(
        self,
        context_key: str,
        context_value: Any,
        limit: int = 10
    ) -> List[EpisodicEvent]:
        """
        Retrieve events by context.

        Args:
            context_key: Key in context dictionary
            context_value: Value to match
            limit: Maximum number of events to return

        Returns:
            List of matching events
        """
        events = [
            e for e in self._events
            if e.context.get(context_key) == context_value
        ]
        events.sort(key=lambda e: e.importance, reverse=True)

        return events[:limit]

    def search(
        self,
        query: str,
        limit: int = 10
    ) -> List[tuple[EpisodicEvent, float]]:
        """
        Simple keyword search across event contents.

        Args:
            query: Search query
            limit: Maximum number of results

        Returns:
            List of (event, relevance_score) tuples
        """
        query_lower = query.lower()
        results = []

        for event in self._events:
            content_lower = event.content.lower()

            # Simple relevance: count keyword matches
            if query_lower in content_lower:
                # Relevance = keyword frequency + importance
                matches = content_lower.count(query_lower)
                relevance = (matches * 0.5) + event.importance
                results.append((event, relevance))

        results.sort(key=lambda x: x[1], reverse=True)
        return results[:limit]

    def _calculate_importance(
        self,
        emotional_valence: float,
        context: Optional[Dict[str, Any]]
    ) -> float:
        """
        Calculate importance based on emotion and context.

        Args:
            emotional_valence: Emotional charge
            context: Event context

        Returns:
            Importance score (0-1)
        """
        # Base importance
        importance = 0.5

        # Boost for emotionally charged events
        emotion_magnitude = abs(emotional_valence)
        importance += emotion_magnitude * self.emotion_boost

        # Boost for events with rich context
        if context and len(context) > 0:
            importance += 0.1

        # Clamp to [0, 1]
        return max(0.0, min(1.0, importance))

    def _evict(self):
        """Evict least important events when at capacity."""
        if len(self._events) <= self.capacity:
            return

        # Sort by combined score: importance + access frequency - age penalty
        def score(event):
            age = time.time() - event.timestamp
            age_penalty = age / 86400  # 1 day = 0.1 penalty
            return event.importance + (event.access_count * 0.05) - age_penalty

        self._events.sort(key=score, reverse=True)
        del self._events[self.capacity:]

    def get_recent_events(self, limit: int = 10) -> List[EpisodicEvent]:
        """Get most recent events."""
        events = sorted(self._events, key=lambda e: e.timestamp, reverse=True)
        return events[:limit]

    def get_important_events(self, limit: int = 10) -> List[EpisodicEvent]:
        """Get most important events."""
        events = sorted(self._events, key=lambda e: e.importance, reverse=True)
        return events[:limit]

    def __len__(self) -> int:
        """Return number of stored events."""
        return len(self._events)

    def __repr__(self) -> str:
        """String representation of episodic memory."""
        return f"EpisodicMemory(events={len(self._events)}, capacity={self.capacity})"


def create_episodic_memory(
    capacity: int = 1000,
    decay_rate: float = 0.1,
    emotion_boost: float = 0.2
) -> EpisodicMemory:
    """
    Factory function to create an episodic memory instance.

    Args:
        capacity: Maximum number of events
        decay_rate: Rate at which importance decays
        emotion_boost: Boost for emotionally charged events

    Returns:
        Configured EpisodicMemory instance
    """
    return EpisodicMemory(
        capacity=capacity,
        decay_rate=decay_rate,
        emotion_boost=emotion_boost
    )
