"""
Test suite for Memory Sharing module.

Tests cover:
- Pack creation and management
- Memory sharing protocols
- Trust-based sharing
- Conflict resolution
- Access tracking
"""

import pytest
import time
from hierarchical_memory.sharing.protocol import (
    MemorySharing,
    AgentPack,
    SharedMemory,
    SharingStrategy
)


class TestAgentPackBasics:
    """Test agent pack functionality."""

    @pytest.mark.sharing
    def test_pack_initialization(self, agent_pack):
        """Test pack initialization."""
        pack = agent_pack
        assert pack.pack_id == "test_pack"
        assert len(pack.members) == 4

    @pytest.mark.sharing
    def test_add_member(self, agent_pack):
        """Test adding member to pack."""
        pack = agent_pack
        initial_count = len(pack.members)
        pack.add_member("new_agent")
        assert len(pack.members) == initial_count + 1

    @pytest.mark.sharing
    def test_trust_matrix(self, agent_pack):
        """Test trust relationships."""
        pack = agent_pack
        trust = pack.get_trust("agent_1", "agent_2")
        assert trust == 0.8

    @pytest.mark.sharing
    def test_set_trust(self, agent_pack):
        """Test setting trust level."""
        pack = agent_pack
        pack.set_trust("agent_1", "agent_2", 0.9)
        trust = pack.get_trust("agent_1", "agent_2")
        assert trust == 0.9

    @pytest.mark.sharing
    def test_trust_bounds(self, agent_pack):
        """Test that trust is bounded [0, 1]."""
        pack = agent_pack

        # Test upper bound
        pack.set_trust("agent_1", "agent_2", 1.5)
        assert pack.get_trust("agent_1", "agent_2") == 1.0

        # Test lower bound
        pack.set_trust("agent_1", "agent_2", -0.5)
        assert pack.get_trust("agent_1", "agent_2") == 0.0

    @pytest.mark.sharing
    def test_default_trust(self, agent_pack):
        """Test default trust for non-existent relationships."""
        pack = agent_pack
        trust = pack.get_trust("agent_1", "agent_99")
        assert trust == 0.5


class TestSharedMemory:
    """Test shared memory data structure."""

    @pytest.mark.sharing
    def test_shared_memory_creation(self):
        """Test creating shared memory."""
        memory = SharedMemory(
            content="Important observation",
            source_agent="agent_1",
            memory_type="episodic",
            importance=0.8
        )
        assert memory.content == "Important observation"
        assert memory.source_agent == "agent_1"
        assert memory.memory_type == "episodic"
        assert memory.importance == 0.8
        assert memory.timestamp is not None
        assert len(memory.shared_with) == 0

    @pytest.mark.sharing
    def test_shared_memory_with_recipients(self):
        """Test shared memory with specified recipients."""
        memory = SharedMemory(
            content="Shared knowledge",
            source_agent="agent_1",
            shared_with={"agent_2", "agent_3"}
        )
        assert len(memory.shared_with) == 2
        assert "agent_2" in memory.shared_with
        assert "agent_3" in memory.shared_with


class TestMemorySharingBasics:
    """Test basic memory sharing functionality."""

    @pytest.mark.sharing
    def test_share_memory(self, memory_sharing):
        """Test sharing a memory."""
        sharing = memory_sharing
        success = sharing.share_memory(
            agent_id="agent_1",
            content="Important fact",
            memory_type="semantic",
            importance=0.9
        )
        assert success is True
        assert len(sharing._shared_memories) == 1

    @pytest.mark.sharing
    def test_share_from_non_member(self, memory_sharing):
        """Test sharing from non-member agent."""
        sharing = memory_sharing
        success = sharing.share_memory(
            agent_id="non_member",
            content="Test",
            memory_type="episodic"
        )
        assert success is False

    @pytest.mark.sharing
    def test_share_memory_with_targets(self, memory_sharing):
        """Test selective sharing with specific targets."""
        sharing = memory_sharing
        success = sharing.share_memory(
            agent_id="agent_1",
            content="Secret message",
            memory_type="episodic",
            importance=0.7,
            strategy=SharingStrategy.SELECTIVE,
            target_agents=["agent_2"]
        )
        assert success is True

        # Check shared with
        shared = sharing._shared_memories[-1]
        assert "agent_2" in shared.shared_with
        assert "agent_3" not in shared.shared_with


