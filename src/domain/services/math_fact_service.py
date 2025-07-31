"""Math fact tracking service with SM-2 spaced repetition algorithm."""

from typing import List, Optional, Dict, Tuple, Any
from datetime import datetime
from src.domain.models.math_fact_performance import MathFactPerformance
from src.domain.models.math_fact_attempt import MathFactAttempt
from src.infrastructure.database.repositories.math_fact_repository import (
    MathFactRepository,
)


class MathFactService:
    """Service for math fact performance tracking using SM-2 spaced repetition algorithm."""

    def __init__(self, fact_repository: MathFactRepository):
        """Initialize the service with required repository.

        Args:
            fact_repository: Repository for fact performance data access
        """
        self.fact_repository = fact_repository

    def create_fact_key(self, operand1: int, operand2: int) -> str:
        """Create fact key preserving operand order.

        Records facts exactly as presented without normalization.
        E.g., "8+3" and "3+8" are tracked as separate facts.

        Args:
            operand1: First operand
            operand2: Second operand

        Returns:
            Fact key string preserving operand order
        """
        return f"{operand1}+{operand2}"

    def track_attempt(
        self,
        user_id: str,
        operand1: int,
        operand2: int,
        user_answer: Optional[int],
        correct_answer: int,
        is_correct: bool,
        response_time_ms: int,
        incorrect_attempts_in_session: int = 0,
        timestamp: Optional[datetime] = None,
    ) -> Optional[MathFactPerformance]:
        """Track a math fact attempt and update SM-2 data.

        Args:
            user_id: ID of the user
            operand1: First operand
            operand2: Second operand
            user_answer: User's answer (None if no answer provided)
            correct_answer: The correct answer
            is_correct: Whether the attempt was correct
            response_time_ms: Response time in milliseconds
            incorrect_attempts_in_session: Number of incorrect attempts before this one
            timestamp: When the attempt was made (defaults to now)

        Returns:
            Updated MathFactPerformance instance or None if failed
        """
        fact_key = self.create_fact_key(operand1, operand2)
        attempt_timestamp = timestamp or datetime.now()

        try:
            # Get or create fact performance record
            performance = self.fact_repository.get_user_fact_performance(
                user_id, fact_key
            )
            if performance is None:
                performance = MathFactPerformance.create_new(user_id, fact_key)

            # Update basic performance metrics
            performance.update_performance(
                is_correct, response_time_ms, attempt_timestamp
            )

            # Calculate SM-2 grade and apply algorithm
            sm2_grade = performance.calculate_sm2_grade(
                response_time_ms, incorrect_attempts_in_session
            )
            performance.apply_sm2_algorithm(sm2_grade)

            # Create attempt record
            attempt = MathFactAttempt.create_new(
                user_id=user_id,
                fact_key=fact_key,
                operand1=operand1,
                operand2=operand2,
                user_answer=user_answer,
                correct_answer=correct_answer,
                is_correct=is_correct,
                response_time_ms=response_time_ms,
                incorrect_attempts_in_session=incorrect_attempts_in_session,
                sm2_grade=sm2_grade,
            )

            # Save both performance and attempt atomically
            updated_performance = (
                self.fact_repository.upsert_fact_performance_with_attempt(
                    performance, attempt
                )
            )

            return updated_performance

        except Exception as e:
            # Log error in real implementation
            print(f"Error tracking attempt: {e}")
            return None

    def get_facts_due_for_review(
        self, user_id: str, limit: Optional[int] = None
    ) -> List[MathFactPerformance]:
        """Get facts that are due for review based on SM-2 scheduling.

        Args:
            user_id: ID of the user
            limit: Maximum number of facts to return (None for all)

        Returns:
            List of facts due for review, ordered by next_review_date
        """
        result = self.fact_repository.get_facts_due_for_review(user_id, limit)
        return result if result is not None else []

    def get_user_fact_performance(
        self, user_id: str, operand1: int, operand2: int
    ) -> Optional[MathFactPerformance]:
        """Get performance data for a specific fact.

        Args:
            user_id: ID of the user
            operand1: First operand
            operand2: Second operand

        Returns:
            MathFactPerformance instance or None if not found
        """
        fact_key = self.create_fact_key(operand1, operand2)
        return self.fact_repository.get_user_fact_performance(user_id, fact_key)

    def get_all_user_performances(self, user_id: str) -> List[MathFactPerformance]:
        """Get all fact performances for a user.

        Args:
            user_id: ID of the user

        Returns:
            List of all MathFactPerformance instances for the user
        """
        result = self.fact_repository.get_all_user_performances(user_id)
        return result if result is not None else []

    def get_user_fact_attempts(
        self, user_id: str, fact_key: Optional[str] = None, limit: Optional[int] = None
    ) -> List[MathFactAttempt]:
        """Get attempt history for a user.

        Args:
            user_id: ID of the user
            fact_key: Optional specific fact key to filter by
            limit: Maximum number of attempts to return

        Returns:
            List of MathFactAttempt instances, ordered by attempted_at DESC
        """
        result = self.fact_repository.get_user_fact_attempts(user_id, fact_key, limit)
        return result if result is not None else []

    def analyze_session_performance(
        self, user_id: str, session_attempts: List[Tuple[int, int, bool, int, int]]
    ) -> Dict[str, Any]:
        """Analyze performance from a quiz session using SM-2 data.

        Args:
            user_id: ID of the user
            session_attempts: List of (operand1, operand2, is_correct, response_time_ms, incorrect_attempts)

        Returns:
            Dictionary containing session analysis with SM-2 metrics
        """
        if not session_attempts:
            return {
                "facts_practiced": [],
                "new_facts_learned": [],
                "facts_due_for_review": 0,
                "average_response_time_ms": 0,
                "session_accuracy": 0.0,
            }

        # Process all attempts and update SM-2 data
        facts_practiced = []
        new_facts_learned = []

        for (
            operand1,
            operand2,
            is_correct,
            response_time_ms,
            incorrect_attempts,
        ) in session_attempts:
            fact_key = self.create_fact_key(operand1, operand2)

            # Check if this was a new fact
            existing_performance = self.fact_repository.get_user_fact_performance(
                user_id, fact_key
            )
            is_new_fact = (
                existing_performance is None or existing_performance.total_attempts == 0
            )

            # Track the attempt (this will update SM-2 data)
            performance = self.track_attempt(
                user_id=user_id,
                operand1=operand1,
                operand2=operand2,
                user_answer=operand1 + operand2 if is_correct else None,  # Simplified
                correct_answer=operand1 + operand2,
                is_correct=is_correct,
                response_time_ms=response_time_ms,
                incorrect_attempts_in_session=incorrect_attempts,
            )

            if performance:
                facts_practiced.append(fact_key)
                if is_new_fact:
                    new_facts_learned.append(fact_key)

        # Calculate session statistics
        total_attempts = len(session_attempts)
        correct_attempts = sum(
            1 for _, _, is_correct, _, _ in session_attempts if is_correct
        )
        total_response_time = sum(
            response_time_ms for _, _, _, response_time_ms, _ in session_attempts
        )

        session_accuracy = (
            (correct_attempts / total_attempts * 100) if total_attempts > 0 else 0.0
        )
        average_response_time = (
            total_response_time / total_attempts if total_attempts > 0 else 0
        )

        # Get count of facts due for review
        facts_due = self.get_facts_due_for_review(user_id)
        facts_due_count = len(facts_due)

        return {
            "facts_practiced": facts_practiced,
            "new_facts_learned": new_facts_learned,
            "facts_due_for_review": facts_due_count,
            "average_response_time_ms": average_response_time,
            "session_accuracy": session_accuracy,
            "total_attempts": total_attempts,
            "correct_attempts": correct_attempts,
        }

    def get_weak_facts(
        self,
        user_id: str,
        difficulty_range: Optional[Tuple[int, int]] = None,
        limit: int = 10,
    ) -> List[MathFactPerformance]:
        """Get facts that need more practice based on SM-2 data.

        Args:
            user_id: ID of the user
            difficulty_range: Optional tuple of (low, high) difficulty levels
            limit: Maximum number of facts to return

        Returns:
            List of facts that need practice, prioritizing those due for review
        """
        # Get facts due for review first (these are the weakest)
        due_facts = self.get_facts_due_for_review(user_id, limit)

        if len(due_facts) >= limit:
            return due_facts[:limit]

        # If we need more facts, get those with low ease factors or high repetition resets
        additional_needed = limit - len(due_facts)
        weak_facts = self.fact_repository.get_weak_facts(
            user_id, difficulty_range, additional_needed
        )
        weak_facts = weak_facts if weak_facts is not None else []

        return due_facts + weak_facts[:additional_needed]

    def get_performance_summary(self, user_id: str) -> Dict[str, Any]:
        """Get overall performance summary with SM-2 metrics.

        Args:
            user_id: ID of the user

        Returns:
            Dictionary containing performance summary
        """
        all_performances = self.get_all_user_performances(user_id)

        if not all_performances:
            return {
                "total_facts": 0,
                "facts_due_for_review": 0,
                "average_accuracy": 0.0,
                "average_ease_factor": 2.5,
                "total_attempts": 0,
                "facts_by_interval": {},
            }

        total_facts = len(all_performances)
        facts_due = len([p for p in all_performances if p.is_due_for_review])
        total_attempts = sum(p.total_attempts for p in all_performances)
        total_accuracy = sum(
            p.accuracy for p in all_performances if p.total_attempts > 0
        )
        average_accuracy = total_accuracy / total_facts if total_facts > 0 else 0.0

        # Calculate average ease factor
        ease_factors = [float(p.easiness_factor) for p in all_performances]
        average_ease_factor = (
            sum(ease_factors) / len(ease_factors) if ease_factors else 2.5
        )

        # Group facts by interval days
        facts_by_interval = {}
        for performance in all_performances:
            interval = performance.interval_days
            if interval not in facts_by_interval:
                facts_by_interval[interval] = 0
            facts_by_interval[interval] += 1

        return {
            "total_facts": total_facts,
            "facts_due_for_review": facts_due,
            "average_accuracy": average_accuracy,
            "average_ease_factor": average_ease_factor,
            "total_attempts": total_attempts,
            "facts_by_interval": facts_by_interval,
        }
