# Hierarchical Memory System

A comprehensive four-tier memory architecture for AI agents, inspired by human cognitive science.

## Overview

The Hierarchical Memory System implements a sophisticated, biologically-inspired memory architecture for AI agents. It provides four distinct memory tiers, each serving a specific purpose in information processing and storage, similar to how human memory works.

### Features

- **Working Memory**: Fast, capacity-limited short-term storage with priority-based eviction
- **Episodic Memory**: Autobiographical event storage with emotional tagging and temporal context
- **Semantic Memory**: General knowledge and concepts with vector embeddings for similarity search
- **Procedural Memory**: Skills and know-how with practice-based mastery progression
- **Memory Consolidation**: Automatic transfer of memories between tiers based on importance
- **Multi-Modal Retrieval**: Search across all memory tiers using semantic, temporal, and contextual modes
- **Memory Sharing**: Pack-based memory sharing between agents with trust-based filtering

## Installation

```bash
pip install hierarchical-memory
```

Or install from source:

```bash
git clone https://github.com/yourusername/hierarchical-memory.git
cd hierarchical-memory
pip install -e .
```

## Quick Start

```python
from hierarchical_memory import HierarchicalMemory

# Initialize the memory system
memory = HierarchicalMemory()

# Working memory - short-term storage
memory.working.add("task1", "Complete project report", importance=0.8)

# Episodic memory - events and experiences
memory.episodic.add(
    "Discussed Q4 roadmap with team",
    emotional_valence=0.7,
    importance=0.8,
    context={"location": "office"}
)

# Semantic memory - general knowledge
memory.semantic.add_concept("project", attributes={"type": "work", "priority": "high"})

# Procedural memory - skills
memory.procedural.add_skill("report writing", attributes={"difficulty": "medium"})

# Search across all memory tiers
results = memory.search("project", mode="semantic", top_k=5)

# Get system statistics
stats = memory.get_stats()
```

## Architecture

### Four-Tier Memory System

```
┌─────────────────────────────────────────────────────────┐
│                   Hierarchical Memory                    │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────────┐                                  │
│  │  Working Memory  │  ← Short-term, capacity-limited   │
│  │   (20 items)     │     Priority-based eviction       │
│  └────────┬─────────┘                                  │
│           │ Consolidation                              │
│           ▼                                            │
│  ┌──────────────────┐                                  │
│  │ Episodic Memory  │  ← Events, experiences            │
│  │   (1000 events)  │    Emotional tagging              │
│  └────────┬─────────┘    Temporal context               │
│           │ Consolidation                              │
│           ▼                                            │
│  ┌──────────────────┐                                  │
│  │ Semantic Memory  │  ← Concepts, knowledge            │
│  │  (unlimited)     │    Vector embeddings              │
│  └──────────────────┘    Similarity search              │
│                                                         │
│  ┌──────────────────┐                                  │
│  │Procedural Memory │  ← Skills, know-how              │
│  │  (unlimited)     │    Mastery levels                 │
│  └──────────────────┘    Practice-based improvement     │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Memory Tiers

#### 1. Working Memory
- **Capacity**: 20 items (configurable)
- **Decay**: 30-minute half-life
- **Features**:
  - Priority-based eviction
  - Importance boosting on access
  - Time-based decay

#### 2. Episodic Memory
- **Capacity**: 1000 events (configurable)
- **Features**:
  - Time-stamped events
  - Emotional valence (-1 to 1)
  - Contextual metadata
  - Importance scoring

#### 3. Semantic Memory
- **Capacity**: Unlimited
- **Features**:
  - Vector embeddings (384 dimensions)
  - Concept hierarchies
  - Similarity search
  - Attribute-based storage

#### 4. Procedural Memory
- **Capacity**: Unlimited
- **Features**:
  - 6 mastery levels (Novice to Master)
  - Practice-based improvement
  - Skill prerequisites
  - Success rate tracking

## Advanced Usage

### Memory Consolidation

```python
# Automatic consolidation during sleep/rest
consolidated = memory.consolidate(batch_size=10)

