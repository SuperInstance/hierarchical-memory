"""
Test suite for Episodic Memory module.

Tests cover:
- CRUD operations for episodic events
- Temporal search
- Location-based search
- Participant search
- Emotional search
- Importance filtering
- Statistics and summaries
"""

import pytest
from datetime import datetime, timedelta
from hierarchical_memory.episodic_memory import EpisodicMemory
from hierarchical_memory.memory_types import MemoryType


class TestEpisodicMemoryBasics:
    """Test basic episodic memory functionality."""

    @pytest.mark.episodic
    def test_initialization(self, episodic_memory):
        """Test episodic memory initialization."""
        assert episodic_memory is not None
        assert len(episodic_memory) == 0

    @pytest.mark.episodic
    def test_store_memory(self, episodic_memory):
        """Test storing a basic episodic memory."""
        memory = episodic_memory.store(
            content="Went for a walk in the park",
            importance=7.0,
            emotional_valence=0.6
        )
        assert memory is not None
        assert memory.content == "Went for a walk in the park"
        assert memory.importance == 7.0
        assert memory.emotional_valence == 0.6
        assert memory.memory_type == MemoryType.EPISODIC
        assert len(episodic_memory) == 1

    @pytest.mark.episodic
    def test_store_with_context(self, episodic_memory):
        """Test storing memory with full context."""
        timestamp = datetime.now() - timedelta(days=1)
        memory = episodic_memory.store(
            content="Team meeting about project roadmap",
            importance=8.0,
            emotional_valence=0.3,
            participants=["Alice", "Bob", "Charlie"],
            location="Conference Room A",
            timestamp=timestamp
        )
        assert memory is not None
        assert memory.participants == ["Alice", "Bob", "Charlie"]
        assert memory.location == "Conference Room A"
        assert abs(memory.timestamp - timestamp) < timedelta(seconds=1)

    @pytest.mark.episodic
    def test_retrieve_by_id(self, episodic_memory):
        """Test retrieving memory by ID."""
        memory = episodic_memory.store("Test event", importance=5.0)
        retrieved = episodic_memory.retrieve(memory.id)
        assert retrieved is not None
        assert retrieved.id == memory.id
        assert retrieved.content == "Test event"

    @pytest.mark.episodic
    def test_retrieve_nonexistent(self, episodic_memory):
        """Test retrieving non-existent memory."""
        result = episodic_memory.retrieve("nonexistent_id")
        assert result is None

    @pytest.mark.episodic
    def test_access_count_increments(self, episodic_memory):
        """Test that access count increments."""
        memory = episodic_memory.store("Important event", importance=7.0)
        initial_count = memory.access_count

        episodic_memory.retrieve(memory.id)
        retrieved = episodic_memory.retrieve(memory.id)

        assert retrieved.access_count == initial_count + 2


class TestTemporalSearch:
    """Test time-based search functionality."""

    @pytest.mark.episodic
    def test_search_by_time_range(self, populated_episodic_memory):
        """Test searching within time range."""
        episodic, memories = populated_episodic_memory
        start = datetime.now() - timedelta(days=5)
        end = datetime.now() - timedelta(days=2)

        results = episodic.search_by_time(start_time=start, end_time=end, limit=10)
        assert len(results) > 0
        assert all(start <= m.timestamp <= end for m in results)

    @pytest.mark.episodic
    def test_search_recent_memories(self, populated_episodic_memory):
        """Test getting recent memories."""
        episodic, memories = populated_episodic_memory
        recent = episodic.get_recent(hours=48, limit=5)
        assert len(recent) <= 5

        cutoff = datetime.now() - timedelta(hours=48)
        assert all(m.timestamp >= cutoff for m in recent)

    @pytest.mark.episodic
    def test_search_without_time_range(self, episodic_memory):
        """Test search without time constraints."""
        for i in range(5):
            episodic_memory.store(f"Event {i}", importance=5.0)

        results = episodic_memory.search_by_time(limit=10)
        assert len(results) == 5

    @pytest.mark.episodic
    def test_time_ordering(self, populated_episodic_memory):
        """Test that results are ordered by time (most recent first)."""
        episodic, memories = populated_episodic_memory
        results = episodic.search_by_time(limit=10)
        
        for i in range(len(results) - 1):
            assert results[i].timestamp >= results[i+1].timestamp


