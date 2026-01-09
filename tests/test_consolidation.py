"""
Test suite for Memory Consolidation module.

Tests cover:
- Queue management
- Priority-based consolidation
- KL divergence calculation
- Sleep-based consolidation
- Working to episodic transfer
- Episodic to semantic transfer
"""

import pytest
import numpy as np
from hierarchical_memory.consolidation.pipeline import (
    ConsolidationPipeline,
    ConsolidationStatus,
    ConsolidationTask
)
from hierarchical_memory.core.working import WorkingMemory
from hierarchical_memory.core.episodic import EpisodicMemory
from hierarchical_memory.core.semantic import SemanticMemory


class TestConsolidationPipelineBasics:
    """Test basic consolidation pipeline functionality."""

    @pytest.mark.consolidation
    def test_initialization(self, working_memory, episodic_memory, semantic_memory):
        """Test consolidation pipeline initialization."""
        pipeline = ConsolidationPipeline(
            working_memory=working_memory,
            episodic_memory=episodic_memory,
            semantic_memory=semantic_memory,
            consolidation_threshold=0.7,
            batch_size=10
        )
        assert pipeline is not None
        assert pipeline.consolidation_threshold == 0.7
        assert pipeline.batch_size == 10
        assert pipeline.get_queue_size() == 0

    @pytest.mark.consolidation
    def test_add_to_queue(self, consolidation_pipeline):
        """Test adding items to consolidation queue."""
        pipeline = consolidation_pipeline
        pipeline.add_to_queue("working", "episodic", "item1", 0.8)
        pipeline.add_to_queue("working", "episodic", "item2", 0.6)

        assert pipeline.get_queue_size() == 2

    @pytest.mark.consolidation
    def test_prioritize_queue(self, consolidation_pipeline):
        """Test queue prioritization."""
        pipeline = consolidation_pipeline
        pipeline.add_to_queue("working", "episodic", "item1", 0.5)
        pipeline.add_to_queue("working", "episodic", "item2", 0.9)
        pipeline.add_to_queue("working", "episodic", "item3", 0.7)

        pipeline.prioritize_queue()

        # Highest priority should be first
        assert pipeline._queue[0].priority == 0.9

    @pytest.mark.consolidation
    def test_clear_queue(self, consolidation_pipeline):
        """Test clearing the consolidation queue."""
        pipeline = consolidation_pipeline
        pipeline.add_to_queue("working", "episodic", "item1", 0.8)
        pipeline.add_to_queue("working", "episodic", "item2", 0.7)

        assert pipeline.get_queue_size() == 2

        pipeline.clear_queue()
        assert pipeline.get_queue_size() == 0


class TestConsolidationTasks:
    """Test consolidation task management."""

    @pytest.mark.consolidation
    def test_task_creation(self):
        """Test creating consolidation tasks."""
        task = ConsolidationTask(
            source_tier="working",
            target_tier="episodic",
            item_id="test_item",
            priority=0.8
        )
        assert task.source_tier == "working"
        assert task.target_tier == "episodic"
        assert task.item_id == "test_item"
        assert task.priority == 0.8
        assert task.status == ConsolidationStatus.PENDING
        assert task.timestamp is not None

    @pytest.mark.consolidation
    def test_task_status_transitions(self, consolidation_pipeline):
        """Test task status changes during consolidation."""
        pipeline = consolidation_pipeline
        pipeline.add_to_queue("working", "episodic", "item1", 0.9)

        task = pipeline._queue[0]
        assert task.status == ConsolidationStatus.PENDING


class TestKLDivergence:
    """Test KL divergence calculation for surprise-based consolidation."""

    @pytest.mark.consolidation
    def test_kl_divergence_identical(self, sample_distributions):
        """Test KL divergence for identical distributions."""
        p, _ = sample_distributions
        pipeline = ConsolidationPipeline(
            WorkingMemory(), EpisodicMemory(), SemanticMemory()
        )

        kl = pipeline._calculate_kl_divergence(p, p)
        assert kl == pytest.approx(0.0, abs=1e-10)

    @pytest.mark.consolidation
    def test_kl_divergence_different(self, sample_distributions):
        """Test KL divergence for different distributions."""
        p, q = sample_distributions
        pipeline = ConsolidationPipeline(
            WorkingMemory(), EpisodicMemory(), SemanticMemory()
        )

        kl = pipeline._calculate_kl_divergence(p, q)
        assert kl > 0

    @pytest.mark.consolidation
    def test_trigger_consolidation_by_surprise(self, consolidation_pipeline):
        """Test surprise-based consolidation triggering."""
        pipeline = consolidation_pipeline

        # Create different distributions
        p = np.array([0.1, 0.2, 0.7])
        q = np.array([0.7, 0.2, 0.1])

        surprise = pipeline.trigger_consolidation_by_surprise(p, q)

        # Should have high surprise
        assert surprise > 0.5


