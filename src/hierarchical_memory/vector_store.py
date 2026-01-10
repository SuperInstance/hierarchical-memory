"""
Hierarchical Memory System - Vector Store Module
================================================

Vector-based semantic memory retrieval using embeddings.

Supports:
- Qdrant vector database (production)
- In-memory fallback (development)
- Sentence transformer embeddings
- Weighted retrieval (recency, importance, relevance)
- Batch operations

The vector store enables semantic search across memories, finding relevant
content even without exact keyword matches.
"""

from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field, asdict
from datetime import datetime
import hashlib

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False
    QdrantClient = None
    Distance = None
    VectorParams = None
    PointStruct = None
    Filter = None
    FieldCondition = None
    MatchValue = None

try:
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False
    SentenceTransformer = None

import numpy as np


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class MemoryVector:
    """Memory with embedding and metadata"""
    id: str
    content: str
    embedding: Optional[List[float]] = None
    character_id: str = ""
    timestamp: str = ""
    memory_type: str = ""
    importance: float = 5.0
    emotional_valence: float = 0.0
    participants: List[str] = field(default_factory=list)
    location: str = ""
    consolidated: bool = False
    is_temporal_landmark: bool = False
    landmark_type: Optional[str] = None
    access_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MemoryVector":
        """Create from dictionary"""
        return cls(**data)


# ============================================================================
# EMBEDDING MODEL
# ============================================================================

class EmbeddingModel:
    """
    Wrapper for embedding generation.

    Supports:
    - sentence-transformers (preferred)
    - Fallback hash-based embeddings
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2", device: str = "cpu"):
        self.model_name = model_name
        self.device = device
        self.model = None
        self.embedding_dim = 384  # Default for MiniLM

        if EMBEDDINGS_AVAILABLE:
            try:
                self.model = SentenceTransformer(model_name, device=device)
                self.embedding_dim = self.model.get_sentence_embedding_dimension()
            except Exception as e:
                print(f"Warning: Could not load embedding model {model_name}: {e}")

    def encode(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding for text.

        Returns:
            List of floats representing the embedding, or None if failed
        """
        if self.model is not None:
            try:
                embedding = self.model.encode(text, convert_to_numpy=False)
                return embedding.tolist() if hasattr(embedding, 'tolist') else list(embedding)
            except Exception as e:
                print(f"Error encoding text: {e}")

        # Fallback: hash-based embedding
        return self._hash_embedding(text)

    def encode_batch(self, texts: List[str]) -> List[Optional[List[float]]]:
        """Encode multiple texts efficiently"""
        if self.model is not None:
            try:
                embeddings = self.model.encode(texts, convert_to_numpy=False)
                return [
                    emb.tolist() if hasattr(emb, 'tolist') else list(emb)
                    for emb in embeddings
                ]
            except Exception as e:
                print(f"Error encoding batch: {e}")

        return [self._hash_embedding(text) for text in texts]

    def _hash_embedding(self, text: str) -> List[float]:
        """
        Simple hash-based embedding (fallback).
        Creates a deterministic but semantically meaningless embedding.
        """
        hash_digest = hashlib.sha256(text.encode()).hexdigest()
        embedding = []

        # Create embedding of correct dimension
        for i in range(self.embedding_dim):
            byte_val = int(hash_digest[i % len(hash_digest)], 16)
            # Normalize to approximately [-1, 1]
            embedding.append((byte_val - 7.5) / 7.5)

        return embedding

    @property
    def dimension(self) -> int:
        """Get embedding dimension"""
        return self.embedding_dim


# ============================================================================
# VECTOR MEMORY STORE
# ============================================================================