class TestLocationSearch:
    """Test location-based search functionality."""

    @pytest.mark.episodic
    def test_search_by_location(self, populated_episodic_memory):
        """Test searching memories by location."""
        episodic, memories = populated_episodic_memory
        results = episodic.search_by_location("Hawaii", limit=10)
        assert len(results) > 0
        assert all(m.location == "Hawaii" for m in results)

    @pytest.mark.episodic
    def test_search_nonexistent_location(self, episodic_memory):
        """Test searching for memories at non-existent location."""
        results = episodic_memory.search_by_location("Moon", limit=10)
        assert len(results) == 0

    @pytest.mark.episodic
    def test_location_importance_ranking(self, populated_episodic_memory):
        """Test that location results are ranked by importance."""
        episodic, memories = populated_episodic_memory
        results = episodic.search_by_location("University", limit=10)
        
        for i in range(len(results) - 1):
            assert results[i].importance >= results[i+1].importance

    @pytest.mark.episodic
    def test_get_location_history(self, populated_episodic_memory):
        """Test getting location frequency statistics."""
        episodic, memories = populated_episodic_memory
        history = episodic.get_location_history()
        assert isinstance(history, dict)
        assert len(history) > 0
        
        # Check that counts are positive
        for location, count in history.items():
            assert count > 0


class TestParticipantSearch:
    """Test participant-based search functionality."""

    @pytest.mark.episodic
    def test_search_by_participant(self, populated_episodic_memory):
        """Test searching memories involving specific participants."""
        episodic, memories = populated_episodic_memory
        results = episodic.search_by_participants(["family"], limit=10)
        assert len(results) > 0
        assert all("family" in m.participants for m in results)

    @pytest.mark.episodic
    def test_search_multiple_participants(self, populated_episodic_memory):
        """Test searching with multiple participants."""
        episodic, memories = populated_episodic_memory
        results = episodic.search_by_participants(["family", "friends"], limit=10)
        assert len(results) > 0

    @pytest.mark.episodic
    def test_search_nonexistent_participant(self, episodic_memory):
        """Test searching for non-existent participant."""
        results = episodic_memory.search_by_participants(["Alien"], limit=10)
        assert len(results) == 0

    @pytest.mark.episodic
    def test_participant_network(self, populated_episodic_memory):
        """Test getting social network from memories."""
        episodic, memories = populated_episodic_memory
        network = episodic.get_participant_network()
        assert isinstance(network, dict)
        
        # If there are co-participants, check network structure
        if network:
            for person, connections in network.items():
                assert isinstance(connections, dict)
                for other, count in connections.items():
                    assert count > 0


class TestEmotionalSearch:
    """Test emotional-based search functionality."""

    @pytest.mark.episodic
    def test_search_positive_emotions(self, populated_episodic_memory):
        """Test searching for positive memories."""
        episodic, memories = populated_episodic_memory
        results = episodic.search_by_emotion(min_valence=0.5, limit=10)
        assert len(results) > 0
        assert all(m.emotional_valence >= 0.5 for m in results)

    @pytest.mark.episodic
    def test_search_negative_emotions(self, populated_episodic_memory):
        """Test searching for negative memories."""
        episodic, memories = populated_episodic_memory
        results = episodic.search_by_emotion(max_valence=-0.3, limit=10)
        assert len(results) > 0
        assert all(m.emotional_valence <= -0.3 for m in results)

    @pytest.mark.episodic
    def test_search_emotional_range(self, populated_episodic_memory):
        """Test searching within emotional range."""
        episodic, memories = populated_episodic_memory
        results = episodic.search_by_emotion(
            min_valence=-0.2,
            max_valence=0.3,
            limit=10
        )
        assert all(-0.2 <= m.emotional_valence <= 0.3 for m in results)

    @pytest.mark.episodic
    def test_emotional_ranking(self, populated_episodic_memory):
        """Test that emotional results are ranked by intensity."""
        episodic, memories = populated_episodic_memory
        results = episodic.search_by_emotion(min_valence=0.0, limit=10)
        
        for i in range(len(results) - 1):
            intensity_i = abs(results[i].emotional_valence)
            intensity_j = abs(results[i+1].emotional_valence)
            assert intensity_i >= intensity_j


class TestImportanceSearch:
    """Test importance-based search functionality."""

    @pytest.mark.episodic
    def test_search_by_importance(self, populated_episodic_memory):
        """Test searching memories above importance threshold."""
        episodic, memories = populated_episodic_memory
        results = episodic.search_by_importance(min_importance=8.0, limit=10)
        assert len(results) > 0
        assert all(m.importance >= 8.0 for m in results)

    @pytest.mark.episodic
    def test_importance_ranking(self, populated_episodic_memory):
        """Test that importance results are ranked by importance."""
        episodic, memories = populated_episodic_memory
        results = episodic.search_by_importance(min_importance=5.0, limit=10)
        
        for i in range(len(results) - 1):
            assert results[i].importance >= results[i+1].importance