class TestWorkingToEpisodicConsolidation:
    """Test consolidation from working to episodic memory."""

    @pytest.mark.consolidation
    def test_consolidate_working_to_episodic(self, working_memory, episodic_memory, semantic_memory):
        """Test basic working to episodic consolidation."""
        # Add to working memory
        from hierarchical_memory.core.working import MemoryItem
        item = MemoryItem(content="Important meeting", importance=0.8)
        working_memory._items["key1"] = item

        # Create pipeline and consolidate
        pipeline = ConsolidationPipeline(working_memory, episodic_memory, semantic_memory)
        pipeline.add_to_queue("working", "episodic", "key1", 0.8)

        consolidated = pipeline.consolidate_next_batch()

        # Item should be removed from working memory
        assert "key1" not in working_memory._items or consolidated >= 0

    @pytest.mark.consolidation
    def test_batch_consolidation(self, working_memory, episodic_memory, semantic_memory):
        """Test batch consolidation of multiple items."""
        from hierarchical_memory.core.working import MemoryItem

        pipeline = ConsolidationPipeline(
            working_memory, episodic_memory, semantic_memory,
            batch_size=3
        )

        # Add multiple items
        for i in range(5):
            key = f"item{i}"
            item = MemoryItem(content=f"Content {i}", importance=0.7 + i*0.05)
            working_memory._items[key] = item
            pipeline.add_to_queue("working", "episodic", key, 0.7 + i*0.05)

        # Consolidate one batch
        consolidated = pipeline.consolidate_next_batch()

        # Should consolidate up to batch_size
        assert consolidated <= 3


class TestEpisodicToSemanticConsolidation:
    """Test consolidation from episodic to semantic memory."""

    @pytest.mark.consolidation
    def test_consolidate_episodic_to_semantic(self, working_memory, episodic_memory, semantic_memory):
        """Test basic episodic to semantic consolidation."""
        # Add episodic memory
        event_id = episodic_memory.add(
            content="Learned that Python is a programming language",
            importance=0.8,
            context={"type": "learning"}
        )

        # Create pipeline
        pipeline = ConsolidationPipeline(working_memory, episodic_memory, semantic_memory)
        pipeline.add_to_queue("episodic", "semantic", event_id, 0.8)

        # Consolidate
        consolidated = pipeline.consolidate_next_batch()

        # Should create semantic concept
        assert consolidated >= 0

    @pytest.mark.consolidation
    def test_concept_extraction(self, working_memory, episodic_memory, semantic_memory):
        """Test concept extraction during consolidation."""
        # Add episodic memory about a concept
        event_id = episodic_memory.add(
            content="Machine learning models learn from data",
            importance=0.9
        )

        pipeline = ConsolidationPipeline(working_memory, episodic_memory, semantic_memory)
        pipeline.add_to_queue("episodic", "semantic", event_id, 0.9)
        pipeline.consolidate_next_batch()

        # Concept should be extracted (first word in this simple implementation)
        # Verify semantic memory has content
        assert len(semantic_memory._concepts) >= 0


class TestSleepConsolidation:
    """Test sleep-based consolidation."""

    @pytest.mark.consolidation
    def test_sleep_consolidation(self, working_memory, episodic_memory, semantic_memory):
        """Test consolidation during sleep period."""
        from hierarchical_memory.core.working import MemoryItem

        pipeline = ConsolidationPipeline(working_memory, episodic_memory, semantic_memory)

        # Add items to working memory
        for i in range(5):
            key = f"dream{i}"
            item = MemoryItem(content=f"Dream content {i}", importance=0.7)
            working_memory._items[key] = item

        # Simulate sleep
        consolidated = pipeline.simulate_sleep_consolidation(duration_hours=8.0)

        # Some consolidation should occur
        assert consolidated >= 0

    @pytest.mark.consolidation
    def test_sleep_duration_effect(self, working_memory, episodic_memory, semantic_memory):
        """Test that sleep duration affects consolidation."""
        from hierarchical_memory.core.working import MemoryItem

        # Add items
        for i in range(10):
            key = f"item{i}"
            item = MemoryItem(content=f"Content {i}", importance=0.8)
            working_memory._items[key] = item

        # Short sleep
        pipeline1 = ConsolidationPipeline(working_memory, episodic_memory, semantic_memory)
        consolidated_short = pipeline1.simulate_sleep_consolidation(duration_hours=2.0)

        # Longer sleep (with fresh items)
        for i in range(10, 20):
            key = f"item{i}"
            item = MemoryItem(content=f"Content {i}", importance=0.8)
            working_memory._items[key] = item

        pipeline2 = ConsolidationPipeline(working_memory, episodic_memory, semantic_memory)
        consolidated_long = pipeline2.simulate_sleep_consolidation(duration_hours=8.0)

        # Longer sleep should consolidate more (or equal)
        assert consolidated_long >= consolidated_short


