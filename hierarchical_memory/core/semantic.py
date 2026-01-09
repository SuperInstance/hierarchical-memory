"""
Semantic Memory Module
General knowledge and concepts without temporal context.

Based on Tulving's semantic memory theory - general world knowledge,
concepts, and facts independent of personal experience.
"""

import time
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass, field
from collections import defaultdict
import numpy as np


@dataclass
class Concept:
    """A concept in semantic memory."""
    name: str
    embedding: Optional[np.ndarray] = None
    attributes: Dict[str, Any] = field(default_factory=dict)
    associations: Set[str] = field(default_factory=set)
    access_count: int = 0
    last_accessed: float = field(default_factory=time.time)
    creation_time: float = field(default_factory=time.time)


class SemanticMemory:
    """
    Semantic memory for storing and retrieving general knowledge.

    Features:
    - Vector embeddings for similarity-based retrieval
    - Concept hierarchies and associations
    - Attribute-based storage
    - Similarity search using cosine similarity
    """

    def __init__(
        self,
        embedding_dim: int = 384,
        enable_embeddings: bool = True
    ):
        """
        Initialize semantic memory.

        Args:
            embedding_dim: Dimension of embedding vectors (default: 384)
            enable_embeddings: Whether to use vector embeddings (default: True)
        """
        self.embedding_dim = embedding_dim
        self.enable_embeddings = enable_embeddings
        self._concepts: Dict[str, Concept] = {}
        self._hierarchy: Dict[str, Set[str]] = defaultdict(set)  # parent -> children

    def add_concept(
        self,
        name: str,
        embedding: Optional[np.ndarray] = None,
        attributes: Optional[Dict[str, Any]] = None,
        parent: Optional[str] = None
    ) -> bool:
        """
        Add a concept to semantic memory.

        Args:
            name: Concept name (unique identifier)
            embedding: Optional vector embedding
            attributes: Optional concept attributes
            parent: Optional parent concept for hierarchy

        Returns:
            True if added successfully
        """
        if not name:
            raise ValueError("Concept name cannot be empty")
        if name in self._concepts:
            return False

        # Create embedding if not provided and enabled
        if embedding is None and self.enable_embeddings:
            # Simple random embedding (in production, use proper encoder)
            embedding = np.random.randn(self.embedding_dim)
            embedding = embedding / np.linalg.norm(embedding)

        concept = Concept(
            name=name,
            embedding=embedding,
            attributes=attributes or {}
        )

        self._concepts[name] = concept

        # Add to hierarchy if parent specified
        if parent and parent in self._concepts:
            self._hierarchy[parent].add(name)
            concept.associations.add(parent)
            self._concepts[parent].associations.add(name)

        return True

    def get_concept(self, name: str) -> Optional[Concept]:
        """
        Retrieve a concept by name.

        Args:
            name: Concept name

        Returns:
            The concept, or None if not found
        """
        concept = self._concepts.get(name)
        if concept:
            concept.access_count += 1
            concept.last_accessed = time.time()
        return concept

    def update_concept(
        self,
        name: str,
        attributes: Optional[Dict[str, Any]] = None,
        embedding: Optional[np.ndarray] = None
    ) -> bool:
        """
        Update an existing concept.

        Args:
            name: Concept name
            attributes: New attributes to merge
            embedding: New embedding

        Returns:
            True if updated successfully
        """
        concept = self._concepts.get(name)
        if not concept:
            return False

        if attributes:
            concept.attributes.update(attributes)

        if embedding is not None:
            concept.embedding = embedding

        return True

    def associate(self, concept1: str, concept2: str) -> bool:
        """
        Create an association between two concepts.

        Args:
            concept1: First concept name
            concept2: Second concept name

        Returns:
            True if association created
        """
        if concept1 not in self._concepts or concept2 not in self._concepts:
            return False

        self._concepts[concept1].associations.add(concept2)
        self._concepts[concept2].associations.add(concept1)
        return True

    def similarity_search(
        self,
        query: np.ndarray,
        top_k: int = 10,
        threshold: float = 0.7
    ) -> List[tuple[str, float]]:
        """
        Find concepts similar to query embedding.

        Args:
            query: Query embedding vector
            top_k: Maximum number of results
            threshold: Minimum similarity threshold

        Returns:
            List of (concept_name, similarity_score) tuples
        """
        if not self.enable_embeddings:
            return []

        # Normalize query
        query = query / np.linalg.norm(query)

        results = []
        for name, concept in self._concepts.items():
            if concept.embedding is not None:
                # Cosine similarity
                similarity = float(np.dot(query, concept.embedding))

                if similarity >= threshold:
                    results.append((name, similarity))

                    # Update access stats
                    concept.access_count += 1
                    concept.last_accessed = time.time()

        # Sort by similarity
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]

    def keyword_search(
        self,
        query: str,
        top_k: int = 10
    ) -> List[tuple[str, float]]:
        """
        Search concepts by keyword matching.

        Args:
            query: Search query
            top_k: Maximum number of results

        Returns:
            List of (concept_name, relevance_score) tuples
        """
        query_lower = query.lower()
        results = []

        for name, concept in self._concepts.items():
            score = 0.0

            # Match in name
            if query_lower in name.lower():
                score += 0.5

            # Match in attributes
            for key, value in concept.attributes.items():
                if query_lower in key.lower() or query_lower in str(value).lower():
                    score += 0.3

            # Match in associations
            for assoc in concept.associations:
                if query_lower in assoc.lower():
                    score += 0.2

            if score > 0:
                results.append((name, score))

        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]

    def get_children(self, parent: str) -> List[str]:
        """
        Get child concepts in hierarchy.

        Args:
            parent: Parent concept name

        Returns:
            List of child concept names
        """
        return list(self._hierarchy.get(parent, set()))

    def get_associations(self, concept: str) -> Set[str]:
        """
        Get associated concepts.

        Args:
            concept: Concept name

        Returns:
            Set of associated concept names
        """
        c = self._concepts.get(concept)
        return c.associations if c else set()

    def get_path_to_root(self, concept: str) -> List[str]:
        """
        Get path from concept to root of hierarchy.

        Args:
            concept: Starting concept name

        Returns:
            List of concept names from leaf to root
        """
        path = [concept]
        visited = set()

        while concept:
            visited.add(concept)

            # Find parent
            found_parent = False
            for parent, children in self._hierarchy.items():
                if concept in children and parent not in visited:
                    path.append(parent)
                    concept = parent
                    found_parent = True
                    break

            if not found_parent:
                break

        return path

    def get_stats(self) -> Dict[str, Any]:
        """
        Get memory statistics.

        Returns:
            Dictionary of statistics
        """
        total_accesses = sum(c.access_count for c in self._concepts.values())

        return {
            "total_concepts": len(self._concepts),
            "with_embeddings": sum(
                1 for c in self._concepts.values()
                if c.embedding is not None
            ),
            "total_associations": sum(
                len(c.associations) for c in self._concepts.values()
            ) // 2,
            "total_accesses": total_accesses,
            "avg_accesses": total_accesses / len(self._concepts) if self._concepts else 0
        }

    def __len__(self) -> int:
        """Return number of concepts."""
        return len(self._concepts)

    def __contains__(self, name: str) -> bool:
        """Check if concept exists."""
        return name in self._concepts

    def __repr__(self) -> str:
        """String representation of semantic memory."""
        return f"SemanticMemory(concepts={len(self._concepts)}, embedding_dim={self.embedding_dim})"


def create_semantic_memory(
    embedding_dim: int = 384,
    enable_embeddings: bool = True
) -> SemanticMemory:
    """
    Factory function to create a semantic memory instance.

    Args:
        embedding_dim: Dimension of embedding vectors
        enable_embeddings: Whether to use vector embeddings

    Returns:
        Configured SemanticMemory instance
    """
    return SemanticMemory(
        embedding_dim=embedding_dim,
        enable_embeddings=enable_embeddings
    )
