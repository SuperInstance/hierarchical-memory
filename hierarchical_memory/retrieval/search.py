"""
Memory Retrieval System
Multi-modal search across all memory tiers.

Provides flexible search capabilities including semantic,
temporal, spatial, and contextual retrieval.
"""

import time
import numpy as np
from typing import List, Dict, Any, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum

from ..core.working import WorkingMemory
from ..core.episodic import EpisodicMemory, EpisodicEvent
from ..core.semantic import SemanticMemory, Concept
from ..core.procedural import ProceduralMemory, Skill


class RetrievalMode(Enum):
    """Memory retrieval modes."""
    SEMANTIC = "semantic"
    TEMPORAL = "temporal"
    SPATIAL = "spatial"
    CONTEXTUAL = "contextual"
    ASSOCIATIVE = "associative"
    HYBRID = "hybrid"


@dataclass
class RetrievalResult:
    """A memory retrieval result."""
    content: Any
    tier: str  # "working", "episodic", "semantic", "procedural"
    score: float
    metadata: Dict[str, Any]
    timestamp: Optional[float] = None


class MemoryRetrieval:
    """
    Multi-modal memory retrieval system.

    Features:
    - Semantic similarity search
    - Temporal range queries
    - Context-based retrieval
    - Associative search
    - Hybrid retrieval combining multiple modes
    - Tier-specific search
    """

    def __init__(
        self,
        working_memory: WorkingMemory,
        episodic_memory: EpisodicMemory,
        semantic_memory: SemanticMemory,
        procedural_memory: ProceduralMemory,
        default_top_k: int = 10
    ):
        """
        Initialize memory retrieval system.

        Args:
            working_memory: Working memory instance
            episodic_memory: Episodic memory instance
            semantic_memory: Semantic memory instance
            procedural_memory: Procedural memory instance
            default_top_k: Default number of results to return
        """
        self.working_memory = working_memory
        self.episodic_memory = episodic_memory
        self.semantic_memory = semantic_memory
        self.procedural_memory = procedural_memory
        self.default_top_k = default_top_k

    def search(
        self,
        query: Union[str, np.ndarray],
        mode: RetrievalMode = RetrievalMode.SEMANTIC,
        tier: Optional[str] = None,
        top_k: Optional[int] = None,
        **kwargs
    ) -> List[RetrievalResult]:
        """
        Search memories using specified mode.

        Args:
            query: Search query (text or embedding)
            mode: Retrieval mode
            tier: Memory tier to search (None = all tiers)
            top_k: Number of results
            **kwargs: Additional mode-specific parameters

        Returns:
            List of retrieval results sorted by score
        """
        if top_k is None:
            top_k = self.default_top_k

        results = []

        # Search specified tier or all tiers
        tiers = [tier] if tier else ["working", "episodic", "semantic", "procedural"]

        for tier_name in tiers:
            if tier_name == "working":
                results.extend(self._search_working(query, mode, top_k, **kwargs))
            elif tier_name == "episodic":
                results.extend(self._search_episodic(query, mode, top_k, **kwargs))
            elif tier_name == "semantic":
                results.extend(self._search_semantic(query, mode, top_k, **kwargs))
            elif tier_name == "procedural":
                results.extend(self._search_procedural(query, mode, top_k, **kwargs))

        # Sort by score
        results.sort(key=lambda r: r.score, reverse=True)

        return results[:top_k]

    def _search_working(
        self,
        query: Union[str, np.ndarray],
        mode: RetrievalMode,
        top_k: int,
        **kwargs
    ) -> List[RetrievalResult]:
        """Search working memory."""
        results = []

        if isinstance(query, str):
            # Keyword search
            for key, content in self.working_memory.items().items():
                if query.lower() in str(content).lower():
                    results.append(RetrievalResult(
                        content=content,
                        tier="working",
                        score=0.8,  # Simple relevance
                        metadata={"key": key}
                    ))

        return results

    def _search_episodic(
        self,
        query: Union[str, np.ndarray],
        mode: RetrievalMode,
        top_k: int,
        **kwargs
    ) -> List[RetrievalResult]:
        """Search episodic memory."""
        results = []

        if mode == RetrievalMode.TEMPORAL:
            # Time range search
            start_time = kwargs.get("start_time")
            end_time = kwargs.get("end_time")
            events = self.episodic_memory.retrieve_by_time(
                start_time=start_time,
                end_time=end_time,
                limit=top_k
            )
            for event in events:
                results.append(RetrievalResult(
                    content=event.content,
                    tier="episodic",
                    score=event.importance,
                    metadata={
                        "emotional_valence": event.emotional_valence,
                        "context": event.context
                    },
                    timestamp=event.timestamp
                ))

        elif mode == RetrievalMode.SEMANTIC and isinstance(query, str):
            # Keyword search
            search_results = self.episodic_memory.search(query, limit=top_k)
            for event, score in search_results:
                results.append(RetrievalResult(
                    content=event.content,
                    tier="episodic",
                    score=score,
                    metadata={
                        "emotional_valence": event.emotional_valence,
                        "context": event.context
                    },
                    timestamp=event.timestamp
                ))

        elif mode == RetrievalMode.CONTEXTUAL:
            # Context-based search
            context_key = kwargs.get("context_key")
            context_value = kwargs.get("context_value")
            if context_key and context_value:
                events = self.episodic_memory.retrieve_by_context(
                    context_key=context_key,
                    context_value=context_value,
                    limit=top_k
                )
                for event in events:
                    results.append(RetrievalResult(
                        content=event.content,
                        tier="episodic",
                        score=event.importance,
                        metadata={
                            "context": event.context,
                            "emotional_valence": event.emotional_valence
                        },
                        timestamp=event.timestamp
                    ))

        return results

    def _search_semantic(
        self,
        query: Union[str, np.ndarray],
        mode: RetrievalMode,
        top_k: int,
        **kwargs
    ) -> List[RetrievalResult]:
        """Search semantic memory."""
        results = []

        if mode == RetrievalMode.SEMANTIC and isinstance(query, np.ndarray):
            # Vector similarity search
            search_results = self.semantic_memory.similarity_search(
                query=query,
                top_k=top_k,
                threshold=kwargs.get("threshold", 0.7)
            )
            for concept_name, score in search_results:
                concept = self.semantic_memory.get_concept(concept_name)
                if concept:
                    results.append(RetrievalResult(
                        content=concept.name,
                        tier="semantic",
                        score=score,
                        metadata={
                            "attributes": concept.attributes,
                            "associations": list(concept.associations)
                        }
                    ))

        elif isinstance(query, str):
            # Keyword search
            search_results = self.semantic_memory.keyword_search(
                query=query,
                top_k=top_k
            )
            for concept_name, score in search_results:
                concept = self.semantic_memory.get_concept(concept_name)
                if concept:
                    results.append(RetrievalResult(
                        content=concept.name,
                        tier="semantic",
                        score=score,
                        metadata={
                            "attributes": concept.attributes,
                            "associations": list(concept.associations)
                        }
                    ))

        return results

    def _search_procedural(
        self,
        query: Union[str, np.ndarray],
        mode: RetrievalMode,
        top_k: int,
        **kwargs
    ) -> List[RetrievalResult]:
        """Search procedural memory."""
        results = []

        if isinstance(query, str):
            # Search skills by name or attributes
            for skill_name, skill in self.procedural_memory._skills.items():
                score = 0.0

                # Match in name
                if query.lower() in skill_name.lower():
                    score += 0.5

                # Match in attributes
                for key, value in skill.attributes.items():
                    if query.lower() in key.lower() or query.lower() in str(value).lower():
                        score += 0.3

                if score > 0:
                    results.append(RetrievalResult(
                        content=skill.name,
                        tier="procedural",
                        score=score + (skill.mastery_level * 0.1),
                        metadata={
                            "mastery_level": skill.mastery_level,
                            "practice_count": skill.practice_count,
                            "success_rate": skill.success_rate
                        }
                    ))

        results.sort(key=lambda r: r.score, reverse=True)
        return results[:top_k]

    def associative_search(
        self,
        seed_item: str,
        tier: str,
        max_depth: int = 2,
        top_k: int = 10
    ) -> List[RetrievalResult]:
        """
        Perform associative search starting from a seed item.

        Args:
            seed_item: Starting item identifier
            tier: Memory tier to search
            max_depth: Maximum association depth
            top_k: Maximum results

        Returns:
            List of associated items
        """
        results = []
        visited = set()
        queue = [(seed_item, 0)]

        while queue and len(results) < top_k:
            current_item, depth = queue.pop(0)

            if current_item in visited or depth > max_depth:
                continue

            visited.add(current_item)

            if tier == "semantic":
                concept = self.semantic_memory.get_concept(current_item)
                if concept:
                    results.append(RetrievalResult(
                        content=concept.name,
                        tier=tier,
                        score=1.0 - (depth * 0.2),
                        metadata={"depth": depth}
                    ))
                    # Add associations to queue
                    for assoc in concept.associations:
                        if assoc not in visited:
                            queue.append((assoc, depth + 1))

        results.sort(key=lambda r: r.score, reverse=True)
        return results[:top_k]

    def hybrid_search(
        self,
        query: str,
        weights: Optional[Dict[str, float]] = None,
        top_k: int = 10
    ) -> List[RetrievalResult]:
        """
        Perform hybrid search across multiple retrieval modes.

        Args:
            query: Search query
            weights: Weights for different modes
            top_k: Maximum results

        Returns:
            Combined and re-ranked results
        """
        if weights is None:
            weights = {
                "semantic": 0.4,
                "temporal": 0.2,
                "contextual": 0.2,
                "associative": 0.2
            }

        all_results = []

        # Search using different modes
        if weights.get("semantic", 0) > 0:
            results = self.search(query, RetrievalMode.SEMANTIC, top_k=top_k)
            for r in results:
                r.score *= weights["semantic"]
            all_results.extend(results)

        if weights.get("temporal", 0) > 0:
            results = self.search(
                query,
                RetrievalMode.TEMPORAL,
                top_k=top_k,
                start_time=time.time() - 86400  # Last 24 hours
            )
            for r in results:
                r.score *= weights["temporal"]
            all_results.extend(results)

        # Combine and re-rank
        # Deduplicate by content
        seen = {}
        for result in all_results:
            content_key = str(result.content)
            if content_key not in seen or result.score > seen[content_key].score:
                seen[content_key] = result

        combined = list(seen.values())
        combined.sort(key=lambda r: r.score, reverse=True)

        return combined[:top_k]


def create_memory_retrieval(
    working_memory: WorkingMemory,
    episodic_memory: EpisodicMemory,
    semantic_memory: SemanticMemory,
    procedural_memory: ProceduralMemory,
    default_top_k: int = 10
) -> MemoryRetrieval:
    """
    Factory function to create a memory retrieval system.

    Args:
        working_memory: Working memory instance
        episodic_memory: Episodic memory instance
        semantic_memory: Semantic memory instance
        procedural_memory: Procedural memory instance
        default_top_k: Default number of results to return

    Returns:
        Configured MemoryRetrieval instance
    """
    return MemoryRetrieval(
        working_memory=working_memory,
        episodic_memory=episodic_memory,
        semantic_memory=semantic_memory,
        procedural_memory=procedural_memory,
        default_top_k=default_top_k
    )
