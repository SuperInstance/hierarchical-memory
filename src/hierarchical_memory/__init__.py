"""
Hierarchical Memory System
==========================

A 6-tier memory architecture inspired by cognitive neuroscience:
- Working Memory: Current attention/context
- Mid-Term Memory: Session buffer (1-6 hours)
- Long-Term Memory: Consolidated storage (1+ weeks)
- Episodic Memory: Specific events ("what-where-when")
- Semantic Memory: Consolidated patterns & facts
- Procedural Memory: Skills & learned behaviors

Features:
- Memory importance scoring
- Temporal landmark detection
- Episodic to semantic consolidation
- Vector-based semantic search (Qdrant integration optional)
- Autobiographical narrative generation
- Identity persistence tracking

Basic Usage:
-------------
>>> from hierarchical_memory import HierarchicalMemory
>>>
>>> # Initialize
>>> memory = HierarchicalMemory(character_id="agent_001")
>>>
>>> # Store memories
>>> memory.store("Met with the team to discuss project goals",
...             importance=7.0,
...             emotional_valence=0.5)
>>>
>>> # Retrieve relevant memories
>>> relevant = memory.retrieve("team meeting", top_k=5)
>>>
>>> # Trigger consolidation
>>> memory.consolidate()
"""

from hierarchical_memory.core import (
    HierarchicalMemory,
    Memory,
    MemoryType,
    MemoryImportance,
)
from hierarchical_memory.consolidation import (
    ConsolidationEngine,
    ConsolidationStrategy,
    ClusterBasedConsolidation,
    AdaptiveConsolidation,
    IncrementalConsolidation,
)
from hierarchical_memory.vector_store import (
    VectorMemoryStore,
    MemoryVector,
    EmbeddingModel,
)
from hierarchical_memory.identity import (
    IdentityPersistence,
    IdentityDriftTracker,
)

__version__ = "0.1.0"
__all__ = [
    # Core
    "HierarchicalMemory",
    "Memory",
    "MemoryType",
    "MemoryImportance",
    # Consolidation
    "ConsolidationEngine",
    "ConsolidationStrategy",
    "ClusterBasedConsolidation",
    "AdaptiveConsolidation",
    "IncrementalConsolidation",
    # Vector Store
    "VectorMemoryStore",
    "MemoryVector",
    "EmbeddingModel",
    # Identity
    "IdentityPersistence",
    "IdentityDriftTracker",
]

__author__ = "Extracted from DMLog"
__license__ = "MIT"
