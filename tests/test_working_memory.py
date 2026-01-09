"""
Test suite for Working Memory module.

Tests cover:
- Capacity limits and eviction
- Temporal decay
- CRUD operations
- Priority-based management
- Statistics and monitoring
"""

import pytest
from datetime import datetime, timedelta
from hierarchical_memory.working_memory import WorkingMemory
from hierarchical_memory.memory_types import MemoryType


class TestWorkingMemoryBasics:
    """Test basic working memory functionality."""

    @pytest.mark.working
    def test_initialization(self, working_memory):
        """Test working memory initialization with defaults."""
        assert working_memory.capacity == 20
        assert len(working_memory) == 0
        assert working_memory.decay_duration == timedelta(minutes=30)

    @pytest.mark.working
    def test_custom_initialization(self):
        """Test working memory with custom parameters."""
        wm = WorkingMemory(capacity=10, decay_minutes=60)
        assert wm.capacity == 10
        assert wm.decay_duration == timedelta(minutes=60)

    @pytest.mark.working
    def test_add_memory(self, working_memory):
        """Test adding a memory to working memory."""
        memory = working_memory.add(
            content="Test task",
            importance=7.0,
            emotional_valence=0.5
        )
        assert memory is not None
        assert memory.content == "Test task"
        assert memory.importance == 7.0
        assert memory.emotional_valence == 0.5
        assert memory.memory_type == MemoryType.WORKING
        assert len(working_memory) == 1

    @pytest.mark.working
    def test_add_multiple_memories(self, working_memory):
        """Test adding multiple memories."""
        for i in range(5):
            working_memory.add(f"Task {i}", importance=5.0 + i)
        assert len(working_memory) == 5

    @pytest.mark.working
    def test_get_memory(self, working_memory):
        """Test retrieving a memory by ID."""
        memory = working_memory.add("Important meeting", importance=8.0)
        retrieved = working_memory.get(memory.id)
        assert retrieved is not None
        assert retrieved.id == memory.id
        assert retrieved.content == "Important meeting"
        assert retrieved.access_count == 1

    @pytest.mark.working
    def test_get_nonexistent_memory(self, working_memory):
        """Test getting a memory that doesn't exist."""
        result = working_memory.get("nonexistent_id")
        assert result is None

    @pytest.mark.working
    def test_remove_memory(self, working_memory):
        """Test removing a memory."""
        memory = working_memory.add("Temporary task", importance=5.0)
        assert len(working_memory) == 1
        assert working_memory.remove(memory.id) is True
        assert len(working_memory) == 0

    @pytest.mark.working
    def test_remove_nonexistent_memory(self, working_memory):
        """Test removing a memory that doesn't exist."""
        assert working_memory.remove("nonexistent_id") is False

    @pytest.mark.working
    def test_update_memory(self, working_memory):
        """Test updating memory attributes."""
        memory = working_memory.add("Original content", importance=5.0)
        updated = working_memory.update(
            memory.id,
            content="Updated content",
            importance=8.0
        )
        assert updated is not None
        assert updated.content == "Updated content"
        assert updated.importance == 8.0

    @pytest.mark.working
    def test_clear_all_memories(self, populated_working_memory):
        """Test clearing all memories."""
        wm, _ = populated_working_memory
        assert len(wm) > 0
        wm.clear()
        assert len(wm) == 0


class TestCapacityAndEviction:
    """Test capacity limits and eviction behavior."""

    @pytest.mark.working
    def test_capacity_limit(self, small_working_memory):
        """Test that capacity is enforced."""
        wm = small_working_memory
        assert wm.capacity == 5

        # Add exactly capacity items
        for i in range(5):
            wm.add(f"Task {i}", importance=5.0)
        assert len(wm) == 5

        # Add one more - should evict lowest priority
        wm.add("High priority task", importance=10.0)
        assert len(wm) == 5  # Still at capacity

    @pytest.mark.working
    def test_eviction_by_importance(self, small_working_memory):
        """Test that lower importance items are evicted first."""
        wm = small_working_memory

        # Fill with low priority items
        low_priority_ids = []
        for i in range(4):
            mem = wm.add(f"Low priority {i}", importance=3.0)
            low_priority_ids.append(mem.id)

        # Add high priority item
        wm.add("High priority", importance=9.0)

        # Add another item - should evict a low priority one
        wm.add("Medium priority", importance=6.0)

        # Check that at least one low priority was evicted
        remaining_count = sum(1 for mid in low_priority_ids if mid in wm)
        assert remaining_count < 4

    @pytest.mark.working
    def test_eviction_by_access_count(self, small_working_memory):
        """Test that frequently accessed items are prioritized."""
        wm = small_working_memory

        # Fill to capacity
        memories = []
        for i in range(5):
            mem = wm.add(f"Task {i}", importance=5.0)
            memories.append(mem)

        # Access first memory multiple times
        for _ in range(5):
            wm.get(memories[0].id)

        # Add new memory with equal importance
        wm.add("New task", importance=5.0)

        # First memory should still be there (accessed frequently)
        assert memories[0].id in wm

    @pytest.mark.working
    def test_contains_operator(self, working_memory):
        """Test memory existence check with 'in' operator."""
        memory = working_memory.add("Test task", importance=5.0)
        assert memory.id in working_memory
        assert "nonexistent_id" not in working_memory

    @pytest.mark.working
    def test_length_operator(self, working_memory):
        """Test len() operator."""
        assert len(working_memory) == 0
        working_memory.add("Task 1", importance=5.0)
        assert len(working_memory) == 1
        working_memory.add("Task 2", importance=5.0)
        assert len(working_memory) == 2