class TestStatistics:
    """Test statistics and summaries."""

    @pytest.mark.episodic
    def test_get_statistics_empty(self, episodic_memory):
        """Test statistics for empty episodic memory."""
        stats = episodic_memory.get_statistics()
        assert stats["total_memories"] == 0
        assert stats["unique_locations"] == 0
        assert stats["unique_participants"] == 0

    @pytest.mark.episodic
    def test_get_statistics_populated(self, populated_episodic_memory):
        """Test statistics for populated episodic memory."""
        episodic, memories = populated_episodic_memory
        stats = episodic.get_statistics()
        assert stats["total_memories"] > 0
        assert stats["unique_locations"] > 0
        assert stats["unique_participants"] > 0

    @pytest.mark.episodic
    def test_emotional_summary(self, populated_episodic_memory):
        """Test emotional summary statistics."""
        episodic, memories = populated_episodic_memory
        summary = episodic.get_emotional_summary()
        assert summary["total_memories"] > 0
        assert "average_valence" in summary
        assert "positive_count" in summary
        assert "negative_count" in summary
        assert "neutral_count" in summary
        assert summary["positive_count"] + summary["negative_count"] + summary["neutral_count"] == summary["total_memories"]

    @pytest.mark.episodic
    def test_most_emotional_memories(self, populated_episodic_memory):
        """Test identification of most positive/negative memories."""
        episodic, memories = populated_episodic_memory
        summary = episodic.get_emotional_summary()
        assert summary["most_positive"] is not None
        assert summary["most_negative"] is not None


class TestEdgeCases:
    """Test edge cases and error handling."""

    @pytest.mark.episodic
    def test_empty_participants_list(self, episodic_memory):
        """Test storing memory with empty participants."""
        memory = episodic_memory.store(
            content="Solitary activity",
            importance=5.0,
            participants=[]
        )
        assert memory is not None
        assert memory.participants == []

    @pytest.mark.episodic
    def test_empty_location(self, episodic_memory):
        """Test storing memory with empty location."""
        memory = episodic_memory.store(
            content="Digital activity",
            importance=5.0,
            location=""
        )
        assert memory is not None
        assert memory.location == ""

    @pytest.mark.episodic
    def test_future_timestamp(self, episodic_memory):
        """Test storing memory with future timestamp."""
        future_time = datetime.now() + timedelta(days=1)
        memory = episodic_memory.store(
            content="Planned event",
            importance=5.0,
            timestamp=future_time
        )
        assert memory is not None

    @pytest.mark.episodic
    def test_very_long_content(self, episodic_memory):
        """Test storing very long memory content."""
        long_content = "A" * 10000
        memory = episodic_memory.store(long_content, importance=5.0)
        assert memory is not None
        assert len(memory.content) == 10000


class TestIntegration:
    """Integration tests for episodic memory."""

    @pytest.mark.episodic
    @pytest.mark.integration
    def test_complex_search_workflow(self, populated_episodic_memory):
        """Test complex multi-criteria search."""
        episodic, memories = populated_episodic_memory
        
        # Search for recent, positive, important memories
        recent = episodic.get_recent(hours=72, limit=20)
        positive = [m for m in recent if m.emotional_valence > 0.5]
        important = [m for m in positive if m.importance > 7.0]
        
        # Verify results
        assert len(important) >= 0
        for memory in important:
            assert memory.emotional_valence > 0.5
            assert memory.importance > 7.0

    @pytest.mark.episodic
    @pytest.mark.integration
    def test_autobiographical_timeline(self, populated_episodic_memory):
        """Test creating autobiographical timeline."""
        episodic, memories = populated_episodic_memory
        
        # Get all memories ordered by time
        all_memories = episodic.search_by_time(limit=100)
        
        # Verify chronological order
        for i in range(len(all_memories) - 1):
            assert all_memories[i].timestamp >= all_memories[i+1].timestamp
        
        # Verify all contexts are present
        locations = set(m.location for m in all_memories if m.location)
        participants = set()
        for m in all_memories:
            participants.update(m.participants)
        
        assert len(locations) > 0
        assert len(participants) > 0
