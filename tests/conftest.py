"""
Shared pytest configuration and fixtures
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List
import numpy as np

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from hierarchical_memory.working_memory import WorkingMemory
from hierarchical_memory.episodic_memory import EpisodicMemory
from hierarchical_memory.semantic_memory import SemanticMemory
from hierarchical_memory.procedural_memory import ProceduralMemory
from hierarchical_memory.consolidation.pipeline import ConsolidationPipeline
from hierarchical_memory.retrieval.search import MemoryRetrieval
from hierarchical_memory.sharing.protocol import MemorySharing, AgentPack


# =============================================================================
# Working Memory Fixtures
# =============================================================================

@pytest.fixture
def working_memory():
    """Fresh working memory instance with default capacity."""
    return WorkingMemory(capacity=20, decay_minutes=30)


@pytest.fixture
def small_working_memory():
    """Working memory with small capacity for testing eviction."""
    return WorkingMemory(capacity=5, decay_minutes=30)


@pytest.fixture
def populated_working_memory(working_memory):
    """Working memory populated with test data."""
    test_data = [
        ("Task 1: Complete documentation", 8.0, 0.5),
        ("Meeting with team at 2pm", 7.0, 0.0),
        ("Buy groceries", 5.0, -0.2),
        ("Call mom for birthday", 9.0, 0.8),
        ("Review pull request #123", 6.0, 0.1),
        ("Update dependencies", 4.0, 0.0),
        ("Prepare presentation", 7.5, 0.3),
    ]
    memories = []
    for content, importance, emotion in test_data:
        mem = working_memory.add(content, importance, emotion)
        memories.append(mem)
    return working_memory, memories


# =============================================================================
# Episodic Memory Fixtures
# =============================================================================

@pytest.fixture
def episodic_memory():
    """Fresh episodic memory instance."""
    return EpisodicMemory()


@pytest.fixture
def populated_episodic_memory(episodic_memory):
    """Episodic memory populated with test data."""
    base_time = datetime.now() - timedelta(days=7)
    test_events = [
        ("Summer vacation in Hawaii", 9.0, 0.9, ["family", "friends"], "Hawaii", base_time),
        ("Graduation ceremony", 10.0, 0.95, ["family", "teachers"], "University", base_time + timedelta(days=1)),
        ("First job interview", 8.0, -0.3, ["interviewer"], "Office", base_time + timedelta(days=2)),
        ("Birthday party", 7.0, 0.7, ["friends"], "Home", base_time + timedelta(days=3)),
        ("Car accident", 9.5, -0.9, ["police", "other driver"], "Highway", base_time + timedelta(days=4)),
        ("Learned to play guitar", 6.0, 0.5, ["teacher"], "Music School", base_time + timedelta(days=5)),
        ("Moved to new city", 8.5, 0.0, ["movers"], "Apartment", base_time + timedelta(days=6)),
    ]
    memories = []
    for content, importance, emotion, participants, location, timestamp in test_events:
        mem = episodic_memory.store(
            content=content,
            importance=importance,
            emotional_valence=emotion,
            participants=participants,
            location=location,
            timestamp=timestamp
        )
        memories.append(mem)
    return episodic_memory, memories


# =============================================================================
# Semantic Memory Fixtures
# =============================================================================

@pytest.fixture
def semantic_memory():
    """Fresh semantic memory instance."""
    return SemanticMemory()


@pytest.fixture
def populated_semantic_memory(semantic_memory):
    """Semantic memory populated with test data."""
    test_concepts = [
        ("Python", "High-level programming language", 9.0, None),
        ("Machine Learning", "AI subset that learns from data", 8.0, "Artificial Intelligence"),
        ("Neural Network", "Computing architecture inspired by biological neurons", 8.0, "Machine Learning"),
        ("Algorithm", "Step-by-step procedure for solving problems", 7.0, None),
        ("Database", "Organized collection of structured data", 7.0, None),
    ]
    memories = []
    for concept, definition, importance, parent in test_concepts:
        mem = semantic_memory.store_concept(concept, definition, importance, parent)
        memories.append(mem)

    test_facts = [
        ("Python was created by Guido van Rossum", 1.0),
        ("Earth orbits around the Sun", 1.0),
        ("Water boils at 100 degrees Celsius at sea level", 0.95),
    ]
    for fact, confidence in test_facts:
        mem = semantic_memory.store_fact(fact, confidence)
        memories.append(mem)

    return semantic_memory, memories


# =============================================================================
# Procedural Memory Fixtures
# =============================================================================

@pytest.fixture
def procedural_memory():
    """Fresh procedural memory instance."""
    return ProceduralMemory()


@pytest.fixture
def populated_procedural_memory(procedural_memory):
    """Procedural memory populated with test skills."""
    test_skills = [
        ("Python Programming", "Write and debug Python code", 0.8, None),
        ("Public Speaking", "Deliver presentations to audiences", 0.6, None),
        ("Data Analysis", "Analyze and visualize data", 0.7, ["Python Programming"]),
        ("Machine Learning", "Build and train ML models", 0.4, ["Python Programming", "Data Analysis"]),
        ("Cooking", "Prepare meals", 0.9, None),
    ]
    memories = []
    for name, description, mastery, deps in test_skills:
        mem = procedural_memory.learn_skill(name, description, mastery, deps)
        memories.append(mem)
    return procedural_memory, memories


# =============================================================================
# Consolidation Pipeline Fixtures
# =============================================================================

@pytest.fixture
def consolidation_pipeline(working_memory, episodic_memory, semantic_memory):
    """Consolidation pipeline with all memory systems."""
    return ConsolidationPipeline(
        working_memory=working_memory,
        episodic_memory=episodic_memory,
        semantic_memory=semantic_memory,
        consolidation_threshold=0.7,
        batch_size=10
    )


# =============================================================================
# Retrieval System Fixtures
# =============================================================================

@pytest.fixture
def memory_retrieval(working_memory, episodic_memory, semantic_memory, procedural_memory):
    """Memory retrieval system with all memory tiers."""
    return MemoryRetrieval(
        working_memory=working_memory,
        episodic_memory=episodic_memory,
        semantic_memory=semantic_memory,
        procedural_memory=procedural_memory,
        default_top_k=10
    )


@pytest.fixture
def populated_all_memory_systems(populated_working_memory, populated_episodic_memory,
                                 populated_semantic_memory, populated_procedural_memory):
    """All memory systems populated with test data."""
    working, _ = populated_working_memory
    episodic, _ = populated_episodic_memory
    semantic, _ = populated_semantic_memory
    procedural, _ = populated_procedural_memory
    return {
        "working": working,
        "episodic": episodic,
        "semantic": semantic,
        "procedural": procedural,
    }


# =============================================================================
# Memory Sharing Fixtures
# =============================================================================

@pytest.fixture
def agent_pack():
    """Test agent pack with multiple agents."""
    pack = AgentPack(pack_id="test_pack")
    members = ["agent_1", "agent_2", "agent_3", "agent_4"]
    for member in members:
        pack.add_member(member)
    # Set up trust relationships
    pack.set_trust("agent_1", "agent_2", 0.8)
    pack.set_trust("agent_1", "agent_3", 0.6)
    pack.set_trust("agent_2", "agent_3", 0.9)
    pack.set_trust("agent_3", "agent_4", 0.7)
    return pack


@pytest.fixture
def memory_sharing(agent_pack):
    """Memory sharing protocol with test pack."""
    return MemorySharing(
        pack=agent_pack,
        default_strategy=None,  # Will use default TRUST_BASED
        trust_threshold=0.5,
        enable_conflict_resolution=True
    )


# =============================================================================
# Test Data Fixtures
# =============================================================================

@pytest.fixture
def sample_texts():
    """Sample texts for testing."""
    return [
        "The quick brown fox jumps over the lazy dog",
        "Machine learning is a subset of artificial intelligence",
        "Python is a versatile programming language",
        "The Eiffel Tower is located in Paris",
        "Water consists of hydrogen and oxygen molecules",
    ]


@pytest.fixture
def sample_distributions():
    """Sample probability distributions for KL divergence tests."""
    np.random.seed(42)
    p = np.random.rand(10)
    q = np.random.rand(10)
    # Normalize
    p = p / p.sum()
    q = q / q.sum()
    return p, q


@pytest.fixture
def time_range():
    """Time range for temporal search tests."""
    end = datetime.now()
    start = end - timedelta(days=7)
    return start, end


# =============================================================================
# Helper Functions
# =============================================================================

@pytest.fixture
def assert_memory_valid():
    """Factory function to validate memory objects."""
    def _assert(memory, memory_type, has_content=True):
        assert memory is not None
        assert memory.memory_type == memory_type
        if has_content:
            assert len(memory.content) > 0
        assert memory.importance >= 0
        assert -1 <= memory.emotional_valence <= 1
        assert memory.timestamp is not None
    return _assert


# =============================================================================
# Test Configuration
# =============================================================================

def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "working: Working memory tests")
    config.addinivalue_line("markers", "episodic: Episodic memory tests")
    config.addinivalue_line("markers", "semantic: Semantic memory tests")
    config.addinivalue_line("markers", "procedural: Procedural memory tests")
    config.addinivalue_line("markers", "consolidation: Consolidation tests")
    config.addinivalue_line("markers", "retrieval: Retrieval tests")
    config.addinivalue_line("markers", "sharing: Memory sharing tests")


# =============================================================================
# Coverage Hooks
# =============================================================================

@pytest.fixture(autouse=True)
def reset_time(monkeypatch):
    """Reset time-related state for each test."""
    # This can be used to mock time if needed
    yield
