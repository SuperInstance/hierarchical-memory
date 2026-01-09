"""
Memory Sharing Protocol
Pack-based memory sharing between agents.

Enables agents to share memories within their "pack" (group),
with conflict resolution and trust-based filtering.
"""

import time
import numpy as np
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
import hashlib


class SharingStrategy(Enum):
    """Memory sharing strategies."""
    BROADCAST = "broadcast"  # Share with all pack members
    SELECTIVE = "selective"  # Share with specific agents
    QUERY_BASED = "query_based"  # Share only when queried
    TRUST_BASED = "trust_based"  # Share based on trust scores


@dataclass
class SharedMemory:
    """A memory shared between agents."""
    content: Any
    source_agent: str
    timestamp: float = field(default_factory=time.time)
    memory_type: str = "episodic"  # "episodic", "semantic", "procedural"
    importance: float = 0.5
    access_count: int = 0
    shared_with: Set[str] = field(default_factory=set)


@dataclass
class AgentPack:
    """A pack of agents that can share memories."""
    pack_id: str
    members: Set[str] = field(default_factory=set)
    trust_matrix: Dict[str, Dict[str, float]] = field(default_factory=dict)

    def add_member(self, agent_id: str):
        """Add an agent to the pack."""
        self.members.add(agent_id)
        if agent_id not in self.trust_matrix:
            self.trust_matrix[agent_id] = {}

    def set_trust(self, agent1: str, agent2: str, trust: float):
        """Set trust level between two agents (0-1)."""
        if agent1 in self.members and agent2 in self.members:
            self.trust_matrix[agent1][agent2] = max(0.0, min(1.0, trust))

    def get_trust(self, agent1: str, agent2: str) -> float:
        """Get trust level between two agents."""
        return self.trust_matrix.get(agent1, {}).get(agent2, 0.5)