class TestDecay:
    """Test temporal decay behavior."""

    @pytest.mark.working
    def test_get_decayed_memory(self, working_memory):
        """Test that decayed memories return None."""
        # Create working memory with very short decay
        wm = WorkingMemory(capacity=20, decay_minutes=0)
        memory = wm.add("Temporary task", importance=5.0)

        # Immediately check - should be decayed
        retrieved = wm.get(memory.id)
        assert retrieved is None or len(wm.get_all(decayed=False)) == 0

    @pytest.mark.working
    def test_get_all_with_decayed(self, populated_working_memory):
        """Test get_all with and without decayed memories."""
        wm, _ = populated_working_memory
        all_memories = wm.get_all(decayed=True)
        active_memories = wm.get_all(decayed=False)

        # With recent memories, all should be active
        assert len(all_memories) >= len(active_memories)

    @pytest.mark.working
    def test_cleanup_decayed(self, working_memory):
        """Test cleanup of decayed memories."""
        wm = WorkingMemory(capacity=20, decay_minutes=0)
        wm.add("Task 1", importance=5.0)
        wm.add("Task 2", importance=5.0)

        # Cleanup should remove decayed memories
        removed = wm.cleanup_decayed()
        assert removed >= 0
        assert len(wm) == 0


class TestPriorityAndAccess:
    """Test priority-based management and access tracking."""

    @pytest.mark.working
    def test_access_count_increments(self, working_memory):
        """Test that access count increments on retrieval."""
        memory = working_memory.add("Popular task", importance=5.0)
        assert memory.access_count == 1

        working_memory.get(memory.id)
        retrieved = working_memory.get(memory.id)
        assert retrieved.access_count == 3

    @pytest.mark.working
    def test_last_accessed_updated(self, working_memory):
        """Test that last_accessed timestamp is updated."""
        memory = working_memory.add("Task", importance=5.0)
        first_access = memory.last_accessed

        # Small delay to ensure timestamp difference
        import time
        time.sleep(0.01)

        working_memory.get(memory.id)
        retrieved = working_memory.get(memory.id)
        assert retrieved.last_accessed > first_access

    @pytest.mark.working
    def test_importance_range_validation(self, working_memory):
        """Test that importance scores are within valid range."""
        # Valid range
        wm = working_memory
        wm.add("Low importance", importance=1.0)
        wm.add("High importance", importance=10.0)

        # Edge cases
        wm.add("Edge low", importance=0.0)
        wm.add("Edge high", importance=10.0)

    @pytest.mark.working
    def test_emotional_valence_range(self, working_memory):
        """Test emotional valence is in valid range."""
        wm = working_memory
        wm.add("Positive memory", importance=5.0, emotional_valence=1.0)
        wm.add("Negative memory", importance=5.0, emotional_valence=-1.0)
        wm.add("Neutral memory", importance=5.0, emotional_valence=0.0)


