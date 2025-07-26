"""Tests for MasteryLevel enum."""

import pytest
from src.domain.models.mastery_level import MasteryLevel


class TestMasteryLevel:
    """Test MasteryLevel enumeration."""

    def test_enum_values(self):
        """Test that enum has correct values."""
        assert MasteryLevel.LEARNING.value == "learning"
        assert MasteryLevel.PRACTICING.value == "practicing"
        assert MasteryLevel.MASTERED.value == "mastered"

    def test_string_conversion(self):
        """Test string representation of enum values."""
        assert str(MasteryLevel.LEARNING) == "learning"
        assert str(MasteryLevel.PRACTICING) == "practicing"
        assert str(MasteryLevel.MASTERED) == "mastered"

    def test_from_string_valid(self):
        """Test creating enum from valid string values."""
        assert MasteryLevel.from_string("learning") == MasteryLevel.LEARNING
        assert MasteryLevel.from_string("practicing") == MasteryLevel.PRACTICING
        assert MasteryLevel.from_string("mastered") == MasteryLevel.MASTERED

    def test_from_string_case_insensitive(self):
        """Test that from_string is case insensitive."""
        assert MasteryLevel.from_string("LEARNING") == MasteryLevel.LEARNING
        assert MasteryLevel.from_string("Practicing") == MasteryLevel.PRACTICING
        assert MasteryLevel.from_string("MASTERED") == MasteryLevel.MASTERED

    def test_from_string_invalid(self):
        """Test that invalid string raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            MasteryLevel.from_string("invalid")

        assert "Invalid mastery level: invalid" in str(exc_info.value)
        assert "learning" in str(exc_info.value)
        assert "practicing" in str(exc_info.value)
        assert "mastered" in str(exc_info.value)

    def test_comparison(self):
        """Test enum comparison."""
        assert MasteryLevel.LEARNING == MasteryLevel.LEARNING
        assert MasteryLevel.LEARNING != MasteryLevel.PRACTICING
        assert MasteryLevel.PRACTICING != MasteryLevel.MASTERED


@pytest.mark.unit
class TestMasteryLevelUnit:
    """Unit tests for MasteryLevel enum."""

    def test_enum_membership(self):
        """Test enum membership."""
        assert MasteryLevel.LEARNING in MasteryLevel
        assert MasteryLevel.PRACTICING in MasteryLevel
        assert MasteryLevel.MASTERED in MasteryLevel

    def test_enum_iteration(self):
        """Test iterating over enum values."""
        values = [level.value for level in MasteryLevel]
        assert "learning" in values
        assert "practicing" in values
        assert "mastered" in values
        assert len(values) == 3