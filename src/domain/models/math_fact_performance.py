"""Domain model for math fact performance tracking with SM-2 spaced repetition."""

from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional


@dataclass
class MathFactPerformance:
    """Represents performance tracking for a specific math fact using SM-2 spaced repetition algorithm.

    Tracks accuracy, speed, and SM-2 spaced repetition data for individual
    math facts like "7+8" or "3+5".
    """

    id: str
    user_id: str
    fact_key: str  # e.g., "7+8", "3+5"
    total_attempts: int = 0
    correct_attempts: int = 0
    total_response_time_ms: int = 0
    fastest_response_ms: Optional[int] = None
    slowest_response_ms: Optional[int] = None
    last_attempted: Optional[datetime] = None

    # SM-2 Algorithm Properties
    repetition_number: int = 0  # Number of consecutive correct responses >= grade 3
    easiness_factor: Decimal = Decimal("2.50")  # Difficulty factor (1.3-4.0)
    interval_days: int = 1  # Days until next review
    next_review_date: Optional[datetime] = (
        None  # When this fact should be reviewed next
    )

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @property
    def accuracy(self) -> float:
        """Calculate accuracy percentage.

        Returns:
            Accuracy as a percentage (0.0 to 100.0)
        """
        if self.total_attempts == 0:
            return 0.0
        return (self.correct_attempts / self.total_attempts) * 100

    @property
    def average_response_time_ms(self) -> float:
        """Calculate average response time in milliseconds.

        Returns:
            Average response time for correct attempts only
        """
        if self.correct_attempts == 0:
            return 0.0
        return self.total_response_time_ms / self.correct_attempts

    @property
    def average_response_time_seconds(self) -> float:
        """Calculate average response time in seconds.

        Returns:
            Average response time for correct attempts in seconds
        """
        return self.average_response_time_ms / 1000

    @property
    def is_due_for_review(self) -> bool:
        """Check if this fact is due for review based on SM-2 scheduling.

        Returns:
            True if the fact should be reviewed now
        """
        if self.next_review_date is None:
            return True
        return datetime.now() >= self.next_review_date

    def update_performance(
        self,
        is_correct: bool,
        response_time_ms: int,
        timestamp: Optional[datetime] = None,
    ) -> None:
        """Update performance metrics with a new attempt.

        Args:
            is_correct: Whether the attempt was correct
            response_time_ms: Response time in milliseconds
            timestamp: When the attempt was made (defaults to now)
        """
        self.total_attempts += 1
        self.last_attempted = timestamp or datetime.now()

        if is_correct:
            self.correct_attempts += 1
            self.total_response_time_ms += response_time_ms

            # Update fastest/slowest times for correct responses only
            if (
                self.fastest_response_ms is None
                or response_time_ms < self.fastest_response_ms
            ):
                self.fastest_response_ms = response_time_ms
            if (
                self.slowest_response_ms is None
                or response_time_ms > self.slowest_response_ms
            ):
                self.slowest_response_ms = response_time_ms

    def calculate_sm2_grade(
        self, response_time_ms: int, incorrect_attempts: int
    ) -> int:
        """Calculate SM-2 grade (0-5) from response metrics.

        Args:
            response_time_ms: Time taken to respond in milliseconds
            incorrect_attempts: Number of incorrect attempts before getting it right

        Returns:
            Grade from 0-5 for SM-2 algorithm:
            - 0: Total blackout (2+ incorrect attempts)
            - 1: Familiar but slow after seeing answer
            - 2: Easy to remember after seeing answer
            - 3: Significant effort but got it right first try
            - 4: Some hesitation but got it right first try
            - 5: Perfect recall
        """
        if incorrect_attempts >= 2:
            return 0  # Total blackout
        elif incorrect_attempts == 1:
            # Got it wrong once, then correct
            if response_time_ms < 3000:
                return 2  # Easy to remember after seeing answer
            else:
                return 1  # Familiar but slow after seeing answer
        else:
            # Got it right on first try
            if response_time_ms < 2000:
                return 5  # Perfect recall
            elif response_time_ms < 3000:
                return 4  # Some hesitation
            else:
                return 3  # Significant effort

    def apply_sm2_algorithm(self, grade: int) -> None:
        """Apply SM-2 spaced repetition algorithm to update interval and ease factor.

        Args:
            grade: Quality of response (0-5)
        """
        if grade < 0 or grade > 5:
            raise ValueError(f"Grade must be between 0 and 5, got {grade}")

        if grade < 3:
            # Incorrect response - reset repetition number but keep ease factor
            self.repetition_number = 0
            self.interval_days = 1
        else:
            # Correct response
            if self.repetition_number == 0:
                self.interval_days = 1
            elif self.repetition_number == 1:
                self.interval_days = 6
            else:
                # Calculate interval based on previous interval and ease factor
                self.interval_days = int(
                    self.interval_days * float(self.easiness_factor)
                )

            self.repetition_number += 1

        # Update ease factor based on grade
        old_ef = float(self.easiness_factor)
        new_ef = old_ef + (0.1 - (5 - grade) * (0.08 + (5 - grade) * 0.02))

        # Clamp ease factor to valid range (1.3 - 4.0)
        new_ef = max(1.3, min(4.0, new_ef))
        self.easiness_factor = Decimal(str(round(new_ef, 2)))

        # Set next review date
        self.next_review_date = datetime.now() + timedelta(days=self.interval_days)

    @classmethod
    def create_new(
        cls, user_id: str, fact_key: str, id: Optional[str] = None
    ) -> "MathFactPerformance":
        """Create a new MathFactPerformance instance with SM-2 defaults.

        Args:
            user_id: ID of the user
            fact_key: The math fact key (e.g., "7+8")
            id: Optional ID (will be generated if not provided)

        Returns:
            New MathFactPerformance instance
        """
        import uuid

        now = datetime.now()
        return cls(
            id=id or str(uuid.uuid4()),
            user_id=user_id,
            fact_key=fact_key,
            next_review_date=now + timedelta(days=1),  # Review tomorrow initially
            created_at=now,
        )

    @classmethod
    def from_dict(cls, data: dict) -> "MathFactPerformance":
        """Create MathFactPerformance from dictionary data.

        Args:
            data: Dictionary containing performance data

        Returns:
            MathFactPerformance instance
        """
        # Parse timestamps
        created_at = None
        if data.get("created_at"):
            created_at_str = data["created_at"].replace("Z", "+00:00")
            created_at = datetime.fromisoformat(created_at_str)

        updated_at = None
        if data.get("updated_at"):
            updated_at_str = data["updated_at"].replace("Z", "+00:00")
            updated_at = datetime.fromisoformat(updated_at_str)

        last_attempted = None
        if data.get("last_attempted"):
            last_attempted_str = data["last_attempted"].replace("Z", "+00:00")
            last_attempted = datetime.fromisoformat(last_attempted_str)

        next_review_date = None
        if data.get("next_review_date"):
            next_review_str = data["next_review_date"].replace("Z", "+00:00")
            next_review_date = datetime.fromisoformat(next_review_str)

        return cls(
            id=data["id"],
            user_id=data["user_id"],
            fact_key=data["fact_key"],
            total_attempts=data.get("total_attempts", 0),
            correct_attempts=data.get("correct_attempts", 0),
            total_response_time_ms=data.get("total_response_time_ms", 0),
            fastest_response_ms=data.get("fastest_response_ms"),
            slowest_response_ms=data.get("slowest_response_ms"),
            last_attempted=last_attempted,
            repetition_number=data.get("repetition_number", 0),
            easiness_factor=Decimal(str(data.get("easiness_factor", "2.50"))),
            interval_days=data.get("interval_days", 1),
            next_review_date=next_review_date,
            created_at=created_at,
            updated_at=updated_at,
        )

    def to_dict(self) -> dict:
        """Convert MathFactPerformance to dictionary.

        Returns:
            Dictionary representation suitable for database storage
        """
        return {
            "id": self.id,
            "user_id": self.user_id,
            "fact_key": self.fact_key,
            "total_attempts": self.total_attempts,
            "correct_attempts": self.correct_attempts,
            "total_response_time_ms": self.total_response_time_ms,
            "fastest_response_ms": self.fastest_response_ms,
            "slowest_response_ms": self.slowest_response_ms,
            "last_attempted": (
                self.last_attempted.isoformat() if self.last_attempted else None
            ),
            "repetition_number": self.repetition_number,
            "easiness_factor": float(self.easiness_factor),
            "interval_days": self.interval_days,
            "next_review_date": (
                self.next_review_date.isoformat() if self.next_review_date else None
            ),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