class VectorMemoryStore:
    """
    Vector memory store with optional Qdrant backend.

    Features:
    - Semantic search across memories
    - Weighted retrieval (recency, importance, relevance)
    - Automatic embedding generation
    - In-memory fallback when Qdrant unavailable
    - Per-character collections

    Example:
        >>> store = VectorMemoryStore(character_id="agent_001")
        >>> store.add_memory("Met the team to discuss goals", importance=7.0)
        >>> results = store.search("team meeting", top_k=5)
    """

    def __init__(self,
                 character_id: str,
                 qdrant_url: str = "http://localhost:6333",
                 collection_prefix: str = "character_memories_",
                 embedding_model: Optional[str] = None):
        """
        Initialize vector store.

        Args:
            character_id: Unique identifier for this character
            qdrant_url: Qdrant server URL
            collection_prefix: Prefix for collection names
            embedding_model: Name of sentence-transformer model
        """
        self.character_id = character_id
        self.qdrant_url = qdrant_url
        self.collection_name = f"{collection_prefix}{character_id}"

        # Initialize embedding model
        self.embedding_model = EmbeddingModel(embedding_model or "all-MiniLM-L6-v2")

        # Initialize Qdrant client
        self.client: Optional[QdrantClient] = None
        self.using_fallback = False

        if QDRANT_AVAILABLE:
            try:
                self.client = QdrantClient(url=qdrant_url)
                self._init_collection()
            except Exception as e:
                print(f"Warning: Could not connect to Qdrant: {e}")
                self.using_fallback = True
        else:
            self.using_fallback = True

        # In-memory fallback storage
        self.fallback_memories: Dict[str, MemoryVector] = {}

    def _init_collection(self):
        """Initialize Qdrant collection if it doesn't exist"""
        if not self.client:
            return

        try:
            collections = self.client.get_collections()
            collection_names = [c.name for c in collections.collections]

            if self.collection_name not in collection_names:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.embedding_model.dimension,
                        distance=Distance.COSINE
                    )
                )
                print(f"Created collection: {self.collection_name}")
        except Exception as e:
            print(f"Error initializing collection: {e}")
            self.using_fallback = True

    # ======================================================================
    # MEMORY OPERATIONS
    # ======================================================================

    def add_memory(self,
                   content: str,
                   importance: float = 5.0,
                   memory_type: str = "episodic",
                   emotional_valence: float = 0.0,
                   participants: Optional[List[str]] = None,
                   location: str = "",
                   timestamp: Optional[str] = None,
                   embedding: Optional[List[float]] = None) -> bool:
        """
        Add a memory to the vector store.

        Args:
            content: Memory content
            importance: 1-10 importance score
            memory_type: Type of memory
            emotional_valence: -1 to 1 emotional score
            participants: List of participants
            location: Location string
            timestamp: ISO timestamp (default: now)
            embedding: Pre-computed embedding (optional)

        Returns:
            True if successfully added
        """
        memory_id = hashlib.md5(
            f"{self.character_id}{content}{timestamp or datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]

        # Generate embedding if not provided
        if embedding is None:
            embedding = self.embedding_model.encode(content)

        memory_vector = MemoryVector(
            id=memory_id,
            content=content,
            embedding=embedding,
            character_id=self.character_id,
            timestamp=timestamp or datetime.now().isoformat(),
            memory_type=memory_type,
            importance=importance,
            emotional_valence=emotional_valence,
            participants=participants or [],
            location=location,
        )

        return self.store_vector(memory_vector)

    def store_vector(self, memory_vector: MemoryVector) -> bool:
        """
        Store a pre-created memory vector.

        Args:
            memory_vector: MemoryVector to store

        Returns:
            True if successful
        """
        # Generate embedding if needed
        if memory_vector.embedding is None:
            memory_vector.embedding = self.embedding_model.encode(memory_vector.content)

        # Try Qdrant first
        if self.client and not self.using_fallback:
            try:
                point = PointStruct(
                    id=hash(memory_vector.id) % (2**31),
                    vector=memory_vector.embedding,
                    payload=memory_vector.to_dict()
                )

                self.client.upsert(
                    collection_name=self.collection_name,
                    points=[point]
                )
                return True
            except Exception as e:
                print(f"Error storing to Qdrant: {e}")
                self.using_fallback = True

        # Fallback to in-memory storage
        self.fallback_memories[memory_vector.id] = memory_vector
        return True

    def get_memory(self, memory_id: str) -> Optional[MemoryVector]:
        """Get a memory by ID"""
        # Check fallback first
        if memory_id in self.fallback_memories:
            return self.fallback_memories[memory_id]

        # Check Qdrant
        if self.client and not self.using_fallback:
            try:
                results = self.client.retrieve(
                    collection_name=self.collection_name,
                    ids=[hash(memory_id) % (2**31)],
                    with_payload=True,
                    with_vectors=True
                )
                if results:
                    payload = results[0].payload
                    payload["embedding"] = results[0].vector.tolist() if results[0].vector else None
                    return MemoryVector.from_dict(payload)
            except Exception as e:
                print(f"Error retrieving from Qdrant: {e}")

        return None

    def delete_memory(self, memory_id: str) -> bool:
        """Delete a memory by ID"""
        # Remove from fallback
        if memory_id in self.fallback_memories:
            del self.fallback_memories[memory_id]

        # Remove from Qdrant
        if self.client and not self.using_fallback:
            try:
                self.client.delete(
                    collection_name=self.collection_name,
                    points_selector=[hash(memory_id) % (2**31)]
                )
                return True
            except Exception as e:
                print(f"Error deleting from Qdrant: {e}")

        return True

    # ======================================================================
    # SEARCH & RETRIEVAL
    # ======================================================================

    def search(self,
               query: str,
               top_k: int = 10,
               memory_type: Optional[str] = None,
               α_recency: float = 1.0,
               α_importance: float = 1.0,
               α_relevance: float = 1.0) -> List[MemoryVector]:
        """
        Search memories with weighted scoring.

        Args:
            query: Search query
            top_k: Maximum results
            memory_type: Filter by memory type
            α_recency: Weight for recency
            α_importance: Weight for importance
            α_relevance: Weight for semantic relevance

        Returns:
            List of MemoryVectors sorted by combined score
        """
        # Generate query embedding
        query_embedding = self.embedding_model.encode(query)

        if not query_embedding:
            return []

        # Try Qdrant first
        if self.client and not self.using_fallback:
            try:
                return self._qdrant_search(
                    query_embedding, top_k, memory_type,
                    α_recency, α_importance, α_relevance
                )
            except Exception as e:
                print(f"Error searching Qdrant: {e}")
                self.using_fallback = True

        # Fallback search
        return self._fallback_search(
            query, top_k, memory_type,
            α_recency, α_importance, α_relevance
        )

    def _qdrant_search(self,
                       query_embedding: List[float],
                       top_k: int,
                       memory_type: Optional[str],
                       α_recency: float,
                       α_importance: float,
                       α_relevance: float) -> List[MemoryVector]:
        """Search using Qdrant"""
        # Build filter
        search_filter = None
        if memory_type and FieldCondition is not None:
            search_filter = Filter(
                must=[FieldCondition(key="memory_type", match=MatchValue(value=memory_type))]
            )

        # Search
        search_results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            query_filter=search_filter,
            limit=top_k * 3,  # Get more for re-ranking
            with_payload=True
        )

        # Re-rank with weighted scoring
        scored = []
        current_time = datetime.now()

        for result in search_results:
            payload = result.payload

            # Relevance from Qdrant (cosine similarity)
            relevance_score = result.score

            # Recency score
            try:
                timestamp = datetime.fromisoformat(payload["timestamp"])
                hours_ago = (current_time - timestamp).total_seconds() / 3600
                recency_score = 0.995 ** hours_ago
            except:
                recency_score = 0.5

            # Importance score
            importance_score = payload.get("importance", 5.0) / 10.0

            # Combined score
            total_weight = α_recency + α_importance + α_relevance
            combined_score = (
                α_recency * recency_score +
                α_importance * importance_score +
                α_relevance * relevance_score
            ) / total_weight if total_weight > 0 else 0

            memory = MemoryVector(
                id=payload["id"],
                content=payload["content"],
                embedding=result.vector,
                character_id=payload["character_id"],
                timestamp=payload["timestamp"],
                memory_type=payload["memory_type"],
                importance=payload["importance"],
                emotional_valence=payload.get("emotional_valence", 0.0),
                participants=payload.get("participants", []),
                location=payload.get("location", ""),
                consolidated=payload.get("consolidated", False),
                is_temporal_landmark=payload.get("is_temporal_landmark", False),
                landmark_type=payload.get("landmark_type"),
                access_count=payload.get("access_count", 0)
            )

            scored.append((combined_score, memory))

        # Sort and return top_k
        scored.sort(reverse=True, key=lambda x: x[0])
        return [m for _, m in scored[:top_k]]

    def _fallback_search(self,
                         query: str,
                         top_k: int,
                         memory_type: Optional[str],
                         α_recency: float,
                         α_importance: float,
                         α_relevance: float) -> List[MemoryVector]:
        """Fallback search from in-memory storage"""
        scored = []
        current_time = datetime.now()

        for memory in self.fallback_memories.values():
            # Filter by type
            if memory_type and memory.memory_type != memory_type:
                continue

            # Simple text similarity
            relevance_score = self._text_similarity(query, memory.content)

            # Recency
            try:
                timestamp = datetime.fromisoformat(memory.timestamp)
                hours_ago = (current_time - timestamp).total_seconds() / 3600
                recency_score = 0.995 ** hours_ago
            except:
                recency_score = 0.5

            # Importance
            importance_score = memory.importance / 10.0

            # Combined
            total_weight = α_recency + α_importance + α_relevance
            score = (
                α_recency * recency_score +
                α_importance * importance_score +
                α_relevance * relevance_score
            ) / total_weight if total_weight > 0 else 0

            scored.append((score, memory))

        scored.sort(reverse=True, key=lambda x: x[0])
        return [m for _, m in scored[:top_k]]

    def _text_similarity(self, text1: str, text2: str) -> float:
        """Simple text similarity using word overlap"""
        words1 = set(w.lower() for w in text1.split() if len(w) > 2)
        words2 = set(w.lower() for w in text2.split() if len(w) > 2)

        if not words1 or not words2:
            return 0.0

        intersection = len(words1 & words2)
        union = len(words1 | words2)

        return intersection / union if union > 0 else 0.0

    # ======================================================================
    # BATCH OPERATIONS
    # ======================================================================

    def add_batch(self, memories: List[Dict[str, Any]]) -> int:
        """
        Add multiple memories in batch.

        Args:
            memories: List of memory dictionaries with keys: content, importance, etc.

        Returns:
            Number of memories successfully added
        """
        added = 0
        for mem_dict in memories:
            if self.add_memory(**mem_dict):
                added += 1
        return added

    def search_batch(self, queries: List[str], top_k: int = 5) -> Dict[str, List[MemoryVector]]:
        """
        Search multiple queries.

        Args:
            queries: List of search queries
            top_k: Results per query

        Returns:
            Dict mapping query to results
        """
        return {query: self.search(query, top_k) for query in queries}

    # ======================================================================
    # COLLECTION MANAGEMENT
    # ======================================================================

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store"""
        if self.client and not self.using_fallback:
            try:
                info = self.client.get_collection(self.collection_name)
                return {
                    "name": self.collection_name,
                    "points_count": info.points_count,
                    "status": "Qdrant",
                    "vector_size": info.config.params.vectors.size if hasattr(info, 'config') else self.embedding_model.dimension
                }
            except:
                pass

        return {
            "name": self.collection_name,
            "memories_count": len(self.fallback_memories),
            "status": "Fallback (in-memory)",
            "vector_size": self.embedding_model.dimension
        }

    def clear(self):
        """Clear all memories from the store"""
        self.fallback_memories.clear()

        if self.client and not self.using_fallback:
            try:
                self.client.delete(collection_name=self.collection_name, points_selector=["*"])
            except Exception as e:
                print(f"Error clearing Qdrant: {e}")

    def delete_collection(self):
        """Delete the entire collection"""
        self.fallback_memories.clear()

        if self.client and not self.using_fallback:
            try:
                self.client.delete_collection(self.collection_name)
            except Exception as e:
                print(f"Error deleting collection: {e}")


# ============================================================================
# MULTI-CHARACTER MEMORY SEARCH
# ============================================================================

class MultiCharacterMemorySearch:
    """
    Search across multiple character memory stores.

    Useful for:
    - Finding shared experiences
    - Cross-character context retrieval
    - Group conversation memory
    """

    def __init__(self, stores: Dict[str, VectorMemoryStore]):
        """
        Initialize with multiple character stores.

        Args:
            stores: Dict mapping character_id to VectorMemoryStore
        """
        self.stores = stores

    def search_all(self,
                   query: str,
                   top_k_per_character: int = 3) -> Dict[str, List[MemoryVector]]:
        """Search across all character stores"""
        results = {}
        for char_id, store in self.stores.items():
            results[char_id] = store.search(query, top_k_per_character)
        return results

    def search_theme(self,
                     theme: str,
                     top_k: int = 10) -> List[Tuple[str, MemoryVector]]:
        """
        Search for a theme across all characters.

        Returns combined results with character IDs.
        """
        all_results = []
        for char_id, store in self.stores.items():
            memories = store.search(
                theme,
                top_k=top_k,
                α_recency=0.5,  # Less weight on recency
                α_importance=1.5,  # More weight on importance
                α_relevance=1.0
            )
            all_results.extend([(char_id, m) for m in memories])

        # Sort by importance
        all_results.sort(key=lambda x: x[1].importance, reverse=True)
        return all_results[:top_k]

    def find_shared_experiences(self,
                                 query: str,
                                 min_characters: int = 2) -> List[Dict[str, Any]]:
        """
        Find experiences shared between multiple characters.
        """
        results = self.search_all(query, top_k_per_character=5)

        # Group by content similarity
        grouped = defaultdict(list)
        for char_id, memories in results.items():
            for mem in memories:
                # Use first few words as grouping key
                key = " ".join(mem.content.split()[:5])
                grouped[key].append((char_id, mem))

        # Filter by min characters
        shared = []
        for key, items in grouped.items():
            if len(set(char_id for char_id, _ in items)) >= min_characters:
                shared.append({
                    "theme": key,
                    "characters": [char_id for char_id, _ in items],
                    "memories": [mem for _, mem in items]
                })

        return shared


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def create_vector_store(character_id: str,
                       qdrant_url: str = "http://localhost:6333") -> VectorMemoryStore:
    """Convenience function to create a vector store."""
    return VectorMemoryStore(character_id=character_id, qdrant_url=qdrant_url)


def is_qdrant_available() -> bool:
    """Check if Qdrant is available."""
    return QDRANT_AVAILABLE


def is_embeddings_available() -> bool:
    """Check if sentence-transformers is available."""
    return EMBEDDINGS_AVAILABLE
