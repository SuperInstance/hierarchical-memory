"""
Hierarchical Memory System
A comprehensive four-tier memory architecture for AI agents.

This package implements a human-like memory system with:
- Working Memory: Short-term, capacity-limited storage
- Episodic Memory: Autobiographical events and experiences
- Semantic Memory: General knowledge and concepts
- Procedural Memory: Skills and know-how

Plus supporting systems for:
- Memory Consolidation: Transfer between memory tiers
- Memory Retrieval: Multi-modal search across all tiers
- Memory Sharing: Pack-based sharing between agents
- Forgetting: Biologically-inspired decay curves

Example usage:
    >>> from hierarchical_memory import HierarchicalMemory
    >>> memory = HierarchicalMemory()
    >>> memory.working.add("task1", "Complete the project report", importance=0.8)
    >>> memory.episodic.add("Discussed project timeline with team", emotional_valence=0.5)
    >>> memory.semantic.add_concept("project", attributes={"type": "work", "priority": "high"})
    >>> memory.procedural.add_skill("report writing", attributes={"difficulty": "medium"})
"""

from .core.working import WorkingMemory, create_working_memory
from .core.episodic import EpisodicMemory, EpisodicEvent, create_episodic_memory
from .core.semantic import SemanticMemory, Concept, create_semantic_memory
from .core.procedural import (
    ProceduralMemory,
    Skill,
    MasteryLevel,
    create_procedural_memory
)
from .consolidation.pipeline import (
    ConsolidationPipeline,
    ConsolidationStatus,
    create_consolidation_pipeline
)
from .retrieval.search import (
    MemoryRetrieval,
    RetrievalMode,
    RetrievalResult,
    create_memory_retrieval
)
from .sharing.protocol import (
    MemorySharing,
    AgentPack,
    SharedMemory,
    SharingStrategy,
    create_memory_sharing
)


class HierarchicalMemory:
    """
    Main interface for the hierarchical memory system.

    Integrates all memory tiers and supporting systems into a unified API.
    """

    def __init__(
        self,
        working_capacity: int = 20,
        episodic_capacity: int = 1000,
        semantic_embedding_dim: int = 384,
        practice_threshold: int = 10,
        consolidation_threshold: float = 0.7,
        retrieval_top_k: int = 10
    ):
        """
        Initialize hierarchical memory system.

        Args:
            working_capacity: Working memory capacity
            episodic_capacity: Episodic memory capacity
            semantic_embedding_dim: Semantic memory embedding dimension
            practice_threshold: Practices needed for skill mastery
            consolidation_threshold: Importance threshold for consolidation
            retrieval_top_k: Default number of retrieval results
        """
        # Initialize memory tiers
        self.working = create_working_memory(capacity=working_capacity)
        self.episodic = create_episodic_memory(capacity=episodic_capacity)
        self.semantic = create_semantic_memory(embedding_dim=semantic_embedding_dim)
        self.procedural = create_procedural_memory(practice_threshold=practice_threshold)

        # Initialize supporting systems
        self.consolidation = create_consolidation_pipeline(
            working_memory=self.working,
            episodic_memory=self.episodic,
            semantic_memory=self.semantic,
            consolidation_threshold=consolidation_threshold
        )

        self.retrieval = create_memory_retrieval(
            working_memory=self.working,
            episodic_memory=self.episodic,
            semantic_memory=self.semantic,
            procedural_memory=self.procedural,
            default_top_k=retrieval_top_k
        )

        self.sharing = None  # Initialized separately with pack configuration

    def initialize_sharing(
        self,
        pack_id: str,
        members: list,
        strategy: str = "trust_based",
        trust_threshold: float = 0.5
    ):
        """
        Initialize memory sharing with a pack configuration.

        Args:
            pack_id: Unique pack identifier
            members: List of agent IDs in pack
            strategy: Sharing strategy name
            trust_threshold: Minimum trust for sharing
        """
        strategy_enum = {
            "broadcast": SharingStrategy.BROADCAST,
            "selective": SharingStrategy.SELECTIVE,
            "query_based": SharingStrategy.QUERY_BASED,
            "trust_based": SharingStrategy.TRUST_BASED
        }.get(strategy, SharingStrategy.TRUST_BASED)

        self.sharing = create_memory_sharing(
            pack_id=pack_id,
            members=members,
            default_strategy=strategy_enum,
            trust_threshold=trust_threshold
        )

    def consolidate(self, batch_size: int = 10) -> int:
        """
        Run consolidation pipeline.

        Args:
            batch_size: Number of items to consolidate

        Returns:
            Number of items consolidated
        """
        return self.consolidation.consolidate_next_batch()

    def search(
        self,
        query: str,
        mode: str = "semantic",
        tier: str = None,
        top_k: int = None
    ) -> list:
        """
        Search across memory tiers.

        Args:
            query: Search query
            mode: Retrieval mode (semantic, temporal, contextual, hybrid)
            tier: Memory tier to search (None = all)
            top_k: Number of results

        Returns:
            List of retrieval results
        """
        retrieval_mode = {
            "semantic": RetrievalMode.SEMANTIC,
            "temporal": RetrievalMode.TEMPORAL,
            "contextual": RetrievalMode.CONTEXTUAL,
            "associative": RetrievalMode.ASSOCIATIVE,
            "hybrid": RetrievalMode.HYBRID
        }.get(mode, RetrievalMode.SEMANTIC)

        return self.retrieval.search(query, retrieval_mode, tier, top_k)

    def get_stats(self) -> dict:
        """
        Get comprehensive memory system statistics.

        Returns:
            Dictionary of statistics
        """
        return {
            "working": {
                "items": len(self.working),
                "capacity": self.working.capacity
            },
            "episodic": {
                "events": len(self.episodic),
                "capacity": self.episodic.capacity
            },
            "semantic": {
                "concepts": len(self.semantic),
                "embedding_dim": self.semantic.embedding_dim
            },
            "procedural": self.procedural.get_stats(),
            "consolidation": self.consolidation.get_consolidation_stats(),
            "sharing": self.sharing.get_sharing_stats() if self.sharing else None
        }

    def __repr__(self) -> str:
        """String representation."""
        parts = [
            f"working={len(self.working)}",
            f"episodic={len(self.episodic)}",
            f"semantic={len(self.semantic)}",
            f"procedural={len(self.procedural)}"
        ]
        return f"HierarchicalMemory({', '.join(parts)})"


__version__ = "1.0.0"
__author__ = "LucidDreamer Team"

__all__ = [
    # Main interface
    "HierarchicalMemory",

    # Memory tiers
    "WorkingMemory",
    "EpisodicMemory",
    "SemanticMemory",
    "ProceduralMemory",

    # Data structures
    "MemoryItem",
    "EpisodicEvent",
    "Concept",
    "Skill",
    "MasteryLevel",

    # Consolidation
    "ConsolidationPipeline",
    "ConsolidationStatus",

    # Retrieval
    "MemoryRetrieval",
    "RetrievalMode",
    "RetrievalResult",

    # Sharing
    "MemorySharing",
    "AgentPack",
    "SharedMemory",
    "SharingStrategy",

    # Factory functions
    "create_working_memory",
    "create_episodic_memory",
    "create_semantic_memory",
    "create_procedural_memory",
    "create_consolidation_pipeline",
    "create_memory_retrieval",
    "create_memory_sharing",
]
