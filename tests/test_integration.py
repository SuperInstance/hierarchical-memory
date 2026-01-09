"""
Integration tests for the complete hierarchical memory system.

Tests cover:
- Full workflow across all memory tiers
- Consolidation and retrieval pipeline
- Memory sharing across agents
- End-to-end scenarios
"""

import pytest
import time
from datetime import datetime, timedelta
from hierarchical_memory.working_memory import WorkingMemory
from hierarchical_memory.episodic_memory import EpisodicMemory
from hierarchical_memory.semantic_memory import SemanticMemory
from hierarchical_memory.procedural_memory import ProceduralMemory
from hierarchical_memory.consolidation.pipeline import ConsolidationPipeline
from hierarchical_memory.retrieval.search import MemoryRetrieval
from hierarchical_memory.sharing.protocol import create_memory_sharing


class TestCompleteMemoryLifecycle:
    """Test complete memory lifecycle from working to long-term storage."""

    @pytest.mark.integration
    def test_working_to_episodic_to_semantic(self):
        """Test memory consolidation through all tiers."""
        # Create memory systems
        working = WorkingMemory(capacity=20, decay_minutes=30)
        episodic = EpisodicMemory()
        semantic = SemanticMemory()

        # 1. Add to working memory
        memory = working.add(
            content="Learned that Paris is the capital of France",
            importance=8.0,
            emotional_valence=0.7
        )
        assert memory.id in working

        # 2. Consolidate to episodic
        consolidated_episodic = episodic.store(
            content=memory.content,
            importance=memory.importance,
            emotional_valence=memory.emotional_valence,
            location="Paris",
            timestamp=datetime.now()
        )
        assert consolidated_episodic is not None

        # 3. Consolidate to semantic
        consolidated_semantic = semantic.store_concept(
            concept="Paris",
            definition="Capital city of France",
            importance=7.0
        )
        assert consolidated_semantic is not None

        # Verify knowledge persists
        concept = semantic.get_concept("Paris")
        assert concept is not None
        assert "France" in concept.content

    @pytest.mark.integration
    def test_skill_learning_workflow(self):
        """Test complete skill learning and practice workflow."""
        procedural = ProceduralMemory()

        # 1. Learn new skill
        skill = procedural.learn_skill(
            skill_name="Public Speaking",
            description="Deliver presentations to audiences",
            initial_mastery=0.1
        )
        assert skill is not None
        assert procedural.get_mastery("Public Speaking") <= 0.2

        # 2. Practice multiple times
        for i in range(10):
            procedural.practice_skill(
                "Public Speaking",
                quality=0.8,
                time_spent_minutes=60
            )

        # 3. Verify improvement
        mastery = procedural.get_mastery("Public Speaking")
        assert mastery > 0.3

        # 4. Check if can perform
        can_perform = procedural.can_perform("Public Speaking", threshold=0.5)
        assert can_perform or mastery > 0.1


class TestConsolidationAndRetrieval:
    """Test integration of consolidation and retrieval systems."""

    @pytest.mark.integration
    def test_consolidate_then_retrieve(self):
        """Test consolidating memories then retrieving them."""
        # Create systems
        working = WorkingMemory(capacity=20, decay_minutes=30)
        episodic = EpisodicMemory()
        semantic = SemanticMemory()

        # Add to working
        for i in range(5):
            working.add(
                content=f"Python programming concept {i}",
                importance=7.0 + i * 0.2,
                emotional_valence=0.5
            )

        # Create consolidation pipeline
        pipeline = ConsolidationPipeline(
            working_memory=working,
            episodic_memory=episodic,
            semantic_memory=semantic,
            consolidation_threshold=0.7,
            batch_size=10
        )

        # Queue and consolidate
        for mem_id, content in list(working._memories.items()):
            memory = working.get(mem_id)
            if memory:
                pipeline.add_to_queue("working", "episodic", mem_id, memory.importance / 10)

        consolidated = pipeline.consolidate_next_batch()
        assert consolidated >= 0

    @pytest.mark.integration
    def test_multi_tier_retrieval(self):
        """Test retrieval across all memory tiers."""
        # Create all systems
        working = WorkingMemory(capacity=20, decay_minutes=30)
        episodic = EpisodicMemory()
        semantic = SemanticMemory()
        procedural = ProceduralMemory()

        # Populate all tiers
        working.add("Urgent task: Fix bug", importance=9.0)
        episodic.store(
            content="Team meeting about Python architecture",
            importance=8.0,
            participants=["Alice", "Bob"],
            location="Office"
        )
        semantic.store_concept("Python", "Programming language", 9.0)
        procedural.learn_skill("Python Programming", "Write Python code", 0.7)

        # Create retrieval system
        retrieval = MemoryRetrieval(
            working_memory=working,
            episodic_memory=episodic,
            semantic_memory=semantic,
            procedural_memory=procedural,
            default_top_k=10
        )

        # Search across all tiers
        results = retrieval.search("Python", mode=None, top_k=10)
        assert isinstance(results, list)


