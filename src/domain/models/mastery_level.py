"""Mastery level enumeration for addition fact learning progression."""

from enum import Enum


class MasteryLevel(Enum):
    """Represents the mastery level of an addition fact.

    Levels progress from LEARNING -> PRACTICING -> MASTERED based on
    accuracy and consistency of responses.
    """

    LEARNING = "learning"
    PRACTICING = "practicing"
    MASTERED = "mastered"

    def __str__(self) -> str:
        """Return the string value of the mastery level."""
        return self.value

    @classmethod
    def from_string(cls, value: str) -> "MasteryLevel":
        """Create MasteryLevel from string value.

        Args:
            value: String representation of mastery level

        Returns:
            MasteryLevel enum instance

        Raises:
            ValueError: If value is not a valid mastery level
        """
        try:
            return cls(value.lower())
        except ValueError:
            valid_values = [level.value for level in cls]
            raise ValueError(
                f"Invalid mastery level: {value}. Must be one of: {valid_values}"
            )