# Manual queuing for consolidation
memory.consolidation.add_to_queue(
    source_tier="working",
    target_tier="episodic",
    item_id="task1",
    priority=0.9
)
```

### Multi-Modal Retrieval

```python
# Semantic search
results = memory.search("project", mode="semantic", top_k=5)

# Temporal search (last 24 hours)
import time
results = memory.search(
    "",
    mode="temporal",
    start_time=time.time() - 86400,
    end_time=time.time()
)

# Contextual search
results = memory.search(
    "",
    mode="contextual",
    context_key="location",
    context_value="office"
)

# Hybrid search (combines multiple modes)
results = memory.search("project", mode="hybrid", top_k=5)
```

### Memory Sharing

```python
# Initialize sharing with agent pack
memory.initialize_sharing(
    pack_id="team_alpha",
    members=["agent1", "agent2", "agent3"],
    strategy="trust_based",
    trust_threshold=0.7
)

# Share a memory
memory.sharing.share_memory(
    agent_id="agent1",
    content="Project deadline extended",
    memory_type="episodic",
    importance=0.9
)

# Receive shared memories
shared = memory.sharing.receive_shared_memories("agent2")
```

### Procedural Skill Development

```python
# Add a skill with prerequisites
memory.procedural.add_skill(
    name="debugging",
    attributes={"category": "development"},
    prerequisites=["programming", "testing"]
)

# Practice the skill
for i in range(20):
    success = i > 5  # Improve over time
    memory.procedural.practice("debugging", success=success)

# Check mastery level
skill = memory.procedural.get_skill("debugging")
print(f"Mastery: {skill.mastery_name}")  # "Competent", "Expert", etc.
print(f"Success rate: {skill.success_rate:.1%}")
```

## Examples

See the `examples/` directory for comprehensive examples:

- `basic_usage.py` - Core functionality demonstration
- `memory_consolidation.py` - Consolidation pipeline usage
- `memory_sharing.py` - Multi-agent sharing
- `skill_development.py` - Procedural memory mastery

Run examples:

```bash
python examples/basic_usage.py
```

## Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_working_memory.py

# Run with coverage
pytest --cov=hierarchical_memory
```

## Performance Characteristics

| Tier | Capacity | Access Time | Decay |
|------|----------|-------------|-------|
| Working Memory | 20 items | O(1) | 30 min half-life |
| Episodic Memory | 1000 events | O(n) | Importance-based |
| Semantic Memory | Unlimited | O(n) | None |
| Procedural Memory | Unlimited | O(1) | None |

## Scientific Foundation

This memory system is based on established cognitive science research:

- **Working Memory**: Miller's "7±2" rule, refined by Cowan to "4±1"
- **Episodic Memory**: Tulving's theory of autobiographical memory
- **Semantic Memory**: Tulving's semantic memory framework
- **Consolidation**: Systems consolidation theory (hippocampus to neocortex)
- **Forgetting**: Ebbinghaus forgetting curve and decay theory

## Requirements

- Python 3.8+
- numpy
- Optional: sentence-transformers (for semantic embeddings)
- Optional: torch (for advanced features)
- Optional: faiss (for vector similarity search)

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please see CONTRIBUTING.md for guidelines.

## Citation

If you use this package in your research, please cite:

```bibtex
@software{hierarchical_memory,
  title={Hierarchical Memory System: A Four-Tier Architecture for AI Agents},
  author={LucidDreamer Team},
  year={2026},
  url={https://github.com/yourusername/hierarchical-memory}
}
```

## Acknowledgments

Inspired by cognitive science research on human memory:
- Miller, G. A. (1956). "The magical number seven, plus or minus two"
- Cowan, N. (2001). "The magical number 4 in short-term memory"
- Tulving, E. (1972). "Episodic and semantic memory"
- Squire, L. R. (2004). "Memory systems of the brain"

## Contact

- GitHub Issues: https://github.com/yourusername/hierarchical-memory/issues
- Email: contact@superinstance.ai
