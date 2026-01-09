"""
Procedural Memory Module
========================

Implements skill-based memory with:
- Skill storage with mastery levels
- Practice-based improvement
- Skill transfer
- Forgetting curves
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import numpy as np

from .memory_types import Memory, MemoryType


class ProceduralMemory:
    """
    Procedural Memory: Skills, habits, and learned behaviors

    Neuroscience: "How-to" knowledge stored differently from facts.
    Requires practice, shows gradual improvement, resistant to forgetting.
    """

    def __init__(self):
        self._skills: Dict[str, Memory] = {}
        self._mastery_levels: Dict[str, float] = {}  # 0-1 scale
        self._practice_count: Dict[str, int] = {}
        self._last_practiced: Dict[str, datetime] = {}
        self._skill_dependencies: Dict[str, List[str]] = {}  # prerequisite skills

    def learn_skill(self,
                   skill_name: str,
                   description: str,
                   initial_mastery: float = 0.1,
                   dependencies: List[str] = None) -> Memory:
        """
        Learn a new skill.

        Args:
            skill_name: Name of skill
            description: Skill description
            initial_mastery: Starting mastery (0-1)
            dependencies: Prerequisite skills

        Returns:
            Created memory object
        """
        content = f"Skill: {skill_name} - {description}"

        memory = Memory(
            id=Memory.generate_id(content, datetime.now()),
            content=content,
            memory_type=MemoryType.PROCEDURAL,
            timestamp=datetime.now(),
            importance=6.0
        )

        self._skills[skill_name] = memory
        self._mastery_levels[skill_name] = np.clip(initial_mastery, 0.0, 1.0)
        self._practice_count[skill_name] = 1
        self._last_practiced[skill_name] = datetime.now()

        if dependencies:
            self._skill_dependencies[skill_name] = dependencies

        return memory

    def practice_skill(self, skill_name: str,
                      quality: float = 0.8,
                      time_spent_minutes: int = 30) -> float:
        """
        Practice a skill to improve mastery.

        Args:
            skill_name: Name of skill to practice
            quality: Practice quality (0-1)
            time_spent_minutes: Time spent practicing

        Returns:
            New mastery level
        """
        if skill_name not in self._skills:
            raise ValueError(f"Skill '{skill_name}' not learned yet")

        current_mastery = self._mastery_levels[skill_name]

        # Learning curve: logarithmic improvement
        # Each practice session gives diminishing returns
        practice_count = self._practice_count[skill_name]
        improvement = (0.1 * quality) / (1 + 0.1 * practice_count)

        # Time bonus (up to 2 hours)
        time_bonus = min(time_spent_minutes / 120.0, 0.05)

        # Update mastery
        new_mastery = current_mastery + improvement + time_bonus
        self._mastery_levels[skill_name] = np.clip(new_mastery, 0.0, 1.0)

        # Update practice tracking
        self._practice_count[skill_name] += 1
        self._last_practiced[skill_name] = datetime.now()

        return self._mastery_levels[skill_name]

    def get_mastery(self, skill_name: str) -> float:
        """
        Get current mastery level of skill.

        Args:
            skill_name: Name of skill

        Returns:
            Mastery level (0-1)
        """
        if skill_name not in self._skills:
            return 0.0

        # Apply forgetting curve
        mastery = self._mastery_levels[skill_name]
        last_practiced = self._last_practiced[skill_name]

        # Forgetting: exponential decay over time
        days_since_practice = (datetime.now() - last_practiced).total_seconds() / 86400
        decay_factor = np.exp(-0.05 * days_since_practice)  # 5% daily decay

        return mastery * decay_factor

    def can_perform(self, skill_name: str,
                   threshold: float = 0.7) -> bool:
        """
        Check if skill can be performed at threshold.

        Args:
            skill_name: Name of skill
            threshold: Minimum mastery required

        Returns:
            True if mastery >= threshold
        """
        return self.get_mastery(skill_name) >= threshold

    def forget_skill(self, skill_name: str) -> bool:
        """
        Remove skill from memory.

        Args:
            skill_name: Name of skill

        Returns:
            True if removed
        """
        if skill_name in self._skills:
            del self._skills[skill_name]
            del self._mastery_levels[skill_name]
            del self._practice_count[skill_name]
            del self._last_practiced[skill_name]

            if skill_name in self._skill_dependencies:
                del self._skill_dependencies[skill_name]

            return True

        return False

    def transfer_skill(self, source_skill: str,
                      target_skill: str,
                      transfer_rate: float = 0.3) -> float:
        """
        Transfer mastery from source skill to related target skill.

        Args:
            source_skill: Source skill name
            target_skill: Target skill name
            transfer_rate: How much mastery transfers (0-1)

        Returns:
            New mastery of target skill
        """
        if source_skill not in self._skills:
            raise ValueError(f"Source skill '{source_skill}' not found")

        source_mastery = self.get_mastery(source_skill)

        if target_skill not in self._skills:
            # Auto-learn target skill
            self.learn_skill(target_skill, f"Transferred from {source_skill}")

        # Transfer mastery
        target_mastery = self._mastery_levels[target_skill]
        transferred = source_mastery * transfer_rate

        self._mastery_levels[target_skill] = np.clip(
            target_mastery + transferred, 0.0, 1.0
        )

        return self._mastery_levels[target_skill]

    def get_practice_schedule(self,
                             target_mastery: float = 0.9,
                             skill_name: Optional[str] = None) -> Dict[str, int]:
        """
        Estimate practices needed to reach target mastery.

        Args:
            target_mastery: Desired mastery level
            skill_name: Specific skill (all if None)

        Returns:
            Dict mapping skill name -> practices needed
        """
        if skill_name:
            skills = {skill_name: self._skills.get(skill_name)}
        else:
            skills = self._skills

        schedule = {}

        for name, memory in skills.items():
            if memory is None:
                continue

            current = self.get_mastery(name)

            if current >= target_mastery:
                schedule[name] = 0
            else:
                # Estimate using logarithmic learning curve
                # mastery = 1 - exp(-k * practices)
                # practices = -ln(1 - mastery) / k
                remaining = target_mastery - current
                k = 0.1  # Learning rate
                practices_needed = int(-np.log(1 - remaining) / k)

                schedule[name] = max(1, practices_needed)

        return schedule

    def get_forgetting_curve(self, skill_name: str,
                            days: int = 30) -> List[tuple[int, float]]:
        """
        Simulate forgetting curve for skill.

        Args:
            skill_name: Name of skill
            days: Days to simulate

        Returns:
            List of (day, mastery) tuples
        """
        if skill_name not in self._skills:
            raise ValueError(f"Skill '{skill_name}' not found")

        base_mastery = self._mastery_levels[skill_name]
        curve = []

        for day in range(days + 1):
            decay = np.exp(-0.05 * day)
            mastery = base_mastery * decay
            curve.append((day, mastery))

        return curve

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get procedural memory statistics.

        Returns:
            Statistics dictionary
        """
        mastery_levels = [
            self.get_mastery(skill)
            for skill in self._skills
        ]

        return {
            "total_skills": len(self._skills),
            "mastered_skills": sum(1 for m in mastery_levels if m >= 0.9),
            "learning_skills": sum(1 for m in mastery_levels if 0.3 <= m < 0.9),
            "novice_skills": sum(1 for m in mastery_levels if m < 0.3),
            "average_mastery": np.mean(mastery_levels) if mastery_levels else 0.0,
            "total_practice_sessions": sum(self._practice_count.values()),
        }

    def __len__(self) -> int:
        """Return number of skills"""
        return len(self._skills)