class TestSharingStrategies:
    """Test different sharing strategies."""

    @pytest.mark.sharing
    def test_broadcast_strategy(self, memory_sharing):
        """Test broadcast sharing strategy."""
        sharing = memory_sharing
        success = sharing.share_memory(
            agent_id="agent_1",
            content="Public announcement",
            memory_type="episodic",
            importance=0.8,
            strategy=SharingStrategy.BROADCAST
        )
        assert success is True

        shared = sharing._shared_memories[-1]
        # Should share with all except self
        assert len(shared.shared_with) == len(sharing.pack.members) - 1

    @pytest.mark.sharing
    def test_selective_strategy(self, memory_sharing):
        """Test selective sharing strategy."""
        sharing = memory_sharing
        success = sharing.share_memory(
            agent_id="agent_1",
            content="Targeted message",
            memory_type="episodic",
            importance=0.7,
            strategy=SharingStrategy.SELECTIVE,
            target_agents=["agent_2", "agent_3"]
        )
        assert success is True

        shared = sharing._shared_memories[-1]
        assert shared.shared_with == {"agent_2", "agent_3"}

    @pytest.mark.sharing
    def test_trust_based_strategy(self, memory_sharing):
        """Test trust-based sharing strategy."""
        sharing = memory_sharing
        sharing.share_memory(
            agent_id="agent_1",
            content="Trusted information",
            memory_type="semantic",
            importance=0.9,
            strategy=SharingStrategy.TRUST_BASED
        )

        shared = sharing._shared_memories[-1]
        # agent_1 trusts agent_2 (0.8) and agent_3 (0.6), both above threshold 0.5
        # agent_4 not in trust matrix, defaults to 0.5
        assert len(shared.shared_with) >= 2

    @pytest.mark.sharing
    def test_query_based_strategy(self, memory_sharing):
        """Test query-based sharing strategy."""
        sharing = memory_sharing
        success = sharing.share_memory(
            agent_id="agent_1",
            content="On-demand information",
            memory_type="episodic",
            importance=0.6,
            strategy=SharingStrategy.QUERY_BASED
        )
        assert success is True

        shared = sharing._shared_memories[-1]
        # Query-based shouldn't auto-share
        assert len(shared.shared_with) == 0


class TestReceivingMemories:
    """Test receiving shared memories."""

    @pytest.mark.sharing
    def test_receive_shared_memories(self, memory_sharing):
        """Test receiving memories shared with an agent."""
        sharing = memory_sharing

        # Share memory with agent_2
        sharing.share_memory(
            agent_id="agent_1",
            content="For agent_2",
            memory_type="episodic",
            importance=0.8,
            target_agents=["agent_2"]
        )

        # Agent 2 receives
        received = sharing.receive_shared_memories("agent_2")
        assert len(received) == 1
        assert received[0].content == "For agent_2"

    @pytest.mark.sharing
    def test_receive_by_type(self, memory_sharing):
        """Test filtering received memories by type."""
        sharing = memory_sharing

        sharing.share_memory(
            agent_id="agent_1",
            content="Semantic fact",
            memory_type="semantic",
            importance=0.8,
            target_agents=["agent_2"]
        )
        sharing.share_memory(
            agent_id="agent_1",
            content="Episodic event",
            memory_type="episodic",
            importance=0.7,
            target_agents=["agent_2"]
        )

        # Receive only semantic
        received = sharing.receive_shared_memories("agent_2", memory_type="semantic")
        assert len(received) == 1
        assert received[0].memory_type == "semantic"

    @pytest.mark.sharing
    def test_receive_by_importance(self, memory_sharing):
        """Test filtering received memories by importance."""
        sharing = memory_sharing

        sharing.share_memory(
            agent_id="agent_1",
            content="Important",
            memory_type="episodic",
            importance=0.9,
            target_agents=["agent_2"]
        )
        sharing.share_memory(
            agent_id="agent_1",
            content="Less important",
            memory_type="episodic",
            importance=0.5,
            target_agents=["agent_2"]
        )

        # Receive only high importance
        received = sharing.receive_shared_memories("agent_2", min_importance=0.7)
        assert len(received) == 1
        assert received[0].importance >= 0.7