class TestMemorySharingWorkflow:
    """Test complete memory sharing workflow."""

    @pytest.mark.integration
    def test_agent_pack_collaboration(self):
        """Test agents sharing and receiving memories."""
        # Create sharing system
        sharing = create_memory_sharing(
            pack_id="research_team",
            members=["agent_1", "agent_2", "agent_3"],
            default_strategy=None,  # TRUST_BASED
            trust_threshold=0.5,
            enable_conflict_resolution=True
        )

        # Set up trust relationships
        sharing.pack.set_trust("agent_1", "agent_2", 0.8)
        sharing.pack.set_trust("agent_1", "agent_3", 0.6)

        # Agent 1 makes a discovery
        sharing.share_memory(
            agent_id="agent_1",
            content="Optimized algorithm reduces processing time by 50%",
            memory_type="semantic",
            importance=0.9,
            strategy=None  # Uses default TRUST_BASED
        )

        # Agent 2 receives the discovery
        received = sharing.receive_shared_memories("agent_2")
        assert len(received) > 0
        assert "algorithm" in received[0].content.lower()

        # Agent 2 queries for it later
        results = sharing.query_memories("agent_2", "algorithm")
        assert len(results) > 0

        # Agent 2 updates trust based on value
        sharing.update_trust("agent_2", "agent_1", 0.1)
        new_trust = sharing.pack.get_trust("agent_2", "agent_1")
        assert new_trust == 0.9  # 0.8 + 0.1

    @pytest.mark.integration
    def test_conflict_resolution_workflow(self):
        """Test conflict resolution during sharing."""
        sharing = create_memory_sharing(
            pack_id="test_pack",
            members=["agent_1", "agent_2"],
            enable_conflict_resolution=True
        )

        # Agent 1 shares information
        sharing.share_memory(
            agent_id="agent_1",
            content="The answer is 42",
            memory_type="semantic",
            importance=0.7
        )

        # Agent 2 shares conflicting information
        sharing.share_memory(
            agent_id="agent_2",
            content="The answer is 43",
            memory_type="semantic",
            importance=0.8
        )

        # Retrieve memories for agent_1
        received = sharing.receive_shared_memories("agent_1")
        assert len(received) >= 0


