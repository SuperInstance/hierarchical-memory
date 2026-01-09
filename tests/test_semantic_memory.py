"""
Test suite for Semantic Memory module.

Tests cover:
- Concept storage and retrieval
- Fact storage and verification
- Hierarchical relationships
- Vector similarity search
- Statistics and monitoring
"""

import pytest
import numpy as np
from hierarchical_memory.semantic_memory import SemanticMemory
from hierarchical_memory.memory_types import MemoryType


class TestSemanticMemoryBasics:
    """Test basic semantic memory functionality."""

    @pytest.mark.semantic
    def test_initialization(self, semantic_memory):
        """Test semantic memory initialization."""
        assert semantic_memory is not None
        assert len(semantic_memory) == 0

    @pytest.mark.semantic
    def test_store_concept(self, semantic_memory):
        """Test storing a semantic concept."""
        memory = semantic_memory.store_concept(
            concept="Python",
            definition="A high-level programming language",
            importance=9.0
        )
        assert memory is not None
        assert "Python" in memory.content
        assert memory.importance == 9.0
        assert memory.memory_type == MemoryType.SEMANTIC
        assert len(semantic_memory) == 1

    @pytest.mark.semantic
    def test_store_concept_with_hierarchy(self, semantic_memory):
        """Test storing concept with parent-child relationship."""
        parent = semantic_memory.store_concept(
            concept="Animal",
            definition="Living organism",
            importance=8.0
        )
        child = semantic_memory.store_concept(
            concept="Mammal",
            definition="Warm-blooded animal",
            importance=7.0,
            parent_concept="Animal"
        )
        assert parent is not None
        assert child is not None

    @pytest.mark.semantic
    def test_store_fact(self, semantic_memory):
        """Test storing a semantic fact."""
        memory = semantic_memory.store_fact(
            fact="The Earth orbits around the Sun",
            confidence=1.0
        )
        assert memory is not None
        assert "Earth orbits" in memory.content
        assert memory.importance == 7.0  # 7.0 * confidence

    @pytest.mark.semantic
    def test_store_fact_with_sources(self, semantic_memory):
        """Test storing fact with source memories."""
        memory = semantic_memory.store_fact(
            fact="Paris is the capital of France",
            confidence=0.95,
            source_memory_ids=["mem1", "mem2", "mem3"]
        )
        assert memory is not None
        assert len(memory.consolidation_source_ids) == 3


class TestConceptRetrieval:
    """Test concept retrieval operations."""

    @pytest.mark.semantic
    def test_get_concept(self, semantic_memory):
        """Test retrieving concept by name."""
        semantic_memory.store_concept("Python", "Programming language", 8.0)
        concept = semantic_memory.get_concept("Python")
        assert concept is not None
        assert "Python" in concept.content

    @pytest.mark.semantic
    def test_get_nonexistent_concept(self, semantic_memory):
        """Test retrieving non-existent concept."""
        concept = semantic_memory.get_concept("NonExistent")
        assert concept is None

    @pytest.mark.semantic
    def test_access_count_increments(self, semantic_memory):
        """Test that access count increments."""
        semantic_memory.store_concept("Python", "Language", 8.0)
        semantic_memory.get_concept("Python")
        retrieved = semantic_memory.get_concept("Python")
        assert retrieved.access_count == 2


class TestHierarchicalRelationships:
    """Test hierarchical concept relationships."""

    @pytest.mark.semantic
    def test_get_related_concepts(self, semantic_memory):
        """Test getting related concepts from hierarchy."""
        # Create hierarchy: Animal -> Mammal -> Dog
        semantic_memory.store_concept("Animal", "Living thing", 8.0)
        semantic_memory.store_concept("Mammal", "Warm-blooded", 7.0, "Animal")
        semantic_memory.store_concept("Dog", "Domestic animal", 6.0, "Mammal")

        related = semantic_memory.get_related_concepts("Animal", depth=2)
        assert "Mammal" in related
        assert "Dog" in related

    @pytest.mark.semantic
    def test_no_related_concepts(self, semantic_memory):
        """Test getting related concepts for concept with no children."""
        semantic_memory.store_concept("Lonely", "No children", 5.0)
        related = semantic_memory.get_related_concepts("Lonely", depth=2)
        assert len(related) == 0

    @pytest.mark.semantic
    def test_depth_limit(self, semantic_memory):
        """Test that depth limit works in related concepts."""
        # Create deep hierarchy
        semantic_memory.store_concept("A", "Level 0", 8.0)
        semantic_memory.store_concept("B", "Level 1", 7.0, "A")
        semantic_memory.store_concept("C", "Level 2", 6.0, "B")
        semantic_memory.store_concept("D", "Level 3", 5.0, "C")

        related_depth_1 = semantic_memory.get_related_concepts("A", depth=1)
        related_depth_2 = semantic_memory.get_related_concepts("A", depth=2)

        assert "B" in related_depth_1
        assert "C" not in related_depth_1
        assert "C" in related_depth_2


