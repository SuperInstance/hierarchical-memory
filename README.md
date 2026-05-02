# hierarchical-memory

A four-tier memory architecture for AI agents, inspired by cognitive science. Working → Episodic → Semantic → Procedural, with automatic consolidation and multi-modal retrieval.

## Brand Line

> Hierarchical memory mirrors human cognition — four tiers from fast short-term to persistent knowledge, with trust-based sharing across the Cocapn fleet.

## Installation

```bash
pip install hierarchical-memory
```

Or from source:

```bash
git clone https://github.com/SuperInstance/hierarchical-memory.git
cd hierarchical-memory
pip install -e .
```

## Usage

```python
from hierarchical_memory import HierarchicalMemory

# Initialize the memory system
memory = HierarchicalMemory()

# Working memory - short-term storage
memory.working.add("task1", "Complete project report", importance=0.8)

# Episodic memory - events and experiences
memory.episodic.add("Discussed Q4 roadmap with team", emotional_valence=0.7)

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

**Four-Tier Memory System:**

| Tier | Capacity | Purpose | Access Time |
|------|----------|---------|-------------|
| Working Memory | 20 items | Short-term, priority-based eviction | O(1) |
| Episodic Memory | 1000 events | Autobiographical events, emotional tagging | O(n) |
| Semantic Memory | Unlimited | Concepts, vector embeddings, similarity search | O(n) |
| Procedural Memory | Unlimited | Skills, 6 mastery levels, practice-based | O(1) |

**Memory Flow:**
```
Working → Episodic → Semantic + Procedural
(short)   (events)    (knowledge)   (skills)
```

## Key Features

- **Working Memory**: Fast, capacity-limited with priority-based eviction and 30-min decay
- **Episodic Memory**: Time-stamped events with emotional valence (-1 to 1) and context
- **Semantic Memory**: Vector embeddings (384-dim) for similarity search across concepts
- **Procedural Memory**: 6 mastery levels from Novice to Master, practice-based improvement
- **Memory Consolidation**: Automatic transfer between tiers based on importance
- **Multi-Modal Retrieval**: Semantic, temporal, contextual, and hybrid search modes
- **Memory Sharing**: Pack-based sharing with trust-based filtering across agents

## Advanced Usage

```python
# Memory consolidation
consolidated = memory.consolidate(batch_size=10)

# Multi-modal retrieval
results = memory.search("", mode="temporal", start_time=time.time() - 86400)
results = memory.search("", mode="contextual", context_key="location", context_value="office")

# Multi-agent sharing
memory.initialize_sharing(pack_id="team_alpha", members=["agent1", "agent2"], strategy="trust_based", trust_threshold=0.7)
memory.sharing.share_memory(agent_id="agent1", content="Project deadline extended", memory_type="episodic", importance=0.9)
```

## Fleet Context

Part of the Cocapn fleet. Related repos:

- [iron-to-iron](https://github.com/SuperInstance/iron-to-iron) — I2I protocol for git-native agent-to-agent communication
- [plato-sdk](https://github.com/SuperInstance/plato-sdk) — SDK for PLATO room-based coordination
- [holodeck-core](https://github.com/SuperInstance/holodeck-core) — MUD engine for agent simulation and memory exploration
- [git-agent](https://github.com/SuperInstance/git-agent) — Autonomous Git-native agent framework

---
🦐 Cocapn fleet — lighthouse keeper architecture