class TestStatistics:
    """Test statistics and monitoring."""

    @pytest.mark.working
    def test_get_statistics_empty(self, working_memory):
        """Test statistics for empty working memory."""
        stats = working_memory.get_statistics()
        assert stats["total_items"] == 0
        assert stats["active_items"] == 0
        assert stats["capacity_utilization"] == 0.0
        assert stats["average_importance"] == 0.0

    @pytest.mark.working
    def test_get_statistics_populated(self, populated_working_memory):
        """Test statistics for populated working memory."""
        wm, memories = populated_working_memory
        stats = wm.get_statistics()

        assert stats["total_items"] > 0
        assert stats["active_items"] > 0
        assert stats["capacity_utilization"] > 0
        assert stats["average_importance"] > 0
        assert stats["total_accesses"] > 0

    @pytest.mark.working
    def test_capacity_utilization(self, small_working_memory):
        """Test capacity utilization calculation."""
        wm = small_working_memory
        assert wm.get_statistics()["capacity_utilization"] == 0.0

        # Add half capacity
        for i in range(2):
            wm.add(f"Task {i}", importance=5.0)
        stats = wm.get_statistics()
        assert stats["capacity_utilization"] == 0.4

        # Fill to capacity
        for i in range(3):
            wm.add(f"Task {i+2}", importance=5.0)
        stats = wm.get_statistics()
        assert stats["capacity_utilization"] == 1.0

    @pytest.mark.working
    def test_average_importance(self, working_memory):
        """Test average importance calculation."""
        wm = working_memory
        wm.add("Low", importance=2.0)
        wm.add("Medium", importance=5.0)
        wm.add("High", importance=8.0)

        stats = wm.get_statistics()
        expected_avg = (2.0 + 5.0 + 8.0) / 3
        assert abs(stats["average_importance"] - expected_avg) < 0.01


class TestEdgeCases:
    """Test edge cases and error handling."""

    @pytest.mark.working
    def test_empty_content(self, working_memory):
        """Test adding memory with empty content."""
        memory = working_memory.add("", importance=5.0)
        assert memory is not None
        assert memory.content == ""

    @pytest.mark.working
    def test_very_long_content(self, working_memory):
        """Test adding memory with very long content."""
        long_content = "A" * 10000
        memory = working_memory.add(long_content, importance=5.0)
        assert memory is not None
        assert len(memory.content) == 10000

    @pytest.mark.working
    def test_unicode_content(self, working_memory):
        """Test adding memory with unicode characters."""
        unicode_content = "Hello 世界 🌍 Привет"
        memory = working_memory.add(unicode_content, importance=5.0)
        assert memory is not None
        assert memory.content == unicode_content

    @pytest.mark.working
    def test_rapid_add_remove(self, working_memory):
        """Test rapid add/remove cycles."""
        ids = []
        for i in range(100):
            mem = working_memory.add(f"Task {i}", importance=5.0)
            ids.append(mem.id)

        # Should be at capacity, not 100
        assert len(working_memory) == working_memory.capacity

        # Remove all
        for mid in ids:
            if mid in working_memory:
                working_memory.remove(mid)

        assert len(working_memory) == 0

    @pytest.mark.working
    def test_extra_kwargs(self, working_memory):
        """Test adding memory with extra keyword arguments."""
        memory = working_memory.add(
            "Test task",
            importance=5.0,
            custom_field="custom_value",
            another_field=123
        )
        assert memory is not None


class TestIntegration:
    """Integration tests for working memory."""

    @pytest.mark.working
    @pytest.mark.integration
    def test_full_lifecycle(self, working_memory):
        """Test complete memory lifecycle."""
        # Add
        memory = working_memory.add("Lifecycle test", importance=7.0)
        assert memory.id in working_memory

        # Retrieve multiple times
        for _ in range(3):
            working_memory.get(memory.id)

        # Update
        working_memory.update(memory.id, importance=9.0)

        # Verify
        retrieved = working_memory.get(memory.id)
        assert retrieved.importance == 9.0
        assert retrieved.access_count >= 4

        # Remove
        assert working_memory.remove(memory.id) is True
        assert memory.id not in working_memory

    @pytest.mark.working
    @pytest.mark.integration
    def test_prioritization_workflow(self, small_working_memory):
        """Test realistic prioritization workflow."""
        wm = small_working_memory

        # Add tasks with varying importance
        tasks = [
            ("Check email", 3.0),
            ("Finish project", 10.0),
            ("Meeting prep", 7.0),
            ("Coffee break", 2.0),
            ("Code review", 6.0),
        ]

        for content, importance in tasks:
            wm.add(content, importance=importance)

        # Try to add urgent task - should evict lowest priority
        wm.add("URGENT: Server down", importance=10.0)

        # Verify important tasks are retained
        all_memories = wm.get_all()
        contents = [m.content for m in all_memories]
        assert "Finish project" in contents
        assert "URGENT: Server down" in contents

        # Lower priority tasks likely evicted
        assert len(contents) <= wm.capacity