class TestQuerying:
    """Test querying shared memories."""

    @pytest.mark.sharing
    def test_query_memories(self, memory_sharing):
        """Test querying shared memories."""
        sharing = memory_sharing

        sharing.share_memory(
            agent_id="agent_1",
            content="Python programming is fun",
            memory_type="semantic",
            importance=0.8,
            target_agents=["agent_2"]
        )
        sharing.share_memory(
            agent_id="agent_1",
            content="Java programming is useful",
            memory_type="semantic",
            importance=0.7,
            target_agents=["agent_2"]
        )

        # Query for "programming"
        results = sharing.query_memories("agent_2", "programming", limit=10)
        assert len(results) == 2

    @pytest.mark.sharing
    def test_query_not_shared(self, memory_sharing):
        """Test querying memories not shared with agent."""
        sharing = memory_sharing

        sharing.share_memory(
            agent_id="agent_1",
            content="Secret",
            memory_type="episodic",
            importance=0.9,
            target_agents=["agent_3"]
        )

        # agent_2 didn't receive this
        results = sharing.query_memories("agent_2", "Secret")
        assert len(results) == 0


class TestConflictResolution:
    """Test memory conflict resolution."""

    @pytest.mark.sharing
    def test_resolve_conflict_by_importance(self, memory_sharing):
        """Test resolving conflicts by importance."""
        sharing = memory_sharing

        memory1 = SharedMemory(
            content="Version A",
            source_agent="agent_1",
            importance=0.7,
            memory_type="semantic"
        )
        memory2 = SharedMemory(
            content="Version B",
            source_agent="agent_2",
            importance=0.9,
            memory_type="semantic"
        )

        resolved = sharing.resolve_conflict(memory1, memory2)
        assert resolved == memory2  # Higher importance wins

    @pytest.mark.sharing
    def test_resolve_conflict_by_time(self, memory_sharing):
        """Test resolving conflicts by time when importance is equal."""
        sharing = memory_sharing

        memory1 = SharedMemory(
            content="Version A",
            source_agent="agent_1",
            importance=0.7,
            memory_type="semantic",
            timestamp=1000.0
        )
        memory2 = SharedMemory(
            content="Version B",
            source_agent="agent_2",
            importance=0.7,
            memory_type="semantic",
            timestamp=2000.0  # More recent
        )

        resolved = sharing.resolve_conflict(memory1, memory2)
        assert resolved == memory2  # More recent wins

    @pytest.mark.sharing
    def test_conflict_resolution_disabled(self, agent_pack):
        """Test behavior when conflict resolution is disabled."""
        sharing = MemorySharing(
            pack=agent_pack,
            enable_conflict_resolution=False
        )

        memory1 = SharedMemory(
            content="Version A",
            source_agent="agent_1",
            importance=0.7,
            memory_type="semantic"
        )
        memory2 = SharedMemory(
            content="Version B",
            source_agent="agent_2",
            importance=0.9,
            memory_type="semantic"
        )

        resolved = sharing.resolve_conflict(memory1, memory2)
        # Returns first when disabled
        assert resolved == memory1


class TestTrustUpdates:
    """Test trust level updates."""

    @pytest.mark.sharing
    def test_update_trust_positive(self, memory_sharing):
        """Test positive trust update."""
        sharing = memory_sharing
        initial_trust = sharing.pack.get_trust("agent_1", "agent_2")

        sharing.update_trust("agent_1", "agent_2", 0.2)
        new_trust = sharing.pack.get_trust("agent_1", "agent_2")

        assert new_trust == min(initial_trust + 0.2, 1.0)

    @pytest.mark.sharing
    def test_update_trust_negative(self, memory_sharing):
        """Test negative trust update."""
        sharing = memory_sharing
        sharing.pack.set_trust("agent_1", "agent_2", 0.8)

        sharing.update_trust("agent_1", "agent_2", -0.3)
        new_trust = sharing.pack.get_trust("agent_1", "agent_2")

        assert new_trust == 0.5


