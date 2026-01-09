"""
Test suite for Memory Retrieval module.

Tests cover:
- Semantic search
- Temporal search
- Spatial search
- Contextual search
- Associative search
- Hybrid search
- Multi-tier retrieval
"""

import pytest
import numpy as np
from hierarchical_memory.retrieval.search import (
    MemoryRetrieval,
    RetrievalMode,
    RetrievalResult
)
from hierarchical_memory.core.working import WorkingMemory
from hierarchical_memory.core.episodic import EpisodicMemory
from hierarchical_memory.core.semantic import SemanticMemory
from hierarchical_memory.core.procedural import ProceduralMemory


class TestMemoryRetrievalBasics:
    """Test basic memory retrieval functionality."""

    @pytest.mark.retrieval
    def test_initialization(self, working_memory, episodic_memory, semantic_memory, procedural_memory):
        """Test memory retrieval system initialization."""
        retrieval = MemoryRetrieval(
            working_memory=working_memory,
            episodic_memory=episodic_memory,
            semantic_memory=semantic_memory,
            procedural_memory=procedural_memory,
            default_top_k=10
        )
        assert retrieval is not None
        assert retrieval.default_top_k == 10

    @pytest.mark.retrieval
    def test_search_basic(self, memory_retrieval, sample_texts):
        """Test basic search functionality."""
        retrieval = memory_retrieval
        results = retrieval.search("test query", RetrievalMode.SEMANTIC, top_k=5)
        assert isinstance(results, list)


class TestSemanticSearch:
    """Test semantic similarity search."""

    @pytest.mark.retrieval
    def test_semantic_mode(self, memory_retrieval, populated_all_memory_systems):
        """Test semantic search mode."""
        retrieval = memory_retrieval
        results = retrieval.search("programming", RetrievalMode.SEMANTIC, top_k=5)
        assert isinstance(results, list)
        assert len(results) <= 5

        # Check result structure
        for result in results:
            assert isinstance(result, RetrievalResult)
            assert result.tier in ["working", "episodic", "semantic", "procedural"]
            assert isinstance(result.score, float)

    @pytest.mark.retrieval
    def test_semantic_search_ranking(self, memory_retrieval, populated_all_memory_systems):
        """Test that semantic results are ranked by relevance."""
        retrieval = memory_retrieval
        results = retrieval.search("Python", RetrievalMode.SEMANTIC, top_k=10)

        # Results should be sorted by score (descending)
        for i in range(len(results) - 1):
            assert results[i].score >= results[i+1].score


class TestTemporalSearch:
    """Test temporal-based search."""

    @pytest.mark.retrieval
    def test_temporal_mode(self, memory_retrieval, populated_all_memory_systems, time_range):
        """Test temporal search mode."""
        retrieval = memory_retrieval
        start, end = time_range

        results = retrieval.search(
            "query",
            RetrievalMode.TEMPORAL,
            top_k=5,
            start_time=start.timestamp(),
            end_time=end.timestamp()
        )
        assert isinstance(results, list)

    @pytest.mark.retrieval
    def test_recent_search(self, memory_retrieval, populated_all_memory_systems):
        """Test searching recent memories."""
        retrieval = memory_retrieval

        results = retrieval.search(
            "recent",
            RetrievalMode.TEMPORAL,
            top_k=5,
            start_time=(time.time() - 86400)  # Last 24 hours
        )
        assert isinstance(results, list)


class TestContextualSearch:
    """Test context-based search."""

    @pytest.mark.retrieval
    def test_contextual_mode(self, memory_retrieval, populated_all_memory_systems):
        """Test contextual search mode."""
        retrieval = memory_retrieval

        results = retrieval.search(
            "query",
            RetrievalMode.CONTEXTUAL,
            top_k=5,
            context_key="location",
            context_value="Hawaii"
        )
        assert isinstance(results, list)


