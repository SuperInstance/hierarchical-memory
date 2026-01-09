"""
Test suite for Procedural Memory module.

Tests cover:
- Skill learning
- Practice and improvement
- Forgetting curves
- Skill transfer
- Mastery tracking
"""

import pytest
import time
from datetime import datetime, timedelta
from hierarchical_memory.procedural_memory import ProceduralMemory
from hierarchical_memory.memory_types import MemoryType


class TestProceduralMemoryBasics:
    """Test basic procedural memory functionality."""

    @pytest.mark.procedural
    def test_initialization(self, procedural_memory):
        """Test procedural memory initialization."""
        assert procedural_memory is not None
        assert len(procedural_memory) == 0

    @pytest.mark.procedural
    def test_learn_skill(self, procedural_memory):
        """Test learning a new skill."""
        memory = procedural_memory.learn_skill(
            skill_name="Python Programming",
            description="Write and debug Python code",
            initial_mastery=0.3
        )
        assert memory is not None
        assert "Python Programming" in memory.content
        assert memory.memory_type == MemoryType.PROCEDURAL
        assert len(procedural_memory) == 1

    @pytest.mark.procedural
    def test_learn_skill_with_dependencies(self, procedural_memory):
        """Test learning skill with prerequisites."""
        procedural_memory.learn_skill("Python", "Basic Python", 0.8)
        memory = procedural_memory.learn_skill(
            skill_name="Data Science",
            description="Analyze data",
            initial_mastery=0.1,
            dependencies=["Python"]
        )
        assert memory is not None
        assert "Data Science" in procedural_memory._skill_dependencies

    @pytest.mark.procedural
    def test_learn_skill_clip_mastery(self, procedural_memory):
        """Test that mastery is clipped to [0, 1]."""
        # Too high
        memory1 = procedural_memory.learn_skill("Skill1", "Desc", initial_mastery=1.5)
        assert procedural_memory._mastery_levels["Skill1"] == 1.0

        # Too low
        memory2 = procedural_memory.learn_skill("Skill2", "Desc", initial_mastery=-0.5)
        assert procedural_memory._mastery_levels["Skill2"] == 0.0


class TestSkillPractice:
    """Test skill practice and improvement."""

    @pytest.mark.procedural
    def test_practice_skill(self, procedural_memory):
        """Test practicing a skill."""
        procedural_memory.learn_skill("Guitar", "Play guitar", 0.2)
        initial_mastery = procedural_memory.get_mastery("Guitar")

        new_mastery = procedural_memory.practice_skill("Guitar", quality=0.9, time_spent_minutes=60)

        assert new_mastery > initial_mastery
        assert new_mastery <= 1.0

    @pytest.mark.procedural
    def test_practice_increments_count(self, procedural_memory):
        """Test that practice count increments."""
        procedural_memory.learn_skill("Piano", "Play piano", 0.3)
        initial_count = procedural_memory._practice_count["Piano"]

        procedural_memory.practice_skill("Piano")

        assert procedural_memory._practice_count["Piano"] == initial_count + 1

    @pytest.mark.procedural
    def test_practice_nonexistent_skill(self, procedural_memory):
        """Test practicing a skill that wasn't learned."""
        with pytest.raises(ValueError):
            procedural_memory.practice_skill("UnknownSkill")

    @pytest.mark.procedural
    def test_practice_quality_effect(self, procedural_memory):
        """Test that practice quality affects improvement."""
        procedural_memory.learn_skill("Skill1", "Desc", 0.3)
        procedural_memory.learn_skill("Skill2", "Desc", 0.3)

        # Practice with different quality
        mastery1 = procedural_memory.practice_skill("Skill1", quality=0.5)
        mastery2 = procedural_memory.practice_skill("Skill2", quality=1.0)

        # Higher quality should give better improvement
        assert mastery2 > mastery1

    @pytest.mark.procedural
    def test_practice_time_bonus(self, procedural_memory):
        """Test that practice time provides bonus improvement."""
        procedural_memory.learn_skill("Skill", "Desc", 0.3)

        mastery_short = procedural_memory.practice_skill("Skill", quality=0.8, time_spent_minutes=30)
        mastery_long = procedural_memory.practice_skill("Skill", quality=0.8, time_spent_minutes=120)

        # Longer practice should give more improvement
        # Note: diminishing returns applies, so difference might be small
        assert mastery_long >= mastery_short

    @pytest.mark.procedural
    def test_diminishing_returns(self, procedural_memory):
        """Test that repeated practice shows diminishing returns."""
        procedural_memory.learn_skill("Skill", "Desc", 0.1)

        improvements = []
        for _ in range(5):
            before = procedural_memory.get_mastery("Skill")
            procedural_memory.practice_skill("Skill", quality=0.8, time_spent_minutes=60)
            after = procedural_memory.get_mastery("Skill")
            improvements.append(after - before)

        # Later practices should give less improvement
        assert improvements[0] >= improvements[-1]


