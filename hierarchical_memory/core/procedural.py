"""
Procedural Memory Module
Skills and know-how with practice-based improvement.

Based on procedural memory theory - memory for skills and habits,
improved through practice and repetition.
"""

import time
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
import numpy as np


class MasteryLevel(Enum):
    """Mastery levels for skills."""
    NOVICE = 1
    APPRENTICE = 2
    COMPETENT = 3
    PROFICIENT = 4
    EXPERT = 5
    MASTER = 6


@dataclass
class Skill:
    """A procedural skill with mastery tracking."""
    name: str
    mastery_level: int = 1  # 1-6
    practice_count: int = 0
    success_count: int = 0
    last_practiced: float = field(default_factory=time.time)
    creation_time: float = field(default_factory=time.time)
    attributes: Dict[str, Any] = field(default_factory=dict)
    performance_history: List[float] = field(default_factory=list)

    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        if self.practice_count == 0:
            return 0.0
        return self.success_count / self.practice_count

    @property
    def mastery_name(self) -> str:
        """Get mastery level name."""
        return MasteryLevel(self.mastery_level).name


class ProceduralMemory:
    """
    Procedural memory for skills and know-how.

    Features:
    - Skill mastery levels (Novice to Master, 6 levels)
    - Practice-based improvement
    - Success rate tracking
    - Performance history
    - Skill prerequisites and synergies
    """

    def __init__(
        self,
        practice_threshold: int = 10,
        mastery_decay: bool = False
    ):
        """
        Initialize procedural memory.

        Args:
            practice_threshold: Practices needed for mastery advancement (default: 10)
            mastery_decay: Whether mastery decays without practice (default: False)
        """
        self.practice_threshold = practice_threshold
        self.mastery_decay = mastery_decay
        self._skills: Dict[str, Skill] = {}
        self._prerequisites: Dict[str, Set[str]] = defaultdict(set)
        self._synergies: Dict[str, Dict[str, float]] = defaultdict(dict)

    def add_skill(
        self,
        name: str,
        attributes: Optional[Dict[str, Any]] = None,
        prerequisites: Optional[List[str]] = None
    ) -> bool:
        """
        Add a new skill.

        Args:
            name: Skill name (unique identifier)
            attributes: Optional skill attributes
            prerequisites: Optional list of prerequisite skill names

        Returns:
            True if added successfully
        """
        if not name:
            raise ValueError("Skill name cannot be empty")
        if name in self._skills:
            return False

        skill = Skill(name=name, attributes=attributes or {})
        self._skills[name] = skill

        if prerequisites:
            for prereq in prerequisites:
                if prereq in self._skills:
                    self._prerequisites[name].add(prereq)

        return True

    def practice(
        self,
        name: str,
        success: bool = True,
        performance: Optional[float] = None
    ) -> bool:
        """
        Practice a skill and potentially improve mastery.

        Args:
            name: Skill name
            success: Whether the practice was successful
            performance: Optional performance score (0-1)

        Returns:
            True if skill exists and was practiced
        """
        skill = self._skills.get(name)
        if not skill:
            return False

        skill.practice_count += 1
        skill.last_practiced = time.time()

        if success:
            skill.success_count += 1

        if performance is not None:
            skill.performance_history.append(performance)

        # Check for mastery advancement
        self._check_mastery_advancement(skill)

        return True

    def _check_mastery_advancement(self, skill: Skill):
        """
        Check if skill mastery should advance.

        Args:
            skill: The skill to check
        """
        # Practices needed = threshold * current level
        practices_needed = self.practice_threshold * skill.mastery_level

        if skill.practice_count >= practices_needed:
            # Check success rate requirement
            success_rate = skill.success_rate
            min_success_rate = 0.5 + (skill.mastery_level * 0.05)  # 0.55 to 0.80

            if success_rate >= min_success_rate:
                # Check prerequisites
                if self._prerequisites_met(skill.name):
                    if skill.mastery_level < 6:
                        skill.mastery_level += 1

    def _prerequisites_met(self, skill_name: str) -> bool:
        """
        Check if skill prerequisites are met.

        Args:
            skill_name: Name of the skill

        Returns:
            True if all prerequisites are met
        """
        prereqs = self._prerequisites.get(skill_name, set())

        for prereq in prereqs:
            prereq_skill = self._skills.get(prereq)
            if not prereq_skill or prereq_skill.mastery_level < 3:
                # Prerequisite must be at least Competent level
                return False

        return True

    def get_skill(self, name: str) -> Optional[Skill]:
        """
        Retrieve a skill.

        Args:
            name: Skill name

        Returns:
            The skill, or None if not found
        """
        return self._skills.get(name)

    def can_perform(self, name: str) -> bool:
        """
        Check if a skill can be performed (meets prerequisites).

        Args:
            name: Skill name

        Returns:
            True if skill exists and prerequisites are met
        """
        if name not in self._skills:
            return False

        return self._prerequisites_met(name)

    def get_mastery_level(self, name: str) -> Optional[int]:
        """
        Get mastery level of a skill.

        Args:
            name: Skill name

        Returns:
            Mastery level (1-6), or None if not found
        """
        skill = self._skills.get(name)
        return skill.mastery_level if skill else None

    def add_synergy(self, skill1: str, skill2: str, boost: float = 0.1):
        """
        Add a synergy between two skills.

        Args:
            skill1: First skill name
            skill2: Second skill name
            boost: Practice boost (0-1)
        """
        if skill1 in self._skills and skill2 in self._skills:
            self._synergies[skill1][skill2] = boost
            self._synergies[skill2][skill1] = boost

    def get_synergy_bonus(self, skill: str) -> float:
        """
        Get total synergy bonus for a skill.

        Args:
            skill: Skill name

        Returns:
            Total bonus from synergies
        """
        if skill not in self._synergies:
            return 0.0

        bonus = 0.0
        for other, boost in self._synergies[skill].items():
            other_skill = self._skills.get(other)
            if other_skill and other_skill.mastery_level >= 3:
                # Synergy activates if other skill is Competent or higher
                bonus += boost

        return bonus

    def get_top_skills(self, limit: int = 10) -> List[Skill]:
        """
        Get top skills by mastery level.

        Args:
            limit: Maximum number of skills to return

        Returns:
            List of skills sorted by mastery level
        """
        skills = list(self._skills.values())
        skills.sort(key=lambda s: (s.mastery_level, s.practice_count), reverse=True)
        return skills[:limit]

    def get_practice_streak(self, name: str) -> int:
        """
        Calculate practice streak for a skill.

        Args:
            name: Skill name

        Returns:
            Number of days practiced consecutively
        """
        skill = self._skills.get(name)
        if not skill:
            return 0

        # Simplified streak calculation
        # In production, would track daily practice
        return skill.practice_count // self.practice_threshold

    def get_neglected_skills(self, days: int = 7) -> List[Skill]:
        """
        Get skills that haven't been practiced recently.

        Args:
            days: Days since last practice

        Returns:
            List of neglected skills
        """
        cutoff_time = time.time() - (days * 86400)
        neglected = [
            skill for skill in self._skills.values()
            if skill.last_practiced < cutoff_time
        ]
        neglected.sort(key=lambda s: s.last_practiced)
        return neglected

    def get_stats(self) -> Dict[str, Any]:
        """
        Get memory statistics.

        Returns:
            Dictionary of statistics
        """
        total_practice = sum(s.practice_count for s in self._skills.values())
        total_success = sum(s.success_count for s in self._skills.values())

        mastery_counts = {level.value: 0 for level in MasteryLevel}
        for skill in self._skills.values():
            mastery_counts[skill.mastery_level] += 1

        return {
            "total_skills": len(self._skills),
            "total_practice": total_practice,
            "total_success": total_success,
            "overall_success_rate": total_success / total_practice if total_practice > 0 else 0,
            "mastery_distribution": mastery_counts,
            "mastered_skills": mastery_counts[6],
            "expert_skills": mastery_counts[5]
        }

    def __len__(self) -> int:
        """Return number of skills."""
        return len(self._skills)

    def __contains__(self, name: str) -> bool:
        """Check if skill exists."""
        return name in self._skills

    def __repr__(self) -> str:
        """String representation of procedural memory."""
        return f"ProceduralMemory(skills={len(self._skills)}, threshold={self.practice_threshold})"


def create_procedural_memory(
    practice_threshold: int = 10,
    mastery_decay: bool = False
) -> ProceduralMemory:
    """
    Factory function to create a procedural memory instance.

    Args:
        practice_threshold: Practices needed for mastery advancement
        mastery_decay: Whether mastery decays without practice

    Returns:
        Configured ProceduralMemory instance
    """
    return ProceduralMemory(
        practice_threshold=practice_threshold,
        mastery_decay=mastery_decay
    )
