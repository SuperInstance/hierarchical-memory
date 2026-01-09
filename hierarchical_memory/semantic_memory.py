"""
Semantic Memory Module
======================

Implements conceptual knowledge with:
- Concept storage
- Fact verification
- Pattern extraction
- Hierarchical categories
"""

from typing import List, Optional, Dict, Set, Any
from datetime import datetime
from collections import defaultdict
import numpy as np

from .memory_types import Memory, MemoryType


class SemanticMemory:
    """
    Semantic Memory: Consolidated concepts, facts, and patterns

    Neuroscience: General knowledge disconnected from specific episodes.
    Extracted from repeated patterns in episodic memory.
    """

    def __init__(self):
        self._concepts: Dict[str, Memory] = {}
        self._facts: Dict[str, Memory] = {}
        self._hierarchy: Dict[str, List[str]] = defaultdict(list)  # parent -> children
        self._embeddings: Dict[str, np.ndarray] = {}  # Simple word count embeddings

    def store_concept(self,
                     concept: str,
                     definition: str,
                     importance: float = 6.0,
                     parent_concept: Optional[str] = None) -> Memory:
        """
        Store a semantic concept.

        Args:
            concept: Concept name
            definition: Concept definition
            importance: Importance score (1-10)
            parent_concept: Parent concept in hierarchy

        Returns:
            Created memory object
        """
        content = f"Concept: {concept} - {definition}"

        memory = Memory(
            id=Memory.generate_id(content, datetime.now()),
            content=content,
            memory_type=MemoryType.SEMANTIC,
            timestamp=datetime.now(),
            importance=importance
        )

        self._concepts[concept] = memory

        # Build hierarchy
        if parent_concept:
            self._hierarchy[parent_concept].append(concept)

        # Generate simple embedding
        self._embeddings[concept] = self._simple_embedding(definition)

        return memory

    def store_fact(self,
                  fact: str,
                  confidence: float = 1.0,
                  source_memory_ids: List[str] = None) -> Memory:
        """
        Store a semantic fact.

        Args:
            fact: Factual statement
            confidence: Confidence in fact (0-1)
            source_memory_ids: Source episodic memories

        Returns:
            Created memory object
        """
        memory = Memory(
            id=Memory.generate_id(fact, datetime.now()),
            content=f"Fact: {fact}",
            memory_type=MemoryType.SEMANTIC,
            timestamp=datetime.now(),
            importance=7.0 * confidence,
            consolidation_source_ids=source_memory_ids or []
        )

        self._facts[fact] = memory

        return memory

    def get_concept(self, concept: str) -> Optional[Memory]:
        """
        Retrieve concept by name.

        Args:
            concept: Concept name

        Returns:
            Memory object or None
        """
        memory = self._concepts.get(concept)

        if memory:
            memory.access_count += 1
            memory.last_accessed = datetime.now()

        return memory

    def get_related_concepts(self, concept: str,
                             depth: int = 1) -> List[str]:
        """
        Get concepts related by hierarchy.

        Args:
            concept: Starting concept
            depth: Hierarchy depth to search

        Returns:
            List of related concept names
        """
        related = set()

        # Get children
        queue = [(concept, 0)]

        while queue:
            current, level = queue.pop(0)

            if level >= depth:
                continue

            for child in self._hierarchy.get(current, []):
                related.add(child)
                queue.append((child, level + 1))

        return list(related)

    def verify_fact(self, fact: str) -> tuple[bool, float]:
        """
        Verify if fact is stored and its confidence.

        Args:
            fact: Fact to verify

        Returns:
            (is_known, confidence) tuple
        """
        memory = self._facts.get(fact)

        if not memory:
            return False, 0.0

        # Confidence derived from importance
        confidence = min(memory.importance / 7.0, 1.0)

        return True, confidence

    def search_similar(self, query: str,
                      threshold: float = 0.3,
                      limit: int = 10) -> List[tuple[str, float]]:
        """
        Find concepts similar to query using embeddings.

        Args:
            query: Search query
            threshold: Similarity threshold
            limit: Maximum results

        Returns:
            List of (concept, similarity) tuples
        """
        query_embedding = self._simple_embedding(query)

        similarities = []

        for concept, embedding in self._embeddings.items():
            similarity = self._cosine_similarity(query_embedding, embedding)

            if similarity >= threshold:
                similarities.append((concept, similarity))

        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)

        return similarities[:limit]

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get semantic memory statistics.

        Returns:
            Statistics dictionary
        """
        total_importance = sum(m.importance for m in self._concepts.values())
        total_importance += sum(m.importance for m in self._facts.values())
        total_memories = len(self._concepts) + len(self._facts)

        return {
            "total_concepts": len(self._concepts),
            "total_facts": len(self._facts),
            "total_memories": total_memories,
            "hierarchy_edges": sum(len(children) for children in self._hierarchy.values()),
            "average_importance": total_importance / total_memories if total_memories > 0 else 0.0,
        }

    def _simple_embedding(self, text: str) -> np.ndarray:
        """
        Generate simple word-count embedding.

        Args:
            text: Input text

        Returns:
            Word frequency vector
        """
        words = text.lower().split()
        word_counts = defaultdict(int)

        for word in words:
            if len(word) > 2:  # Ignore short words
                word_counts[word] += 1

        # Return as simple hash-based vector
        vocab_size = 100
        vector = np.zeros(vocab_size)

        for word, count in word_counts.items():
            idx = hash(word) % vocab_size
            vector[idx] = count

        return vector

    def _cosine_similarity(self, vec1: np.ndarray,
                          vec2: np.ndarray) -> float:
        """
        Calculate cosine similarity between vectors.

        Args:
            vec1: First vector
            vec2: Second vector

        Returns:
            Similarity score (0-1)
        """
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def __len__(self) -> int:
        """Return total number of semantic memories"""
        return len(self._concepts) + len(self._facts)
