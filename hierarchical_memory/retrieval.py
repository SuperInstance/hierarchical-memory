"""
Memory Retrieval Module
=======================

Implements flexible search across memory systems:
- 6 search modes (temporal, semantic, spatial, emotional, importance, associative)
- Relevance ranking
- Cross-system search
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
import numpy as np

from .memory_types import Memory, MemoryType
from .working_memory import WorkingMemory
from .episodic_memory import EpisodicMemory
from .semantic_memory import SemanticMemory
from .procedural_memory import ProceduralMemory


class SearchMode(Enum):
    """Memory search modes"""
    TEMPORAL = "temporal"  # Time-based retrieval
    SEMANTIC = "semantic"  # Concept-based retrieval
    SPATIAL = "spatial"    # Location-based retrieval
    EMOTIONAL = "emotional"  # Emotion-based retrieval
    IMPORTANCE = "importance"  # Importance-based retrieval
    ASSOCIATIVE = "associative"  # Association-based retrieval


class RetrievalSystem:
    """
    Unified Retrieval System across all memory types

    Neuroscience: Human memory retrieval uses multiple cues simultaneously.
    This system combines temporal, semantic, spatial, emotional, and
    importance signals for relevance ranking.
    """

    def __init__(self,
                 working: WorkingMemory,
                 episodic: EpisodicMemory,
                 semantic: SemanticMemory,
                 procedural: ProceduralMemory):
        self.working = working
        self.episodic = episodic
        self.semantic = semantic
        self.procedural = procedural

        # Retrieval parameters
        self.RECENCY_DECAY_RATE = 0.995  # Per hour
        self.DEFAULT_TOP_K = 10

    def search(self,
              query: str = "",
              mode: SearchMode = SearchMode.SEMANTIC,
              memory_types: List[MemoryType] = None,
              top_k: int = 10,
              **filters) -> List[Tuple[Memory, float]]:
        """
        Unified search across memory systems.

        Args:
            query: Search query
            mode: Search mode (temporal, semantic, etc.)
            memory_types: Which memory types to search (all if None)
            top_k: Maximum results
            **filters: Mode-specific filters

        Returns:
            List of (memory, relevance_score) tuples
        """
        # Default to all memory types
        if memory_types is None:
            memory_types = [
                MemoryType.WORKING,
                MemoryType.EPISODIC,
                MemoryType.SEMANTIC,
                MemoryType.PROCEDURAL,
            ]

        # Route to appropriate search method
        search_results = []

        if MemoryType.WORKING in memory_types:
            results = self._search_working(query, mode, **filters)
            search_results.extend(results)

        if MemoryType.EPISODIC in memory_types:
            results = self._search_episodic(query, mode, **filters)
            search_results.extend(results)

        if MemoryType.SEMANTIC in memory_types:
            results = self._search_semantic(query, mode, **filters)
            search_results.extend(results)

        if MemoryType.PROCEDURAL in memory_types:
            results = self._search_procedural(query, mode, **filters)
            search_results.extend(results)

        # Rank by combined relevance score
        ranked = self._rank_results(search_results, query)

        return ranked[:top_k]

    def _search_working(self, query: str, mode: SearchMode,
                       **filters) -> List[Tuple[Memory, float]]:
        """Search working memory"""
        memories = self.working.get_all()

        results = []
        for memory in memories:
            score = self._calculate_relevance(memory, query, mode, **filters)
            results.append((memory, score))

        return results

    def _search_episodic(self, query: str, mode: SearchMode,
                        **filters) -> List[Tuple[Memory, float]]:
        """Search episodic memory"""
        memories = []

        # Mode-specific filtering
        if mode == SearchMode.TEMPORAL:
            start_time = filters.get("start_time")
            end_time = filters.get("end_time")
            memories = self.episodic.search_by_time(start_time, end_time, limit=1000)

        elif mode == SearchMode.SPATIAL:
            location = filters.get("location", "")
            memories = self.episodic.search_by_location(location, limit=1000)

        elif mode == SearchMode.EMOTIONAL:
            min_valence = filters.get("min_valence", -1.0)
            max_valence = filters.get("max_valence", 1.0)
            memories = self.episodic.search_by_emotion(min_valence, max_valence, limit=1000)

        elif mode == SearchMode.IMPORTANCE:
            min_importance = filters.get("min_importance", 0.0)
            memories = self.episodic.search_by_importance(min_importance, limit=1000)

        else:  # SEMANTIC or ASSOCIATIVE
            # Get all episodic memories
            memories = list(self.episodic._memories.values())

        # Score memories
        results = []
        for memory in memories:
            score = self._calculate_relevance(memory, query, mode, **filters)
            results.append((memory, score))

        return results

    def _search_semantic(self, query: str, mode: SearchMode,
                        **filters) -> List[Tuple[Memory, float]]:
        """Search semantic memory"""
        if mode == SearchMode.SEMANTIC:
            # Use semantic similarity search
            similar_concepts = self.semantic.search_similar(query, threshold=0.2, limit=1000)

            results = []
            for concept, similarity in similar_concepts:
                memory = self.semantic.get_concept(concept)
                if memory:
                    results.append((memory, similarity))

            return results

        else:
            # Fallback to all semantic memories
            memories = list(self.semantic._concepts.values()) + list(self.semantic._facts.values())

            results = []
            for memory in memories:
                score = self._calculate_relevance(memory, query, mode, **filters)
                results.append((memory, score))

            return results

    def _search_procedural(self, query: str, mode: SearchMode,
                          **filters) -> List[Tuple[Memory, float]]:
        """Search procedural memory"""
        memories = list(self.procedural._skills.values())

        results = []
        for memory in memories:
            score = self._calculate_relevance(memory, query, mode, **filters)
            results.append((memory, score))

        return results

    def _calculate_relevance(self, memory: Memory, query: str,
                            mode: SearchMode, **filters) -> float:
        """
        Calculate relevance score combining multiple factors.

        Combines:
        - Semantic similarity (word overlap)
        - Temporal recency (exponential decay)
        - Importance (normalized)
        - Mode-specific boosts
        """
        # Base semantic similarity
        semantic_sim = self._word_overlap(memory.content, query)

        # Temporal recency score
        hours_ago = (datetime.now() - memory.timestamp).total_seconds() / 3600
        recency_score = self.RECENCY_DECAY_RATE ** hours_ago

        # Importance score (normalized 0-1)
        importance_score = memory.importance / 10.0

        # Access frequency boost
        access_boost = min(memory.access_count / 100.0, 0.2)

        # Mode-specific scoring
        mode_boost = 1.0

        if mode == SearchMode.TEMPORAL:
            mode_boost = 1.0 + 0.5 * recency_score

        elif mode == SearchMode.IMPORTANCE:
            mode_boost = 1.0 + 0.5 * importance_score

        elif mode == SearchMode.EMOTIONAL:
            # Boost emotionally charged memories
            emotional_intensity = abs(memory.emotional_valence)
            mode_boost = 1.0 + 0.5 * emotional_intensity

        # Combined score (weighted average)
        score = (
            0.4 * semantic_sim +
            0.3 * recency_score +
            0.2 * importance_score +
            0.1 * access_boost
        ) * mode_boost

        return score

    def _word_overlap(self, text1: str, text2: str) -> float:
        """Calculate word overlap similarity"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        if not words1 or not words2:
            return 0.0

        intersection = len(words1 & words2)
        union = len(words1 | words2)

        return intersection / union if union > 0 else 0.0

    def _rank_results(self, results: List[Tuple[Memory, float]],
                     query: str) -> List[Tuple[Memory, float]]:
        """Rank results by relevance score"""
        # Sort by score descending
        results.sort(key=lambda x: x[1], reverse=True)

        # Update access counts for retrieved memories
        for memory, score in results:
            memory.access_count += 1
            memory.last_accessed = datetime.now()

        return results

    def retrieve_associated(self, memory: Memory,
                           max_depth: int = 2) -> List[Memory]:
        """
        Retrieve memories associated with given memory.

        Args:
            memory: Starting memory
            max_depth: Association depth

        Returns:
            List of associated memories
        """
        associated = set()
        queue = [memory]

        for _ in range(max_depth):
            if not queue:
                break

            current = queue.pop(0)

            # Get related memories
            for rel_id in current.related_memory_ids:
                if rel_id in self.episodic._memories:
                    rel_memory = self.episodic._memories[rel_id]
                    if rel_memory.id not in associated:
                        associated.add(rel_memory.id)
                        queue.append(rel_memory)

        # Convert IDs to memories
        return [
            self.episodic._memories[mid]
            for mid in associated
            if mid in self.episodic._memories
        ]

    def get_retrieval_statistics(self) -> Dict[str, Any]:
        """Get retrieval system statistics"""
        all_memories = (
            len(self.working) +
            len(self.episodic) +
            len(self.semantic) +
            len(self.procedural)
        )

        total_accesses = (
            sum(m.access_count for m in self.working.get_all()) +
            sum(m.access_count for m in self.episodic._memories.values()) +
            sum(m.access_count for m in self.semantic._concepts.values()) +
            sum(m.access_count for m in self.semantic._facts.values()) +
            sum(m.access_count for m in self.procedural._skills.values())
        )

        return {
            "total_memories": all_memories,
            "total_accesses": total_accesses,
            "working_count": len(self.working),
            "episodic_count": len(self.episodic),
            "semantic_count": len(self.semantic),
            "procedural_count": len(self.procedural),
        }