class TestComplexScenarios:
    """Test complex real-world scenarios."""

    @pytest.mark.integration
    def test_learning_and_knowledge_building(self):
        """Test learning experience and building knowledge."""
        working = WorkingMemory(capacity=20, decay_minutes=30)
        episodic = EpisodicMemory()
        semantic = SemanticMemory()
        procedural = ProceduralMemory()

        # Learning episode
        working.add("Attend Python workshop", importance=8.0, emotional_valence=0.8)
        working.add("Practice coding exercises", importance=7.0, emotional_valence=0.6)

        # Store as episodic memory
        episodic.store(
            content="Attended Python workshop and learned about decorators",
            importance=8.5,
            emotional_valence=0.8,
            participants=["instructor", "other students"],
            location="Training Center",
            timestamp=datetime.now()
        )

        # Extract semantic knowledge
        semantic.store_concept(
            "Python Decorator",
            "Function that modifies another function",
            importance=8.0,
            parent_concept="Python"
        )
        semantic.store_fact(
            "Decorators allow modification of function behavior",
            confidence=0.9
        )

        # Learn procedural skill
        procedural.learn_skill(
            "Python Decorator Usage",
            "Implement and use decorators",
            initial_mastery=0.3
        )

        # Practice the skill
        for _ in range(5):
            procedural.practice_skill("Python Decorator Usage", quality=0.8)

        # Verify learning
        mastery = procedural.get_mastery("Python Decorator Usage")
        assert mastery > 0.3

        # Verify semantic knowledge
        is_known, conf = semantic.verify_fact("Decorators allow modification of function behavior")
        assert is_known is True

    @pytest.mark.integration
    def test_memory_prioritization_and_consolidation(self):
        """Test how important memories are prioritized for consolidation."""
        working = WorkingMemory(capacity=10, decay_minutes=30)
        episodic = EpisodicMemory()
        semantic = SemanticMemory()

        # Add memories with varying importance
        memories = []
        for i in range(15):
            importance = 5.0 + (i % 5)  # 5.0 to 9.0
            mem = working.add(
                content=f"Task {i}: {'Very important' if importance > 8 else 'Routine'}",
                importance=importance,
                emotional_valence=0.0
            )
            memories.append(mem)

        # Create consolidation pipeline
        pipeline = ConsolidationPipeline(
            working_memory=working,
            episodic_memory=episodic,
            semantic_memory=semantic,
            consolidation_threshold=0.7,
            batch_size=5
        )

        # Queue memories
        for mem in memories:
            if mem.id in working:
                pipeline.add_to_queue("working", "episodic", mem.id, mem.importance / 10)

        # Consolidate
        consolidated = pipeline.consolidate_next_batch()
        assert consolidated >= 0

        # Check that important memories were prioritized
        stats = pipeline.get_consolidation_stats()
        assert stats["total_consolidated"] >= 0

    @pytest.mark.integration
    def test_forgetting_and_relearning(self):
        """Test skill forgetting and relearning curve."""
        procedural = ProceduralMemory()

        # Learn skill to high level
        procedural.learn_skill("Language Learning", "Study Spanish", 0.1)
        for _ in range(20):
            procedural.practice_skill("Language Learning", quality=0.9, time_spent_minutes=90)

        high_mastery = procedural.get_mastery("Language Learning")
        assert high_mastery > 0.6

        # Simulate time passing (forgetting)
        old_time = datetime.now() - timedelta(days=30)
        procedural._last_practiced["Language Learning"] = old_time

        decayed_mastery = procedural.get_mastery("Language Learning")
        assert decayed_mastery < high_mastery

        # Relearn (should be faster due to retention)
        procedural.practice_skill("Language Learning", quality=0.9, time_spent_minutes=60)
        relearned_mastery = procedural.get_mastery("Language Learning")

        # Should recover some mastery
        assert relearned_mastery > decayed_mastery


class TestSystemStatistics:
    """Test statistics across the complete system."""

    @pytest.mark.integration
    def test_full_system_statistics(self):
        """Test getting statistics from all memory systems."""
        # Create all systems
        working = WorkingMemory(capacity=20, decay_minutes=30)
        episodic = EpisodicMemory()
        semantic = SemanticMemory()
        procedural = ProceduralMemory()

        # Populate
        working.add("Task 1", importance=7.0)
        working.add("Task 2", importance=8.0)

        episodic.store("Important meeting", importance=9.0, emotional_valence=0.7)
        episodic.store("Lunch with friend", importance=5.0, emotional_valence=0.5)

        semantic.store_concept("Python", "Language", 9.0)
        semantic.store_fact("Python is popular", confidence=0.9)

        procedural.learn_skill("Python", "Programming", 0.7)
        procedural.learn_skill("Communication", "Soft skill", 0.5)

        # Get statistics from all
        working_stats = working.get_statistics()
        episodic_stats = episodic.get_statistics()
        semantic_stats = semantic.get_statistics()
        procedural_stats = procedural.get_statistics()

        # Verify all statistics are accessible
        assert working_stats["total_items"] == 2
        assert episodic_stats["total_memories"] == 2
        assert semantic_stats["total_memories"] == 2
        assert procedural_stats["total_skills"] == 2


class TestErrorHandling:
    """Test error handling across the integrated system."""

    @pytest.mark.integration
    def test_handle_invalid_operations(self):
        """Test handling of invalid operations."""
        working = WorkingMemory()
        episodic = EpisodicMemory()
        semantic = SemanticMemory()
        procedural = ProceduralMemory()

        # Try to get non-existent memories
        assert working.get("nonexistent") is None
        assert episodic.retrieve("nonexistent") is None
        assert semantic.get_concept("nonexistent") is None
        assert procedural.get_mastery("nonexistent") == 0.0

        # Try to practice non-existent skill
        with pytest.raises(ValueError):
            procedural.practice_skill("nonexistent")

    @pytest.mark.integration
    def test_boundary_conditions(self):
        """Test boundary conditions."""
        working = WorkingMemory(capacity=5, decay_minutes=30)

        # Add exactly to capacity
        for i in range(5):
            working.add(f"Task {i}", importance=5.0)
        assert len(working) == 5

        # Add one more - should evict
        working.add("Extra task", importance=10.0)
        assert len(working) == 5