class TestFactVerification:
    """Test fact verification functionality."""

    @pytest.mark.semantic
    def test_verify_known_fact(self, semantic_memory):
        """Test verifying a known fact."""
        semantic_memory.store_fact("Water boils at 100C", confidence=1.0)
        is_known, confidence = semantic_memory.verify_fact("Water boils at 100C")
        assert is_known is True
        assert confidence == 1.0

    @pytest.mark.semantic
    def test_verify_unknown_fact(self, semantic_memory):
        """Test verifying an unknown fact."""
        is_known, confidence = semantic_memory.verify_fact("Moon is made of cheese")
        assert is_known is False
        assert confidence == 0.0

    @pytest.mark.semantic
    def test_verify_partial_confidence(self, semantic_memory):
        """Test fact with partial confidence."""
        semantic_memory.store_fact("It might rain tomorrow", confidence=0.5)
        is_known, confidence = semantic_memory.verify_fact("It might rain tomorrow")
        assert is_known is True
        assert confidence == 0.5


class TestSimilaritySearch:
    """Test vector similarity search."""

    @pytest.mark.semantic
    def test_search_similar_concepts(self, semantic_memory):
        """Test finding similar concepts."""
        # Store related concepts
        semantic_memory.store_concept("Python", "Programming language for data science", 8.0)
        semantic_memory.store_concept("Java", "Programming language for enterprise", 7.0)
        semantic_memory.store_concept("Pizza", "Italian food", 5.0)

        # Search for programming-related query
        results = semantic_memory.search_similar("programming code", threshold=0.0, limit=5)
        assert len(results) > 0
        
        # Python or Java should be in results (they share "programming")
        concepts = [r[0] for r in results]
        assert "Python" in concepts or "Java" in concepts

    @pytest.mark.semantic
    def test_similarity_threshold(self, semantic_memory):
        """Test similarity threshold filtering."""
        semantic_memory.store_concept("Apple", "Fruit that grows on trees", 7.0)
        semantic_memory.store_concept("Orange", "Citrus fruit", 7.0)

        # High threshold should return fewer or no results
        high_threshold = semantic_memory.search_similar("banana", threshold=0.9, limit=5)
        low_threshold = semantic_memory.search_similar("banana", threshold=0.0, limit=5)

        assert len(high_threshold) <= len(low_threshold)

    @pytest.mark.semantic
    def test_similarity_ranking(self, semantic_memory):
        """Test that results are ranked by similarity."""
        semantic_memory.store_concept("Cat", "Small furry pet", 7.0)
        semantic_memory.store_concept("Car", "Vehicle with wheels", 5.0)

        results = semantic_memory.search_similar("kitten", threshold=0.0, limit=5)
        if len(results) >= 2:
            # Cat should be more similar to kitten than car
            similarities = [r[1] for r in results]
            assert similarities[0] >= similarities[1]


class TestStatistics:
    """Test statistics and monitoring."""

    @pytest.mark.semantic
    def test_get_statistics_empty(self, semantic_memory):
        """Test statistics for empty semantic memory."""
        stats = semantic_memory.get_statistics()
        assert stats["total_concepts"] == 0
        assert stats["total_facts"] == 0
        assert stats["total_memories"] == 0

    @pytest.mark.semantic
    def test_get_statistics_populated(self, populated_semantic_memory):
        """Test statistics for populated semantic memory."""
        semantic, memories = populated_semantic_memory
        stats = semantic.get_statistics()
        assert stats["total_concepts"] > 0
        assert stats["total_facts"] > 0
        assert stats["total_memories"] == stats["total_concepts"] + stats["total_facts"]

    @pytest.mark.semantic
    def test_hierarchy_edges_count(self, semantic_memory):
        """Test hierarchy edge counting."""
        semantic.store_concept("A", "Root", 8.0)
        semantic.store_concept("B", "Child 1", 7.0, "A")
        semantic.store_concept("C", "Child 2", 7.0, "A")

        stats = semantic.get_statistics()
        assert stats["hierarchy_edges"] == 2