class TestAccessTracking:
    """Test memory access tracking."""

    @pytest.mark.sharing
    def test_access_logging(self, memory_sharing):
        """Test that access is logged."""
        sharing = memory_sharing

        sharing.share_memory(
            agent_id="agent_1",
            content="Logged memory",
            memory_type="episodic",
            importance=0.7,
            target_agents=["agent_2"]
        )

        sharing.receive_shared_memories("agent_2")

        logs = sharing.get_access_logs("agent_2")
        assert len(logs) > 0

    @pytest.mark.sharing
    def test_access_count_increments(self, memory_sharing):
        """Test that access count increments."""
        sharing = memory_sharing

        sharing.share_memory(
            agent_id="agent_1",
            content="Popular memory",
            memory_type="semantic",
            importance=0.8,
            target_agents=["agent_2"]
        )

        sharing.query_memories("agent_2", "Popular")
        sharing.query_memories("agent_2", "Popular")

        shared = sharing._shared_memories[0]
        assert shared.access_count == 2


class TestStatistics:
    """Test sharing statistics."""

    @pytest.mark.sharing
    def test_get_sharing_stats_empty(self, memory_sharing):
        """Test statistics for empty sharing."""
        sharing = memory_sharing
        stats = sharing.get_sharing_stats()
        assert "total_shared" in stats
        assert "memory_types" in stats
        assert "pack_members" in stats

    @pytest.mark.sharing
    def test_get_sharing_stats_populated(self, memory_sharing):
        """Test statistics after sharing."""
        sharing = memory_sharing

        sharing.share_memory(
            agent_id="agent_1",
            content="Memory 1",
            memory_type="semantic",
            importance=0.8
        )
        sharing.share_memory(
            agent_id="agent_2",
            content="Memory 2",
            memory_type="episodic",
            importance=0.7
        )

        stats = sharing.get_sharing_stats()
        assert stats["total_shared"] == 2
        assert "semantic" in stats["memory_types"]
        assert "episodic" in stats["memory_types"]


class TestIntegration:
    """Integration tests for memory sharing."""

    @pytest.mark.sharing
    @pytest.mark.integration
    def test_full_sharing_workflow(self, memory_sharing):
        """Test complete sharing workflow."""
        sharing = memory_sharing

        # Agent 1 shares important information
        sharing.share_memory(
            agent_id="agent_1",
            content="Critical discovery",
            memory_type="semantic",
            importance=0.95,
            strategy=SharingStrategy.TRUST_BASED
        )

        # Agent 2 receives it
        received = sharing.receive_shared_memories("agent_2")
        assert len(received) == 1

        # Agent 2 queries for it
        results = sharing.query_memories("agent_2", "discovery")
        assert len(results) == 1

        # Agent 2 updates trust based on quality
        sharing.update_trust("agent_2", "agent_1", 0.1)
        new_trust = sharing.pack.get_trust("agent_2", "agent_1")
        assert new_trust > 0.5

    @pytest.mark.sharing
    @pytest.mark.integration
    def test_multi_agent_information_spread(self, memory_sharing):
        """Test information spreading across multiple agents."""
        sharing = memory_sharing

        # Agent 1 broadcasts
        sharing.share_memory(
            agent_id="agent_1",
            content="News flash",
            memory_type="episodic",
            importance=0.8,
            strategy=SharingStrategy.BROADCAST
        )

        # Multiple agents should receive
        total_receives = 0
        for agent_id in ["agent_2", "agent_3", "agent_4"]:
            received = sharing.receive_shared_memories(agent_id)
            total_receives += len(received)

        assert total_receives > 0