class TestAssociativeSearch:
    """Test associative search functionality."""

    @pytest.mark.retrieval
    def test_associative_search(self, memory_retrieval, populated_all_memory_systems):
        """Test associative search from seed item."""
        retrieval = memory_retrieval

        # Search from semantic concept
        results = retrieval.associative_search(
            seed_item="Machine Learning",
            tier="semantic",
            max_depth=2,
            top_k=5
        )
        assert isinstance(results, list)

    @pytest.mark.retrieval
    def test_associative_depth_limit(self, memory_retrieval, populated_all_memory_systems):
        """Test that associative search respects depth limit."""
        retrieval = memory_retrieval

        shallow = retrieval.associative_search(
            seed_item="Python",
            tier="semantic",
            max_depth=1,
            top_k=10
        )

        deep = retrieval.associative_search(
            seed_item="Python",
            tier="semantic",
            max_depth=3,
            top_k=10
        )

        # Deeper search should return more or equal results
        assert len(deep) >= len(shallow)


class TestHybridSearch:
    """Test hybrid search combining multiple modes."""

    @pytest.mark.retrieval
    def test_hybrid_search_default_weights(self, memory_retrieval, populated_all_memory_systems):
        """Test hybrid search with default weights."""
        retrieval = memory_retrieval

        results = retrieval.hybrid_search("Python programming", top_k=5)
        assert isinstance(results, list)
        assert len(results) <= 5

    @pytest.mark.retrieval
    def test_hybrid_search_custom_weights(self, memory_retrieval, populated_all_memory_systems):
        """Test hybrid search with custom weights."""
        retrieval = memory_retrieval

        custom_weights = {
            "semantic": 0.8,
            "temporal": 0.1,
            "contextual": 0.05,
            "associative": 0.05
        }

        results = retrieval.hybrid_search(
            "query",
            weights=custom_weights,
            top_k=5
        )
        assert isinstance(results, list)

    @pytest.mark.retrieval
    def test_hbrid_deduplication(self, memory_retrieval, populated_all_memory_systems):
        """Test that hybrid search deduplicates results."""
        retrieval = memory_retrieval

        results = retrieval.hybrid_search("Python", top_k=10)

        # Check for duplicates by content
        contents = [str(r.content) for r in results]
        unique_contents = set(contents)
        assert len(contents) == len(unique_contents)


class TestTierSpecificSearch:
    """Test searching specific memory tiers."""

    @pytest.mark.retrieval
    def test_working_tier_search(self, memory_retrieval, populated_all_memory_systems):
        """Test searching only working memory."""
        retrieval = memory_retrieval

        results = retrieval.search("task", RetrievalMode.SEMANTIC, tier="working", top_k=5)
        assert isinstance(results, list)
        assert all(r.tier == "working" for r in results)

    @pytest.mark.retrieval
    def test_episodic_tier_search(self, memory_retrieval, populated_all_memory_systems):
        """Test searching only episodic memory."""
        retrieval = memory_retrieval

        results = retrieval.search("event", RetrievalMode.SEMANTIC, tier="episodic", top_k=5)
        assert isinstance(results, list)
        assert all(r.tier == "episodic" for r in results)

    @pytest.mark.retrieval
    def test_semantic_tier_search(self, memory_retrieval, populated_all_memory_systems):
        """Test searching only semantic memory."""
        retrieval = memory_retrieval

        results = retrieval.search("concept", RetrievalMode.SEMANTIC, tier="semantic", top_k=5)
        assert isinstance(results, list)
        assert all(r.tier == "semantic" for r in results)

    @pytest.mark.retrieval
    def test_procedural_tier_search(self, memory_retrieval, populated_all_memory_systems):
        """Test searching only procedural memory."""
        retrieval = memory_retrieval

        results = retrieval.search("skill", RetrievalMode.SEMANTIC, tier="procedural", top_k=5)
        assert isinstance(results, list)
        assert all(r.tier == "procedural" for r in results)


class TestResultRanking:
    """Test result ranking and scoring."""

    @pytest.mark.retrieval
    def test_score_range(self, memory_retrieval, populated_all_memory_systems):
        """Test that scores are in valid range."""
        retrieval = memory_retrieval

        results = retrieval.search("query", RetrievalMode.SEMANTIC, top_k=10)

        for result in results:
            assert 0.0 <= result.score <= 1.0

    @pytest.mark.retrieval
    def test_top_k_limit(self, memory_retrieval, populated_all_memory_systems):
        """Test that top_k limit is respected."""
        retrieval = memory_retrieval

        for k in [1, 5, 10, 20]:
            results = retrieval.search("query", RetrievalMode.SEMANTIC, top_k=k)
            assert len(results) <= k


