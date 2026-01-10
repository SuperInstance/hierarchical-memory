# Hierarchical Memory System - Complete Documentation

**6-Tier Memory Architecture for AI Agents**

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Installation](#installation)
4. [API Reference](#api-reference)
5. [Usage Examples](#usage-examples)
6. [Memory Consolidation](#memory-consolidation)
7. [Advanced Topics](#advanced-topics)

---

## Overview

### What is Hierarchical Memory?

Hierarchical Memory is a Python library implementing a 6-tier memory architecture inspired by cognitive neuroscience. It enables AI agents to form, store, and consolidate memories in a way that mimics human memory systems.

### Key Features

- **6-Tier Hierarchy**: Working, Mid-Term, Long-Term, Episodic, Semantic, Procedural
- **Memory Consolidation**: Automatic episodic-to-semantic pattern extraction
- **Temporal Landmarks**: Detection of significant life events
- **Vector Search**: Optional semantic search via Qdrant
- **Identity Persistence**: Track personality stability
- **Autobiographical Narrative**: Generate coherent life stories

### Use Cases

- AI character development in games
- Chatbot memory systems
- Personal assistant memory
- Agent experience tracking
- Narrative generation systems

---

## Architecture

### Memory Tiers

```
┌────────────────────────────────────────────────────────────────┐
│                    MEMORY HIERARCHY                           │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  TEMPORAL (Time-based)                                        │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐              │
│  │ WORKING    │->│ MID-TERM   │->│ LONG-TERM  │              │
│  │ 0-1 hour   │  │ 1-6 hours  │  │ 1+ weeks   │              │
│  └────────────┘  └────────────┘  └────────────┘              │
│         │              │               │                      │
│         └──────────────┴───────────────┘                      │
│                          │                                     │
│                          v                                     │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │              CONSOLIDATION                              │  │
│  │         (Pattern Extraction)                            │  │
│  └─────────────────────────────────────────────────────────┘  │
│                          │                                     │
│                          v                                     │
│  FUNCTIONAL (Content-based)                                  │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐              │
│  │ EPISODIC   │  │ SEMANTIC   │  │ PROCEDURAL │              │
│  │ What/When  │  │ Patterns   │  │ Skills     │              │
│  └────────────┘  └────────────┘  └────────────┘              │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

### Consolidation Flow

```
NEW EXPERIENCE
      |
      v
WORKING MEMORY (LLM Context)
      |
      v (after 1 hour)
MID-TERM BUFFER (Session)
      |
      v (after importance threshold)
REFLECTION CONSOLIDATION
      |
      v (after 24 hours)
EPISODIC -> SEMANTIC EXTRACTION
      |
      v (after 7 days)
AUTOBIOGRAPHICAL NARRATIVE UPDATE
```

### Core Components

```
hierarchical_memory/
├── __init__.py           # Public API
├── core.py               # HierarchicalMemory class
├── consolidation.py      # ConsolidationEngine
├── vector_store.py       # VectorMemoryStore
├── identity.py           # IdentityPersistence
└── utils.py              # Helper functions
```

---

## Installation

### From PyPI

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

### From Source

```bash
git clone https://github.com/ws-fabric/hierarchical-memory
cd hierarchical-memory
pip install -e .
```

### Verify Installation

```python
from hierarchical_memory import HierarchicalMemory

memory = HierarchicalMemory(character_id="test")
print(memory.get_stats())
# Output: {'total_memories': 0, 'episodic': 0, ...}
```

---

## API Reference

### HierarchicalMemory

Main memory system class.

```python
from hierarchical_memory import HierarchicalMemory, MemoryType

memory = HierarchicalMemory(
    character_id="agent_001",
    storage_path="./memory/agent_001.json"
)
```

#### Constructor

```python
HierarchicalMemory(
    character_id: str,
    storage_path: Optional[Union[str, Path]] = None,
    config: Optional[Dict[str, Any]] = None
)
```

**Parameters:**
- `character_id`: Unique identifier for this agent
- `storage_path`: Path for persistent storage (None = in-memory)
- `config`: Configuration overrides

**Configuration Options:**
```python
{
    "max_working_memories": 10,          # Max working memories
    "max_mid_term_memories": 100,        # Max mid-term memories
    "recency_decay_rate": 0.995,        # Per hour decay
    "reflection_threshold": 150.0,       # Importance for reflection
    "consolidation_window_hours": 24,    # Hours between consolidation
    "temporal_landmark_threshold": 0.6,  # Score for landmark
}
```

#### Methods

##### store()

Store a new memory.

```python
store(
    content: str,
    memory_type: MemoryType = MemoryType.EPISODIC,
    importance: float = 5.0,
    emotional_valence: float = 0.0,
    participants: List[str] = None,
    location: str = ""
) -> Memory
```

**Parameters:**
- `content`: What happened/was learned
- `memory_type`: Type of memory (default: EPISODIC)
- `importance`: 1-10 importance score
- `emotional_valence`: -1 (bad) to +1 (good)
- `participants`: Who was involved
- `location`: Where it happened

**Returns:**
- `Memory`: The stored memory object

**Example:**
```python
memory.store(
    content="Met with the design team to discuss Q1 goals",
    memory_type=MemoryType.EPISODIC,
    importance=7.0,
    emotional_valence=0.5,
    participants=["Alice", "Bob"],
    location="Conference Room A"
)
```

##### retrieve()

Retrieve relevant memories with weighted scoring.

```python
retrieve(
    query: str,
    top_k: int = 10,
    alpha_recency: float = 1.0,
    alpha_importance: float = 1.0,
    alpha_relevance: float = 1.0
) -> List[Memory]
```

**Parameters:**
- `query`: Search query
- `top_k`: Maximum results
- `alpha_recency`: Weight for recency
- `alpha_importance`: Weight for importance
- `alpha_relevance`: Weight for semantic relevance

**Returns:**
- List of memories, ranked by combined score

**Scoring Formula:**
```
Score = (alpha_recency * Recency)
      + (alpha_importance * Importance)
      + (alpha_relevance * Similarity)
```

##### store_working()

Store to working memory (fast, temporary).

```python
store_working(content: str, **kwargs) -> Memory
```

##### store_episodic()

Store as episodic memory.

```python
store_episodic(
    content: str,
    importance: float = 5.0,
    **kwargs
) -> Memory
```

##### store_semantic()

Store as semantic memory.

```python
store_semantic(
    content: str,
    importance: float = 7.0,
    **kwargs
) -> Memory
```

##### get_recent()

Get recent memories.

```python
get_recent(hours: int = 24, top_k: int = 10) -> List[Memory]
```

##### get_important()

Get important memories.

```python
get_important(threshold: float = 7.0, top_k: int = 10) -> List[Memory]
```

##### generate_narrative()

Generate autobiographical narrative.

```python
generate_narrative() -> AutobiographicalNarrative
```

**Returns:**
- Narrative with themes, traits, coherence score

##### get_stats()

Get memory system statistics.

```python
get_stats() -> Dict[str, Any]
```

### MemoryType

Enum for memory tiers.

```python
class MemoryType(Enum):
    WORKING = "working"              # Current attention
    MID_TERM = "mid_term"            # Session buffer
    LONG_TERM = "long_term"          # Consolidated storage
    EPISODIC = "episodic"            # Specific events
    SEMANTIC = "semantic"            # Patterns & facts
    PROCEDURAL = "procedural"        # Skills & habits
```

### Memory

Individual memory unit.

```python
@dataclass
class Memory:
    id: str                           # Unique ID
    content: str                      # Memory content
    memory_type: MemoryType           # Type of memory
    timestamp: datetime               # When it occurred
    importance: float = 5.0           # 1-10 scale
    emotional_valence: float = 0.0    # -1 to +1
    participants: List[str]           # Who was involved
    location: str                     # Where it happened
    access_count: int = 0             # Times retrieved
    last_accessed: Optional[datetime] = None
    consolidated: bool = False        # Consolidated to semantic?
    is_temporal_landmark: bool = False
    landmark_type: Optional[str] = None
```

### AutobiographicalNarrative

Life story constructed from memories.

```python
@dataclass
class AutobiographicalNarrative:
    character_id: str
    narrative: str                    # Life story text
    key_themes: List[str]             # Main themes
    core_identity_traits: Dict[str, float]  # Personality traits
    generated_at: datetime
    memory_ids_used: List[str]
    coherence_score: float            # 0-1 coherence
```

---

## Usage Examples

### Basic Usage

```python
from hierarchical_memory import HierarchicalMemory

# Create memory system
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

memory.store_episodic(
    "Collaborated with design team on new UI",
    importance=6.5,
    emotional_valence=0.3,
    participants=["Design Team"]
)

# Retrieve relevant memories
results = memory.retrieve("team collaboration", top_k=5)

for mem in results:
    print(f"[{mem.importance:.1f}] {mem.content}")

# Output:
# [7.0] Met with the team to discuss Q1 goals
# [6.5] Collaborated with design team on new UI
```

### Memory Types

```python
from hierarchical_memory import HierarchicalMemory, MemoryType

memory = HierarchicalMemory("agent_001")

# Working memory (current focus)
memory.store_working("Currently reviewing deployment logs")

# Episodic (specific event)
memory.store_episodic(
    "Deployed to production on Tuesday",
    importance=8.0,
    location="Production Environment"
)

# Semantic (general knowledge)
memory.store_semantic(
    "I prefer small team collaboration over large meetings",
    importance=7.5
)

# Procedural (skill/habit)
memory.store(
    "Default to defensive programming in production code",
    memory_type=MemoryType.PROCEDURAL,
    importance=8.0
)
```

### Retrieval with Weights

```python
# Emphasize recency (recent memories rank higher)
recent = memory.retrieve("deployment", top_k=5,
                       alpha_recency=2.0,
                       alpha_importance=0.5,
                       alpha_relevance=1.0)

# Emphasize importance (important memories rank higher)
important = memory.retrieve("deployment", top_k=5,
                            alpha_recency=0.5,
                            alpha_importance=2.0,
                            alpha_relevance=1.0)

# Balanced retrieval
balanced = memory.retrieve("deployment", top_k=5,
                         alpha_recency=1.0,
                         alpha_importance=1.0,
                         alpha_relevance=1.0)
```

### Autobiographical Narrative

```python
# Generate life story
narrative = memory.generate_narrative()

print(narrative.narrative)
# Output:
# "I am an AI agent who has experienced collaboration with
#  various teams. My work has focused on technical projects,
#  particularly deployment and UI design. I value small team
#  collaboration and prefer defensive programming practices.
#  Key experiences include successful production deployments
#  and productive design sessions."

print(f"Themes: {narrative.key_themes}")
# Output: Themes: ['collaboration', 'deployment', 'design']

print(f"Traits: {narrative.core_identity_traits}")
# Output: Traits: {'collaborative': 0.82, 'careful': 0.75}
```

---

## Memory Consolidation

### ConsolidationEngine

Orchestrates memory consolidation strategies.

```python
from hierarchical_memory import (
    HierarchicalMemory,
    ConsolidationEngine
)

memory = HierarchicalMemory("agent_001")
engine = ConsolidationEngine()
```

### Reflection Consolidation

Immediate insights from recent experiences (triggered when importance accumulator reaches threshold).

```python
# Trigger reflection manually
result = engine.consolidate(
    memory_system=memory,
    strategy="reflection"
)

print(f"Reflection created: {result.reflection_id}")
print(f"Memories processed: {result.input_count}")
print(f"Semantic memories created: {result.output_count}")
```

### Episodic to Semantic

Pattern extraction from episodic memories.

```python
# Consolidate episodic memories into semantic knowledge
result = engine.consolidate(
    memory_system=memory,
    strategy="episodic_semantic"
)

print(f"Patterns found: {len(result.patterns)}")
for pattern in result.patterns:
    print(f"  - {pattern['semantic_memory'].content}")
    print(f"    From {len(pattern['source_memories'])} memories")
```

### Adaptive Consolidation

Self-timing consolidation based on memory load.

```python
result = engine.consolidate(
    memory_system=memory,
    strategy="adaptive"
)

print(f"Consolidation triggered: {result.triggered}")
print(f"Reason: {result.trigger_reason}")
```

### Consolidation Strategies

| Strategy | Trigger | Description |
|----------|---------|-------------|
| `reflection` | Importance >= 150 | Immediate insights from recent |
| `episodic_semantic` | 24+ hours | Pattern extraction |
| `cluster` | 3+ similar memories | TF-IDF clustering |
| `adaptive` | Memory load | Self-timing |
| `incremental` | Continuous | Small-batch ongoing |

---

## Advanced Topics

### Vector Search

Enable semantic search with Qdrant:

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

for result in results:
    print(f"{result.score:.2f}: {result.memory.content}")
```

### Identity Tracking

Track personality stability and detect drift:

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

# Check for drift
if identity.is_drift_warning():
    print(identity.get_reinforcement_prompt())

# Get full report
report = identity.get_report()
print(f"Coherence Index: {report.coherence_index:.2f}")
# >0.7: Healthy
# 0.4-0.7: Monitor
# <0.4: Intervention needed
```

### Custom Memory Types

```python
from hierarchical_memory import MemoryType

# Extend with custom types
class ExtendedMemoryType(MemoryType):
    DREAM = "dream"           # Dream experiences
    VISION = "vision"         # Prophetic visions
    PLAN = "plan"             # Future plans

# Use custom type
memory.store(
    "Dreamed of a flying dragon",
    memory_type=ExtendedMemoryType.DREAM,
    importance=8.0
)
```

### Persistence

```python
# Memory is automatically saved to storage_path
memory = HierarchicalMemory(
    character_id="agent_001",
    storage_path="./memory/agent_001.json"
)

# Force save
memory.save()

# Load existing memory
memory = HierarchicalMemory(
    character_id="agent_001",
    storage_path="./memory/agent_001.json"  # Loads if exists
)

# Export to JSON
memory.export("memory_backup.json")

# Import from JSON
memory.import_("memory_backup.json")
```

---

## Testing

```python
import pytest
from hierarchical_memory import HierarchicalMemory, MemoryType

def test_store_and_retrieve():
    memory = HierarchicalMemory("test")

    # Store memory
    mem = memory.store_episodic(
        "Test memory",
        importance=7.0
    )

    # Retrieve
    results = memory.retrieve("test", top_k=1)
    assert len(results) == 1
    assert results[0].content == "Test memory"

def test_consolidation():
    memory = HierarchicalMemory("test")

    # Store similar memories
    for i in range(3):
        memory.store_episodic(
            f"Team meeting {i}",
            importance=7.0
        )

    # Consolidate
    engine = ConsolidationEngine()
    result = engine.consolidate(memory, "episodic_semantic")

    assert result.output_count > 0
```

---

**Package Version:** 1.0.0
**Documentation Version:** 1.0.0
**Last Updated:** 2025-01-10
