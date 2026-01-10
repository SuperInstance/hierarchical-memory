#!/usr/bin/env python3
"""
Hierarchical Memory System - Basic Usage Example
================================================

This example demonstrates the core functionality of the hierarchical memory system.
"""

from hierarchical_memory import (
    HierarchicalMemory,
    MemoryType,
    MemoryImportance,
    ConsolidationEngine,
    IdentityPersistence,
)


def main():
    print("=" * 60)
    print("Hierarchical Memory System - Basic Usage")
    print("=" * 60)

    # ========================================================================
    # 1. CREATE MEMORY SYSTEM
    # ========================================================================
    print("\n1. Creating memory system...")
    memory = HierarchicalMemory(
        character_id="agent_001",
        storage_path="./data/agent_001_memory.json"
    )
    print(f"   Created memory system for: {memory.character_id}")

    # ========================================================================
    # 2. STORE MEMORIES
    # ========================================================================
    print("\n2. Storing memories...")

    # Episodic memories (specific events)
    memory.store_episodic(
        "Met with the engineering team to discuss Q1 goals",
        importance=7.0,
        emotional_valence=0.6,
        participants=["Alice", "Bob", "Carol"],
        location="Conference Room A"
    )

    memory.store_episodic(
        "Had a productive brainstorming session about the new feature",
        importance=6.5,
        emotional_valence=0.7,
        participants=["Dave"],
        location="Virtual Meeting"
    )

    memory.store_episodic(
        "Encountered a critical bug that took all day to fix",
        importance=5.0,
        emotional_valence=-0.3,
        participants=["Eve"],
        location="Office"
    )

    memory.store_episodic(
        "Successfully deployed the hotfix to production",
        importance=8.0,
        emotional_valence=0.9,
        participants=["Alice", "Bob"],
        location="Office"
    )

    # Working memory (current context)
    memory.store_working(
        "Currently reviewing the deployment logs",
        importance=4.0
    )

    # Semantic memory (learned facts)
    memory.store_semantic(
        "I work best when collaborating with small teams of 2-4 people",
        importance=7.5,
        emotional_valence=0.5
    )

    print(f"   Stored {len(memory.memories)} memories")

    # ========================================================================
    # 3. RETRIEVE MEMORIES
    # ========================================================================
    print("\n3. Retrieving memories...")

    # Search by query
    results = memory.retrieve("team meeting", top_k=3)
    print(f"   Found {len(results)} memories for 'team meeting':")
    for i, mem in enumerate(results, 1):
        print(f"   {i}. [{mem.memory_type.value}] {mem.content[:60]}...")
        print(f"      Importance: {mem.importance:.1f}, Accessed: {mem.access_count} times")

    # Get recent memories
    recent = memory.get_recent(hours=24, top_k=3)
    print(f"\n   Recent memories (last 24h):")
    for i, mem in enumerate(recent, 1):
        print(f"   {i}. {mem.content[:60]}...")

    # Get important memories
    important = memory.get_important(threshold=6.0, top_k=3)
    print(f"\n   Important memories (>6.0):")
    for i, mem in enumerate(important, 1):
        print(f"   {i}. [{mem.importance:.1f}] {mem.content[:60]}...")

    # ========================================================================
    # 4. TEMPORAL LANDMARKS
    # ========================================================================
    print("\n4. Checking temporal landmarks...")
    landmarks = memory.get_temporal_landmarks()
    print(f"   Found {len(landmarks)} temporal landmarks:")
    for landmark in landmarks:
        mem = memory.get_by_id(landmark.memory_id)
        if mem:
            print(f"   - {landmark.landmark_type}: {mem.content[:50]}...")

    # ========================================================================
    # 5. CONSOLIDATION
    # ========================================================================
    print("\n5. Running consolidation...")
    engine = ConsolidationEngine()

    # Check if consolidation is needed
    if memory.should_consolidate_reflection():
        print("   Reflection consolidation threshold reached!")
        result = engine.consolidate(memory, strategy="reflection", force=True)
        print(f"   Created {result.output_count} reflection memories")

    if memory.should_consolidate_episodic():
        print("   Episodic consolidation threshold reached!")
        result = engine.consolidate(memory, strategy="episodic_semantic", force=True)
        print(f"   Consolidated {result.input_count} episodic memories")
        print(f"   Created {result.output_count} semantic patterns")

    # ========================================================================
    # 6. AUTOBIOGRAPHICAL NARRATIVE
    # ========================================================================
    print("\n6. Generating autobiographical narrative...")
    narrative = memory.generate_narrative()
    print(f"   Coherence score: {narrative.coherence_score:.2f}")
    print(f"   Key themes: {', '.join(narrative.key_themes)}")
    print(f"\n   Narrative excerpt:")
    print("   " + "\n   ".join(narrative.narrative.split("\n")[:5]))

    # ========================================================================
    # 7. IDENTITY TRACKING
    # ========================================================================
    print("\n7. Tracking identity...")
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

    # Update identity from memories
    identity.update_from_memories(list(memory.memories.values()))

    # Get identity report
    report = identity.get_report(list(memory.memories.values()))
    print(f"   Identity Coherence Index: {report.coherence_index:.2f}")
    print(f"   Drift score: {report.drift_score:.2f}")
    print(f"   Core traits: {report.core_traits}")
    print(f"\n   Recommendations:")
    for rec in report.recommendations:
        print(f"   - {rec}")

    # ========================================================================
    # 8. STATS
    # ========================================================================
    print("\n8. Memory system stats...")
    stats = memory.get_stats()
    for key, value in stats.items():
        if isinstance(value, dict):
            print(f"   {key}:")
            for k, v in value.items():
                print(f"     {k}: {v}")
        else:
            print(f"   {key}: {value}")

    # ========================================================================
    # 9. SAVE
    # ========================================================================
    print("\n9. Saving memory system...")
    memory.save()
    print(f"   Saved to: {memory.storage_path}")

    print("\n" + "=" * 60)
    print("Example complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