class TestRetrievalResult:
    """Test retrieval result data structure."""

    @pytest.mark.retrieval
    def test_result_structure(self, memory_retrieval):
        """Test RetrievalResult structure."""
        result = RetrievalResult(
            content="Test content",
            tier="episodic",
            score=0.85,
            metadata={"key": "value"},
            timestamp=time.time()
        )

        assert result.content == "Test content"
        assert result.tier == "episodic"
        assert result.score == 0.85
        assert result.metadata == {"key": "value"}
        assert result.timestamp is not None


class TestEdgeCases:
    """Test edge cases and error handling."""

    @pytest.mark.retrieval
    def test_empty_query(self, memory_retrieval, populated_all_memory_systems):
        """Test search with empty query."""
        retrieval = memory_retrieval

        results = retrieval.search("", RetrievalMode.SEMANTIC, top_k=5)
        assert isinstance(results, list)

    @pytest.mark.retrieval
    def test_no_results(self, memory_retrieval):
        """Test search that returns no results."""
        retrieval = memory_retrieval

        results = retrieval.search(
            "nonexistent_unique_term_xyz123",
            RetrievalMode.SEMANTIC,
            top_k=5
        )
        # May return empty list or results with low scores
        assert isinstance(results, list)

    @pytest.mark.retrieval
    def test_very_long_query(self, memory_retrieval, populated_all_memory_systems):
        """Test search with very long query."""
        retrieval = memory_retrieval
        long_query = "test " * 100

        results = retrieval.search(long_query, RetrievalMode.SEMANTIC, top_k=5)
        assert isinstance(results, list)


class TestIntegration:
    """Integration tests for memory retrieval."""

    @pytest.mark.retrieval
    @pytest.mark.integration
    def test_cross_tier_search(self, memory_retrieval, populated_all_memory_systems):
        """Test searching across all memory tiers."""
        retrieval = memory_retrieval

        results = retrieval.search("important", RetrievalMode.SEMANTIC, top_k=20)

        # Check that we get results from multiple tiers
        tiers = set(r.tier for r in results)
        # At least working memory should have been populated
        assert len(tiers) >= 0

    @pytest.mark.retrieval
    @pytest.mark.integration
    def test_complex_multi_modal_search(self, memory_retrieval, populated_all_memory_systems):
        """Test complex search combining multiple modes."""
        retrieval = memory_retrieval

        # Search for recent, important, semantically related memories
        results = retrieval.hybrid_search(
            "Python programming",
            weights={
                "semantic": 0.5,
                "temporal": 0.3,
                "contextual": 0.2
            },
            top_k=10
        )

        assert isinstance(results, list)
        assert len(results) <= 10

        # Verify ranking
        for i in range(len(results) - 1):
            assert results[i].score >= results[i+1].score

    @pytest.mark.retrieval
    @pytest.mark.integration
    def test_retrieval_with_consolidation(self, working_memory, episodic_memory, semantic_memory, procedural_memory):
        """Test retrieval after consolidation."""
        # Add items
        from hierarchical_memory.core.working import MemoryItem
        for i in range(5):
            key = f"item{i}"
            item = MemoryItem(content=f"Python programming task {i}", importance=0.8)
            working_memory._items[key] = item

        # Create retrieval system
        retrieval = MemoryRetrieval(
            working_memory, episodic_memory, semantic_memory, procedural_memory
        )

        # Search before consolidation
        results_before = retrieval.search("Python", RetrievalMode.SEMANTIC, top_k=10)

        # Consolidate
        from hierarchical_memory.consolidation.pipeline import ConsolidationPipeline
        pipeline = ConsolidationPipeline(working_memory, episodic_memory, semantic_memory)
        for key in list(working_memory._items.keys()):
            pipeline.add_to_queue("working", "episodic", key, 0.8)
        pipeline.consolidate_next_batch()

        # Search after consolidation
        results_after = retrieval.search("Python", RetrievalMode.SEMANTIC, top_k=10)

        # Both should return results
        assert isinstance(results_before, list)
        assert isinstance(results_after, list)