class TestEdgeCases:
    """Test edge cases and error handling."""

    @pytest.mark.semantic
    def test_empty_concept_name(self, semantic_memory):
        """Test storing concept with empty name."""
        memory = semantic_memory.store_concept("", "Empty name", 5.0)
        assert memory is not None

    @pytest.mark.semantic
    def test_very_long_definition(self, semantic_memory):
        """Test storing concept with very long definition."""
        long_def = "A" * 10000
        memory = semantic_memory.store_concept("LongConcept", long_def, 5.0)
        assert memory is not None

    @pytest.mark.semantic
    def test_unicode_content(self, semantic_memory):
        """Test storing unicode content."""
        memory = semantic_memory.store_concept("概念", "中文概念定义", 7.0)
        assert memory is not None

    @pytest.mark.semantic
    def test_confidence_bounds(self, semantic_memory):
        """Test fact confidence within bounds."""
        # Valid range
        semantic_memory.store_fact("Fact 1", confidence=0.0)
        semantic_memory.store_fact("Fact 2", confidence=0.5)
        semantic_memory.store_fact("Fact 3", confidence=1.0)


class TestVectorOperations:
    """Test vector embedding operations."""

    @pytest.mark.semantic
    def test_simple_embedding_generation(self, semantic_memory):
        """Test that embeddings are generated."""
        semantic_memory.store_concept("Test", "Test concept definition", 5.0)
        # Embedding should be created internally
        assert len(semantic_memory._embeddings) > 0

    @pytest.mark.semantic
    def test_cosine_similarity(self, semantic_memory):
        """Test cosine similarity calculation."""
        vec1 = np.array([1.0, 0.0, 0.0])
        vec2 = np.array([1.0, 0.0, 0.0])
        vec3 = np.array([0.0, 1.0, 0.0])

        # Identical vectors
        sim_12 = semantic_memory._cosine_similarity(vec1, vec2)
        assert sim_12 == 1.0

        # Orthogonal vectors
        sim_13 = semantic_memory._cosine_similarity(vec1, vec3)
        assert sim_13 == 0.0

    @pytest.mark.semantic
    def test_zero_vector_handling(self, semantic_memory):
        """Test handling of zero vectors."""
        vec1 = np.array([0.0, 0.0, 0.0])
        vec2 = np.array([1.0, 0.0, 0.0])

        similarity = semantic_memory._cosine_similarity(vec1, vec2)
        assert similarity == 0.0


class TestIntegration:
    """Integration tests for semantic memory."""

    @pytest.mark.semantic
    @pytest.mark.integration
    def test_knowledge_building_workflow(self, semantic_memory):
        """Test building knowledge from episodic-like experiences."""
        # Extract facts from experiences
        experiences = [
            "I saw a penguin at the zoo",
            "Penguins are birds that cannot fly",
            "Penguins live in Antarctica",
        ]

        # Store as concepts/facts
        for exp in experiences:
            semantic_memory.store_fact(exp, confidence=0.8)

        # Verify knowledge can be retrieved
        is_known, conf = semantic_memory.verify_fact(experiences[0])
        assert is_known is True

    @pytest.mark.semantic
    @pytest.mark.integration
    def test_domain_knowledge_structure(self, semantic_memory):
        """Test building structured domain knowledge."""
        # Programming domain
        semantic_memory.store_concept("Programming", "Writing code", 9.0)
        semantic_memory.store_concept("Python", "Language", 8.0, "Programming")
        semantic_memory.store_concept("Java", "Language", 8.0, "Programming")
        semantic_memory.store_concept("Data Science", "Python application", 7.0, "Python")

        # Test hierarchy navigation
        related = semantic_memory.get_related_concepts("Programming", depth=2)
        assert len(related) == 3  # Python, Java, Data Science

        # Test similarity search
        results = semantic_memory.search_similar("coding", threshold=0.0, limit=5)
        assert len(results) > 0