class MemorySharing:
    """
    Memory sharing protocol for agent packs.

    Features:
    - Pack-based memory sharing
    - Multiple sharing strategies
    - Trust-based filtering
    - Conflict resolution
    - Memory access tracking
    """

    def __init__(
        self,
        pack: AgentPack,
        default_strategy: SharingStrategy = SharingStrategy.TRUST_BASED,
        trust_threshold: float = 0.5,
        enable_conflict_resolution: bool = True
    ):
        """
        Initialize memory sharing protocol.

        Args:
            pack: Agent pack configuration
            default_strategy: Default sharing strategy
            trust_threshold: Minimum trust for sharing
            enable_conflict_resolution: Whether to resolve conflicts
        """
        self.pack = pack
        self.default_strategy = default_strategy
        self.trust_threshold = trust_threshold
        self.enable_conflict_resolution = enable_conflict_resolution
        self._shared_memories: List[SharedMemory] = []
        self._access_logs: Dict[str, List[Dict]] = {}

    def share_memory(
        self,
        agent_id: str,
        content: Any,
        memory_type: str = "episodic",
        importance: float = 0.5,
        strategy: Optional[SharingStrategy] = None,
        target_agents: Optional[List[str]] = None
    ) -> bool:
        """
        Share a memory with pack members.

        Args:
            agent_id: Source agent ID
            content: Memory content
            memory_type: Type of memory
            importance: Memory importance (0-1)
            strategy: Sharing strategy (uses default if None)
            target_agents: Specific targets for SELECTIVE strategy

        Returns:
            True if sharing succeeded
        """
        if agent_id not in self.pack.members:
            return False

        strategy = strategy or self.default_strategy

        # Determine recipients based on strategy
        recipients = self._get_recipients(
            agent_id,
            strategy,
            target_agents
        )

        if not recipients:
            return False

        # Create shared memory
        shared_memory = SharedMemory(
            content=content,
            source_agent=agent_id,
            memory_type=memory_type,
            importance=importance,
            shared_with=recipients
        )

        self._shared_memories.append(shared_memory)

        # Log sharing
        self._log_access(agent_id, "share", {
            "recipients": list(recipients),
            "memory_type": memory_type,
            "importance": importance
        })

        return True

    def _get_recipients(
        self,
        agent_id: str,
        strategy: SharingStrategy,
        target_agents: Optional[List[str]]
    ) -> Set[str]:
        """
        Determine recipients based on strategy.

        Args:
            agent_id: Source agent ID
            strategy: Sharing strategy
            target_agents: Specific targets

        Returns:
            Set of recipient agent IDs
        """
        if strategy == SharingStrategy.BROADCAST:
            # Share with all except self
            return self.pack.members - {agent_id}

        elif strategy == SharingStrategy.SELECTIVE:
            # Share with specific agents
            if target_agents:
                return set(target_agents) & self.pack.members - {agent_id}
            return set()

        elif strategy == SharingStrategy.TRUST_BASED:
            # Share only with trusted agents
            recipients = set()
            for member in self.pack.members:
                if member != agent_id:
                    trust = self.pack.get_trust(member, agent_id)
                    if trust >= self.trust_threshold:
                        recipients.add(member)
            return recipients

        elif strategy == SharingStrategy.QUERY_BASED:
            # Share only when queried (no automatic sharing)
            return set()

        return set()

    def receive_shared_memories(
        self,
        agent_id: str,
        memory_type: Optional[str] = None,
        min_importance: float = 0.0
    ) -> List[SharedMemory]:
        """
        Retrieve memories shared with an agent.

        Args:
            agent_id: Receiving agent ID
            memory_type: Filter by memory type
            min_importance: Minimum importance threshold

        Returns:
            List of shared memories
        """
        shared = []

        for memory in self._shared_memories:
            # Check if shared with this agent
            if agent_id not in memory.shared_with:
                continue

            # Filter by type
            if memory_type and memory.memory_type != memory_type:
                continue

            # Filter by importance
            if memory.importance < min_importance:
                continue

            shared.append(memory)

            # Log access
            self._log_access(agent_id, "receive", {
                "source": memory.source_agent,
                "memory_type": memory.memory_type
            })

        return shared

    def query_memories(
        self,
        agent_id: str,
        query: str,
        limit: int = 10
    ) -> List[SharedMemory]:
        """
        Query shared memories by content.

        Args:
            agent_id: Querying agent ID
            query: Search query
            limit: Maximum results

        Returns:
            List of matching shared memories
        """
        results = []
        query_lower = query.lower()

        for memory in self._shared_memories:
            # Check if shared with this agent
            if agent_id not in memory.shared_with:
                continue

            # Simple keyword matching
            if query_lower in str(memory.content).lower():
                results.append(memory)

                # Increment access count
                memory.access_count += 1

        # Sort by importance and access count
        results.sort(
            key=lambda m: (m.importance, m.access_count),
            reverse=True
        )

        return results[:limit]

    def resolve_conflict(
        self,
        memory1: SharedMemory,
        memory2: SharedMemory
    ) -> SharedMemory:
        """
        Resolve conflict between two conflicting memories.

        Args:
            memory1: First memory
            memory2: Second memory

        Returns:
            Resolved memory (the one to keep)
        """
        if not self.enable_conflict_resolution:
            return memory1

        # Resolution strategy: keep more important and more recent memory
        if memory1.importance > memory2.importance:
            return memory1
        elif memory2.importance > memory1.importance:
            return memory2
        else:
            # Equal importance, keep more recent
            return memory1 if memory1.timestamp > memory2.timestamp else memory2

    def update_trust(
        self,
        agent1: str,
        agent2: str,
        delta: float
    ):
        """
        Update trust level between agents.

        Args:
            agent1: First agent ID
            agent2: Second agent ID
            delta: Trust change (-1 to 1)
        """
        current_trust = self.pack.get_trust(agent1, agent2)
        new_trust = max(0.0, min(1.0, current_trust + delta))
        self.pack.set_trust(agent1, agent2, new_trust)

    def _log_access(self, agent_id: str, action: str, metadata: Dict[str, Any]):
        """Log memory access."""
        if agent_id not in self._access_logs:
            self._access_logs[agent_id] = []

        self._access_logs[agent_id].append({
            "timestamp": time.time(),
            "action": action,
            "metadata": metadata
        })

    def get_access_logs(self, agent_id: str) -> List[Dict]:
        """
        Get access logs for an agent.

        Args:
            agent_id: Agent ID

        Returns:
            List of access logs
        """
        return self._access_logs.get(agent_id, [])

    def get_sharing_stats(self) -> Dict[str, Any]:
        """
        Get sharing statistics.

        Returns:
            Dictionary of statistics
        """
        memory_types = {}
        for memory in self._shared_memories:
            memory_types[memory.memory_type] = memory_types.get(memory.memory_type, 0) + 1

        total_accesses = sum(m.access_count for m in self._shared_memories)

        return {
            "total_shared": len(self._shared_memories),
            "memory_types": memory_types,
            "total_accesses": total_accesses,
            "pack_members": len(self.pack.members),
            "avg_trust": np.mean([
                self.pack.get_trust(a1, a2)
                for a1 in self.pack.members
                for a2 in self.pack.members
                if a1 != a2
            ]) if len(self.pack.members) > 1 else 0
        }

    def __repr__(self) -> str:
        """String representation."""
        return f"MemorySharing(pack={self.pack.pack_id}, shared={len(self._shared_memories)})"


def create_memory_sharing(
    pack_id: str,
    members: List[str],
    default_strategy: SharingStrategy = SharingStrategy.TRUST_BASED,
    trust_threshold: float = 0.5,
    enable_conflict_resolution: bool = True
) -> MemorySharing:
    """
    Factory function to create a memory sharing protocol.

    Args:
        pack_id: Unique pack identifier
        members: List of agent IDs in pack
        default_strategy: Default sharing strategy
        trust_threshold: Minimum trust for sharing
        enable_conflict_resolution: Whether to resolve conflicts

    Returns:
        Configured MemorySharing instance
    """
    pack = AgentPack(pack_id=pack_id)
    for member in members:
        pack.add_member(member)

    return MemorySharing(
        pack=pack,
        default_strategy=default_strategy,
        trust_threshold=trust_threshold,
        enable_conflict_resolution=enable_conflict_resolution
    )
