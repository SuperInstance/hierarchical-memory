#!/usr/bin/env python3
"""
Basic Usage Example for Hierarchical Memory System

This example demonstrates the fundamental features of the four-tier
memory architecture.
"""

from hierarchical_memory import HierarchicalMemory


def main():
    """Demonstrate basic memory system usage."""

    print("=" * 60)
    print("Hierarchical Memory System - Basic Usage Example")
    print("=" * 60)
    print()

    # Initialize the memory system
    memory = HierarchicalMemory(
        working_capacity=20,
        episodic_capacity=1000,
        semantic_embedding_dim=384
    )

    print("✓ Memory system initialized")
    print(f"  {memory}")
    print()

    # Working Memory: Short-term, capacity-limited
    print("1. Working Memory (Short-term)")
    print("-" * 40)

    memory.working.add("task1", "Complete project report", importance=0.8)
    memory.working.add("task2", "Email client about meeting", importance=0.6)
    memory.working.add("task3", "Review code changes", importance=0.7)

    print(f"  Added 3 tasks to working memory")
    print(f"  Current items: {len(memory.working)}")

    retrieved = memory.working.get("task1")
    print(f"  Retrieved 'task1': {retrieved}")
    print()

    # Episodic Memory: Autobiographical events
    print("2. Episodic Memory (Events & Experiences)")
    print("-" * 40)

    event_id = memory.episodic.add(
        content="Discussed Q4 roadmap with product team",
        emotional_valence=0.7,  # Positive emotion
        importance=0.8,
        context={"location": "office", "participants": ["Alice", "Bob"]}
    )

    print(f"  Added event: {event_id}")

    memory.episodic.add(
        content="Fixed critical bug in authentication system",
        emotional_valence=0.5,
        importance=0.9,
        context={"type": "work", "category": "development"}
    )

    print(f"  Total events: {len(memory.episodic)}")

    recent = memory.episodic.get_recent_events(limit=2)
    print(f"  Recent events:")
    for event in recent:
        print(f"    - {event.content} (importance: {event.importance})")
    print()

    # Semantic Memory: General knowledge
    print("3. Semantic Memory (Concepts & Knowledge)")
    print("-" * 40)

    memory.semantic.add_concept(
        name="project",
        attributes={"type": "work", "priority": "high", "category": "management"}
    )

    memory.semantic.add_concept(
        name="authentication",
        attributes={"type": "security", "complexity": "high"}
    )

    print(f"  Added 2 concepts")
    print(f"  Total concepts: {len(memory.semantic)}")

    # Search concepts
    results = memory.semantic.keyword_search("project", top_k=5)
    print(f"  Keyword search for 'project': {len(results)} results")
    print()

    # Procedural Memory: Skills and know-how
    print("4. Procedural Memory (Skills & Expertise)")
    print("-" * 40)

    memory.procedural.add_skill(
        name="report writing",
        attributes={"category": "communication", "difficulty": "medium"}
    )

    memory.procedural.add_skill(
        name="bug fixing",
        attributes={"category": "development", "difficulty": "high"}
    )

    print(f"  Added 2 skills")

    # Practice skills
    for _ in range(15):
        memory.procedural.practice("bug fixing", success=True)

    skill = memory.procedural.get_skill("bug fixing")
    print(f"  Practiced 'bug fixing' 15 times")
    print(f"  Mastery level: {skill.mastery_name} (Level {skill.mastery_level})")
    print(f"  Success rate: {skill.success_rate:.1%}")
    print()

    # Memory Consolidation
    print("5. Memory Consolidation")
    print("-" * 40)

    # Add items to consolidation queue
    for key, content in list(memory.working.items().items())[:2]:
        memory.consolidation.add_to_queue("working", "episodic", key, 0.8)

    print(f"  Queued {memory.consolidation.get_queue_size()} items for consolidation")

    consolidated = memory.consolidate()
    print(f"  Consolidated {consolidated} items from working to episodic")
    print()

    # Memory Retrieval
    print("6. Memory Retrieval")
    print("-" * 40)

    results = memory.search("project", mode="semantic", top_k=5)
    print(f"  Searched for 'project' across all memory tiers")
    print(f"  Found {len(results)} results")

    for i, result in enumerate(results[:3], 1):
        print(f"    {i}. [{result.tier}] {result.content} (score: {result.score:.2f})")
    print()

    # Statistics
    print("7. System Statistics")
    print("-" * 40)

    stats = memory.get_stats()
    print(f"  Working memory: {stats['working']['items']}/{stats['working']['capacity']} items")
    print(f"  Episodic memory: {stats['episodic']['events']} events")
    print(f"  Semantic memory: {stats['semantic']['concepts']} concepts")
    print(f"  Procedural memory:")
    print(f"    - Total skills: {stats['procedural']['total_skills']}")
    print(f"    - Total practices: {stats['procedural']['total_practice']}")
    print()

    print("=" * 60)
    print("Example completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
