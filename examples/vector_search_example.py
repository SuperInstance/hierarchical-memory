#!/usr/bin/env python3
"""
Hierarchical Memory System - Vector Search Example
===================================================

This example demonstrates using the vector store for semantic search.
"""

from hierarchical_memory import (
    VectorMemoryStore,
    MultiCharacterMemorySearch,
    is_qdrant_available,
    is_embeddings_available,
)


def main():
    print("=" * 60)
    print("Vector Memory Store - Semantic Search Example")
    print("=" * 60)

    # Check availability
    print(f"\nQdrant available: {is_qdrant_available()}")
    print(f"Embeddings available: {is_embeddings_available()}")

    # ========================================================================
    # 1. CREATE VECTOR STORE
    # ========================================================================
    print("\n1. Creating vector store...")
    store = VectorMemoryStore(
        character_id="agent_001",
        qdrant_url="http://localhost:6333"  # Or omit for in-memory fallback
    )
    print(f"   Created store: {store.collection_name}")
    print(f"   Status: {store.get_stats()['status']}")

    # ========================================================================
    # 2. ADD MEMORIES
    # ========================================================================
    print("\n2. Adding memories...")

    memories_to_add = [
        {
            "content": "Collaborated with the design team on new UI mockups",
            "importance": 7.0,
            "memory_type": "episodic",
            "emotional_valence": 0.6,
            "participants": ["Sarah", "Mike"],
        },
        {
            "content": "Presented quarterly roadmap to stakeholders",
            "importance": 8.5,
            "memory_type": "episodic",
            "emotional_valence": 0.8,
            "participants": ["Executive Team"],
        },
        {
            "content": "Learned that I thrive in collaborative environments",
            "importance": 7.5,
            "memory_type": "semantic",
            "emotional_valence": 0.7,
        },
        {
            "content": "Had a disagreement about technical approach with team lead",
            "importance": 5.0,
            "memory_type": "episodic",
            "emotional_valence": -0.4,
            "participants": ["Tom"],
        },
        {
            "content": "Successfully resolved the conflict and found middle ground",
            "importance": 7.0,
            "memory_type": "episodic",
            "emotional_valence": 0.5,
            "participants": ["Tom"],
        },
        {
            "content": "Pattern: I prefer collaborative problem-solving over working alone",
            "importance": 8.0,
            "memory_type": "semantic",
            "emotional_valence": 0.6,
            "consolidated": True,
        },
    ]

    added = store.add_batch(memories_to_add)
    print(f"   Added {added} memories")

    # ========================================================================
    # 3. SEMANTIC SEARCH
    # ========================================================================
    print("\n3. Semantic search...")

    queries = [
        "teamwork",
        "presentation",
        "conflict",
        "collaboration success",
    ]

    for query in queries:
        results = store.search(query, top_k=2)
        print(f"\n   Query: '{query}'")
        for i, mem in enumerate(results, 1):
            print(f"   {i}. [{mem.memory_type}] {mem.content[:70]}...")
            print(f"      Importance: {mem.importance:.1f}")

    # ========================================================================
    # 4. WEIGHTED SEARCH
    # ========================================================================
    print("\n4. Weighted search (different alpha values)...")

    # Recency-weighted (find recent memories)
    recent = store.search(
        "team",
        top_k=2,
        α_recency=2.0,   # High recency weight
        α_importance=0.5,
        α_relevance=0.5
    )
    print("   Recency-weighted search:")
    for mem in recent:
        print(f"   - {mem.content[:60]}... (timestamp: {mem.timestamp[:19]})")

    # Importance-weighted (find important memories)
    important = store.search(
        "team",
        top_k=2,
        α_recency=0.5,
        α_importance=2.0,   # High importance weight
        α_relevance=0.5
    )
    print("\n   Importance-weighted search:")
    for mem in important:
        print(f"   - [{mem.importance:.1f}] {mem.content[:60]}...")

    # Relevance-weighted (find semantically similar)
    relevant = store.search(
        "teamwork collaboration",
        top_k=2,
        α_recency=0.5,
        α_importance=0.5,
        α_relevance=2.0   # High relevance weight
    )
    print("\n   Relevance-weighted search:")
    for mem in relevant:
        print(f"   - {mem.content[:60]}...")

    # ========================================================================
    # 5. MULTI-CHARACTER SEARCH
    # ========================================================================
    print("\n5. Multi-character search...")

    # Create stores for multiple characters
    stores = {}
    for char_id in ["agent_001", "agent_002", "agent_003"]:
        stores[char_id] = VectorMemoryStore(character_id=char_id)

        # Add some memories for each
        stores[char_id].add_memory(
            content=f"{char_id} worked on the project together",
            memory_type="episodic",
            importance=6.0
        )
        if char_id == "agent_001":
            stores[char_id].add_memory(
                content="Led the team meeting about project goals",
                memory_type="episodic",
                importance=7.5
            )

    # Search across all characters
    multi_search = MultiCharacterMemorySearch(stores)
    results = multi_search.search_all("project meeting", top_k_per_character=2)

    print("   Results across all characters:")
    for char_id, memories in results.items():
        print(f"   {char_id}:")
        for mem in memories:
            print(f"     - {mem.content[:60]}...")

    # Find shared experiences
    print("\n   Finding shared experiences...")
    shared = multi_search.find_shared_experiences("project", min_characters=2)
    for item in shared:
        print(f"   Theme: {item['theme']}")
        print(f"   Characters: {', '.join(item['characters'])}")

    # ========================================================================
    # 6. STATS
    # ========================================================================
    print("\n6. Vector store stats...")
    stats = store.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")

    print("\n" + "=" * 60)
    print("Example complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
