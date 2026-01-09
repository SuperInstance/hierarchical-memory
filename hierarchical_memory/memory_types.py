"""
Memory System Type Definitions
==============================

Core data structures for the hierarchical memory system.
"""

from typing import List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import hashlib


class MemoryType(Enum):
    """Hierarchical memory tiers (inspired by neuroscience)"""
    WORKING = "working"
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"


class MemoryImportance(Enum):
    """Importance scoring (affects consolidation priority)"""
    FORGOTTEN = 1.0
    ROUTINE = 3.0
    NOTABLE = 6.0
    SIGNIFICANT = 8.0
    CORE_IDENTITY = 10.0


@dataclass
class Memory:
    """Individual memory unit"""
    id: str
    content: str
    memory_type: MemoryType
    timestamp: datetime

    # Metadata
    importance: float = 5.0
    emotional_valence: float = 0.0  # -1 (bad) to +1 (good)
    participants: List[str] = field(default_factory=list)
    location: str = ""

    # Consolidation tracking
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    consolidated: bool = False
    consolidation_source_ids: List[str] = field(default_factory=list)

    # Relationships
    related_memory_ids: List[str] = field(default_factory=list)
    contradicts_memory_ids: List[str] = field(default_factory=list)

    # For temporal landmarks
    is_temporal_landmark: bool = False
    landmark_type: Optional[str] = None

    def to_dict(self):
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
        }

    @staticmethod
    def generate_id(content: str, timestamp: datetime) -> str:
        """Generate unique memory ID"""
        unique_str = f"{content}{timestamp.isoformat()}"
        return hashlib.md5(unique_str.encode()).hexdigest()[:16]