class TestMasteryTracking:
    """Test mastery level tracking."""

    @pytest.mark.procedural
    def test_get_mastery(self, procedural_memory):
        """Test getting current mastery level."""
        procedural_memory.learn_skill("Python", "Code", 0.7)
        mastery = procedural_memory.get_mastery("Python")
        assert 0.0 <= mastery <= 1.0

    @pytest.mark.procedural
    def test_get_mastery_unknown_skill(self, procedural_memory):
        """Test getting mastery of unknown skill."""
        mastery = procedural_memory.get_mastery("Unknown")
        assert mastery == 0.0

    @pytest.mark.procedural
    def test_can_perform(self, procedural_memory):
        """Test checking if skill can be performed."""
        procedural_memory.learn_skill("ExpertSkill", "Desc", 0.9)
        procedural_memory.learn_skill("NoviceSkill", "Desc", 0.3)

        assert procedural_memory.can_perform("ExpertSkill", threshold=0.7) is True
        assert procedural_memory.can_perform("NoviceSkill", threshold=0.7) is False
        assert procedural_memory.can_perform("NoviceSkill", threshold=0.2) is True


class TestForgettingCurve:
    """Test forgetting curve functionality."""

    @pytest.mark.procedural
    def test_forgetting_over_time(self, procedural_memory):
        """Test that mastery decreases over time."""
        procedural_memory.learn_skill("Skill", "Desc", 0.8)
        initial_mastery = procedural_memory.get_mastery("Skill")

        # Modify last_practiced to simulate time passing
        old_time = datetime.now() - timedelta(days=10)
        procedural_memory._last_practiced["Skill"] = old_time

        current_mastery = procedural_memory.get_mastery("Skill")

        # Should have decayed
        assert current_mastery < initial_mastery

    @pytest.mark.procedural
    def test_forgetting_rate(self, procedural_memory):
        """Test forgetting curve rate."""
        procedural_memory.learn_skill("Skill", "Desc", 1.0)

        # Set to past
        old_time = datetime.now() - timedelta(days=20)
        procedural_memory._last_practiced["Skill"] = old_time

        mastery = procedural_memory.get_mastery("Skill")

        # Should decay exponentially but not reach zero
        assert 0.0 < mastery < 1.0

    @pytest.mark.procedural
    def test_get_forgetting_curve(self, procedural_memory):
        """Test generating forgetting curve."""
        procedural_memory.learn_skill("Skill", "Desc", 0.9)
        curve = procedural_memory.get_forgetting_curve("Skill", days=30)

        assert len(curve) == 31  # 0 to 30 inclusive
        assert curve[0][0] == 0  # Day 0
        assert curve[-1][0] == 30  # Day 30

        # Mastery should decrease over time
        assert curve[0][1] >= curve[-1][1]

    @pytest.mark.procedural
    def test_forgetting_curve_nonexistent_skill(self, procedural_memory):
        """Test forgetting curve for unknown skill."""
        with pytest.raises(ValueError):
            procedural_memory.get_forgetting_curve("Unknown", days=30)


class TestSkillTransfer:
    """Test skill transfer functionality."""

    @pytest.mark.procedural
    def test_transfer_skill(self, procedural_memory):
        """Test transferring mastery between skills."""
        procedural_memory.learn_skill("Python", "Language", 0.8)
        procedural_memory.learn_skill("DataScience", "Analysis", 0.2)

        new_mastery = procedural_memory.transfer_skill("Python", "DataScience", transfer_rate=0.5)

        # Should improve target skill
        assert new_mastery > 0.2
        assert new_mastery <= 1.0

    @pytest.mark.procedural
    def test_transfer_to_new_skill(self, procedural_memory):
        """Test transfer creates target skill if needed."""
        procedural_memory.learn_skill("Source", "Desc", 0.7)

        new_mastery = procedural_memory.transfer_skill("Source", "Target", transfer_rate=0.3)

        # Target should be created
        assert "Target" in procedural_memory._skills
        assert new_mastery > 0

    @pytest.mark.procedural
    def test_transfer_from_nonexistent_skill(self, procedural_memory):
        """Test transfer from unknown skill."""
        with pytest.raises(ValueError):
            procedural_memory.transfer_skill("Unknown", "Target", 0.3)

    @pytest.mark.procedural
    def test_transfer_rate_effect(self, procedural_memory):
        """Test that transfer rate affects improvement."""
        procedural_memory.learn_skill("Source", "Desc", 0.9)
        procedural_memory.learn_skill("Target1", "Desc", 0.1)
        procedural_memory.learn_skill("Target2", "Desc", 0.1)

        mastery1 = procedural_memory.transfer_skill("Source", "Target1", transfer_rate=0.2)
        mastery2 = procedural_memory.transfer_skill("Source", "Target2", transfer_rate=0.8)

        # Higher transfer rate should give more improvement
        assert mastery2 > mastery1