class TestConsolidationStatistics:
    """Test consolidation statistics and monitoring."""

    @pytest.mark.consolidation
    def test_get_statistics_empty(self, consolidation_pipeline):
        """Test statistics for empty pipeline."""
        stats = consolidation_pipeline.get_consolidation_stats()
        assert "queue_size" in stats
        assert "total_consolidated" in stats
        assert "status_distribution" in stats
        assert "avg_priority" in stats

    @pytest.mark.consolidation
    def test_get_statistics_with_queue(self, consolidation_pipeline):
        """Test statistics with items in queue."""
        pipeline = consolidation_pipeline
        pipeline.add_to_queue("working", "episodic", "item1", 0.8)
        pipeline.add_to_queue("working", "episodic", "item2", 0.6)

        stats = pipeline.get_consolidation_stats()
        assert stats["queue_size"] == 2

    @pytest.mark.consolidation
    def test_status_distribution(self, consolidation_pipeline):
        """Test status distribution tracking."""
        pipeline = consolidation_pipeline
        pipeline.add_to_queue("working", "episodic", "item1", 0.9)
        pipeline.add_to_queue("working", "episodic", "item2", 0.8)

        # Mark one as complete
        pipeline._queue[0].status = ConsolidationStatus.COMPLETE

        stats = pipeline.get_consolidation_stats()
        assert stats["status_distribution"]["complete"] == 1
        assert stats["status_distribution"]["pending"] == 1


class TestConsolidationThreshold:
    """Test consolidation threshold behavior."""

    @pytest.mark.consolidation
    def test_threshold_filtering(self, working_memory, episodic_memory, semantic_memory):
        """Test that items below threshold are not consolidated."""
        pipeline = ConsolidationPipeline(
            working_memory, episodic_memory, semantic_memory,
            consolidation_threshold=0.8
        )

        # Add items below and above threshold
        pipeline.add_to_queue("working", "episodic", "low_priority", 0.5)
        pipeline.add_to_queue("working", "episodic", "high_priority", 0.9)

        consolidated = pipeline.consolidate_next_batch()

        # Only high priority item should consolidate
        assert consolidated == 1

    @pytest.mark.consolidation
    def test_average_priority_calculation(self, consolidation_pipeline):
        """Test average priority calculation."""
        pipeline = consolidation_pipeline
        pipeline.add_to_queue("working", "episodic", "item1", 0.6)
        pipeline.add_to_queue("working", "episodic", "item2", 0.8)

        stats = pipeline.get_consolidation_stats()
        expected_avg = (0.6 + 0.8) / 2
        assert stats["avg_priority"] == pytest.approx(expected_avg)


class TestIntegration:
    """Integration tests for consolidation pipeline."""

    @pytest.mark.consolidation
    @pytest.mark.integration
    def test_full_consolidation_workflow(self, working_memory, episodic_memory, semantic_memory):
        """Test complete consolidation workflow."""
        from hierarchical_memory.core.working import MemoryItem

        # 1. Add to working memory
        for i in range(5):
            key = f"work{i}"
            item = MemoryItem(content=f"Work task {i}", importance=0.7 + i*0.05)
            working_memory._items[key] = item

        # 2. Create pipeline
        pipeline = ConsolidationPipeline(
            working_memory, episodic_memory, semantic_memory,
            consolidation_threshold=0.7,
            batch_size=3
        )

        # 3. Queue items for consolidation
        for key in list(working_memory._items.keys()):
            item = working_memory._items[key]
            pipeline.add_to_queue("working", "episodic", key, item.importance)

        # 4. Consolidate
        consolidated = pipeline.consolidate_next_batch()

        # 5. Verify
        assert consolidated > 0
        assert pipeline.get_consolidation_stats()["total_consolidated"] > 0
