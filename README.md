# Hierarchical Memory

Hierarchical memory system for distributed agent fleets. Memory that organizes itself.

## Brand Line
> Trust-based memory sharing across agents with hierarchical context windows. Enables agents to share context without exposing raw data.

## Installation

```bash
pip install hierarchical-memory
```

## Usage

```python
from hierarchical_memory import HierarchicalMemory

memory = HierarchicalMemory(depth=4)
memory.store("context", {"important": "data"})
context = memory.retrieve("context")
```

## Fleet Context

Part of the Cocapn fleet. Related repos:
- **[plato-sdk](https://github.com/SuperInstance/plato-sdk)** — PLATO tile integration
- **[plato-server](https://github.com/SuperInstance/plato-server)** — Room server for knowledge
- **[iron-to-iron](https://github.com/SuperInstance/iron-to-iron)** — Git-based agent communication
- **[git-agent](https://github.com/SuperInstance/git-agent)** — Agent coordination via git

---
🦐 Cocapn fleet — lighthouse keeper architecture