class TestSkillDeletion:
    """Test skill deletion/forgetting."""

    @pytest.mark.procedural
    def test_forget_skill(self, procedural_memory):
        """Test removing a skill."""
        procedural_memory.learn_skill("Temporary", "Temp", 0.5)
        assert "Temporary" in procedural_memory._skills

        result = procedural_memory.forget_skill("Temporary")

        assert result is True
        assert "Temporary" not in procedural_memory._skills
        assert "Temporary" not in procedural_memory._mastery_levels

    @pytest.mark.procedural
    def test_forget_nonexistent_skill(self, procedural_memory):
        """Test forgetting non-existent skill."""
        result = procedural_memory.forget_skill("Unknown")
        assert result is False

    @pytest.mark.procedural
    def test_forget_with_dependencies(self, procedural_memory):
        """Test forgetting skill with dependencies."""
        procedural_memory.learn_skill("Base", "Desc", 0.8)
        procedural_memory.learn_skill("Advanced", "Desc", 0.5, dependencies=["Base"])

        procedural_memory.forget_skill("Advanced")

        # Dependencies should be cleaned up
        assert "Advanced" not in procedural_memory._skill_dependencies
        assert "Base" in procedural_memory._skills  # Base should remain


class TestPracticeSchedule:
    """Test practice scheduling functionality."""

    @pytest.mark.procedural
    def test_get_practice_schedule_single_skill(self, procedural_memory):
        """Test practice schedule for single skill."""
        procedural_memory.learn_skill("Skill", "Desc", 0.5)

        schedule = procedural_memory.get_practice_schedule(target_mastery=0.9, skill_name="Skill")

        assert "Skill" in schedule
        assert schedule["Skill"] > 0

    @pytest.mark.procedural
    def test_get_practice_schedule_all_skills(self, procedural_memory):
        """Test practice schedule for all skills."""
        procedural_memory.learn_skill("Skill1", "Desc", 0.3)
        procedural_memory.learn_skill("Skill2", "Desc", 0.7)
        procedural_memory.learn_skill("Skill3", "Desc", 0.95)

        schedule = procedural_memory.get_practice_schedule(target_mastery=0.9)

        # Skill3 already above threshold
        assert schedule["Skill3"] == 0
        # Others need practice
        assert schedule["Skill1"] > 0
        assert schedule["Skill2"] > 0

    @pytest.mark.procedural
    def test_get_practice_schedule_unknown_skill(self, procedural_memory):
        """Test practice schedule for unknown skill."""
        schedule = procedural_memory.get_practice_schedule(skill_name="Unknown")
        assert "Unknown" in schedule
        # Unknown skill has 0 mastery, needs practice
        assert schedule["Unknown"] > 0


class TestStatistics:
    """Test statistics and monitoring."""

    @pytest.mark.procedural
    def test_get_statistics_empty(self, procedural_memory):
        """Test statistics for empty procedural memory."""
        stats = procedural_memory.get_statistics()
        assert stats["total_skills"] == 0
        assert stats["mastered_skills"] == 0
        assert stats["average_mastery"] == 0.0

    @pytest.mark.procedural
    def test_get_statistics_populated(self, populated_procedural_memory):
        """Test statistics for populated procedural memory."""
        procedural, memories = populated_procedural_memory
        stats = procedural.get_statistics()
        assert stats["total_skills"] > 0
        assert stats["average_mastery"] > 0

    @pytest.mark.procedural
    def test_skill_classification(self, procedural_memory):
        """Test skill mastery level classification."""
        procedural_memory.learn_skill("Novice", "Desc", 0.2)
        procedural_memory.learn_skill("Learning", "Desc", 0.5)
        procedural_memory.learn_skill("Mastered", "Desc", 0.95)

        stats = procedural_memory.get_statistics()
        assert stats["novice_skills"] == 1
        assert stats["learning_skills"] == 1
        assert stats["mastered_skills"] == 1


class TestIntegration:
    """Integration tests for procedural memory."""

    @pytest.mark.procedural
    @pytest.mark.integration
    def test_skill_lifecycle(self, procedural_memory):
        """Test complete skill lifecycle."""
        # Learn
        procedural_memory.learn_skill("Public Speaking", "Speak to crowds", 0.1)
        assert procedural_memory.get_mastery("Public Speaking") <= 0.2

        # Practice
        for _ in range(5):
            procedural_memory.practice_skill("Public Speaking", quality=0.8, time_spent_minutes=60)

        # Verify improvement
        mastery = procedural_memory.get_mastery("Public Speaking")
        assert mastery > 0.3

        # Time passes (simulated)
        old_time = datetime.now() - timedelta(days=5)
        procedural_memory._last_practiced["Public Speaking"] = old_time

        # Should have decayed some
        decayed_mastery = procedural_memory.get_mastery("Public Speaking")
        assert decayed_mastery < mastery

    @pytest.mark.procedural
    @pytest.mark.integration
    def test_dependent_skills_workflow(self, procedural_memory):
        """Test learning dependent skills."""
        # Learn prerequisite
        procedural_memory.learn_skill("Algebra", "Math", 0.9)

        # Learn dependent skill
        procedural_memory.learn_skill("Calculus", "Advanced math", 0.1, dependencies=["Algebra"])

        # Practice prerequisite first
        procedural_memory.practice_skill("Algebra", quality=0.9)

        # Transfer to dependent
        new_mastery = procedural_memory.transfer_skill("Algebra", "Calculus", transfer_rate=0.4)

        # Dependent should benefit
        assert new_mastery > 0.1
