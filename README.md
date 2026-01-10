# Hierarchical Memory System

A 6-tier hierarchical memory architecture for AI agents, inspired by cognitive neuroscience and memory consolidation research.

## Features

- **6-Tier Memory Hierarchy**: Working, Mid-Term, Long-Term, Episodic, Semantic, and Procedural memory
- **Memory Consolidation**: Automatic episodic-to-semantic pattern extraction
- **Temporal Landmarks**: Automatic detection of significant life events
- **Vector Search**: Optional semantic search using Qdrant and sentence-transformers
- **Identity Persistence**: Track personality stability and detect identity drift
- **Autobiographical Narrative**: Generate coherent life stories from memories

## Installation

```bash
# Basic installation (no external dependencies)
pip install hierarchical-memory

# With vector database support
pip install hierarchical-memory[qdrant]

# With embedding models
pip install hierarchical-memory[embeddings]

# With all optional dependencies
pip install hierarchical-memory[all]
```

## Quick Start

```python
from hierarchical_memory import HierarchicalMemory

# Create a memory system
memory = HierarchicalMemory(
    character_id="agent_001",
    storage_path="./memory/agent_001.json"
)

# Store memories
memory.store_episodic(
    "Met with the team to discuss Q1 goals",
    importance=7.0,
    emotional_valence=0.5,
    participants=["Alice", "Bob"]
)

# Retrieve relevant memories
results = memory.retrieve("team meeting", top_k=5)
for mem in results:
    print(f"[{mem.importance:.1f}] {mem.content}")

# Generate autobiographical narrative
narrative = memory.generate_narrative()
print(narrative.narrative)
```

## Memory Tiers

| Tier | Description | Duration | Example |
|------|-------------|----------|---------|
| Working | Current attention | Seconds-minutes | "Currently reviewing deployment logs" |
| Mid-Term | Session buffer | 1-6 hours | "Working on the API refactor" |
| Long-Term | Consolidated storage | 1+ weeks | "I work at TechCorp as an engineer" |
| Episodic | Specific events | "What-where-when" | "Deployed to production on Tuesday" |
| Semantic | Facts & patterns | Abstract | "I prefer small team collaboration" |
| Procedural | Skills & habits | Knowing-how | "Default to defensive programming" |

## Memory Consolidation

The system automatically consolidates episodic memories into semantic knowledge:

```python
from hierarchical_memory import ConsolidationEngine

# Create consolidation engine
engine = ConsolidationEngine()

# Run consolidation
result = engine.consolidate(memory, strategy="episodic_semantic")

print(f"Consolidated {result.input_count} memories")
print(f"Created {result.output_count} semantic patterns")
```

### Consolidation Strategies

- `reflection`: Immediate insights from recent experiences
- `episodic_semantic`: Pattern extraction from episodic memories
- `cluster`: TF-IDF based clustering
- `adaptive`: Self-timing consolidation
- `incremental`: Small-batch continuous consolidation

## Vector Search

Enable semantic search across memories:

```python
from hierarchical_memory import VectorMemoryStore

# Create vector store
store = VectorMemoryStore(
    character_id="agent_001",
    qdrant_url="http://localhost:6333"
)

# Add memories
store.add_memory(
    "Collaborated with design team on new UI",
    importance=7.0
)

# Semantic search
results = store.search("teamwork", top_k=5)
```

## Identity Tracking

Track personality stability and detect identity drift:

```python
from hierarchical_memory import IdentityPersistence

# Define core traits
identity = IdentityPersistence(
    character_id="agent_001",
    core_traits={
        "openness": 0.7,
        "conscientiousness": 0.8,
        "extraversion": 0.6,
        "agreeableness": 0.7,
        "neuroticism": 0.3
    }
)

# Update from experiences
identity.update_from_experience(
    emotional_valence=0.5,
    social_context=True
)

# Check drift
if identity.is_drift_warning():
    print(identity.get_reinforcement_prompt())

# Get full report
report = identity.get_report()
print(f"Coherence Index: {report.coherence_index:.2f}")
```

## API Reference

### HierarchicalMemory

Main memory system class.

```python
memory = HierarchicalMemory(
    character_id: str,
    storage_path: Optional[str] = None,
    config: Optional[Dict] = None
)
```

**Methods:**
- `store(content, memory_type, importance, ...)` - Store a memory
- `store_working(content, **kwargs)` - Store in working memory
- `store_episodic(content, **kwargs)` - Store as episodic memory
- `store_semantic(content, **kwargs)` - Store as semantic memory
- `retrieve(query, top_k, **kwargs)` - Retrieve with weighted scoring
- `get_recent(hours, top_k)` - Get recent memories
- `get_important(threshold, top_k)` - Get important memories
- `generate_narrative()` - Generate autobiographical narrative
- `get_stats()` - Get system statistics

### MemoryType Enum

- `MemoryType.WORKING`
- `MemoryType.MID_TERM`
- `MemoryType.LONG_TERM`
- `MemoryType.EPISODIC`
- `MemoryType.SEMANTIC`
- `MemoryType.PROCEDURAL`

### ConsolidationEngine

Orchestrates consolidation strategies.

```python
engine = ConsolidationEngine()
result = engine.consolidate(
    memory_system,
    strategy="episodic_semantic",
    force=False
)
```

## Examples

See the `examples/` directory:

- `basic_usage.py` - Core functionality demonstration
- `vector_search_example.py` - Semantic search with vector store

Run examples:
```bash
python examples/basic_usage.py
python examples/vector_search_example.py
```

## Configuration

```python
memory = HierarchicalMemory(
    character_id="agent_001",
    config={
        "max_working_memories": 10,
        "max_mid_term_memories": 100,
        "recency_decay_rate": 0.995,
        "reflection_threshold": 150.0,
        "consolidation_window_hours": 24,
        "temporal_landmark_threshold": 0.6,
    }
)
```

## Architecture

```
hierarchical-memory/
+-- src/hierarchical_memory/
|   +-- __init__.py           # Package exports
|   +-- core.py               # Core memory system
|   +-- consolidation.py      # Consolidation strategies
|   +-- vector_store.py       # Vector search
|   +-- identity.py           # Identity persistence
+-- examples/
|   +-- basic_usage.py
|   +-- vector_search_example.py
+-- README.md
+-- pyproject.toml
```

## License

MIT

## Inspiration

This system is inspired by:
- **Atkinson-Shiffrin model** of memory formation
- **Standard consolidation theory** (hippocampus to neocortex)
- **Autobiographical memory** and temporal landmarks
- **Identity persistence** in AI systems

Extracted from the DMLog project.
