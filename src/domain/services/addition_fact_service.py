"""Addition fact tracking service for business logic."""

from typing import List, Optional, Dict, Tuple, Any
from datetime import datetime
from src.domain.models.addition_fact_performance import AdditionFactPerformance
from src.domain.models.mastery_level import MasteryLevel
from src.infrastructure.database.repositories.addition_fact_repository import (
    AdditionFactRepository,
)


class AdditionFactService:
    """Service for addition fact performance tracking and analytics."""

    def __init__(self, fact_repository: AdditionFactRepository):
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
        is_correct: bool,
        response_time_ms: int,
        timestamp: Optional[datetime] = None,
    ) -> Optional[AdditionFactPerformance]:
        """Track an addition fact attempt.

        Args:
            user_id: ID of the user
            operand1: First operand in the addition
            operand2: Second operand in the addition
            is_correct: Whether the attempt was correct
            response_time_ms: Response time in milliseconds
            timestamp: When the attempt was made (defaults to now)

        Returns:
            Updated AdditionFactPerformance or None if error
        """
        fact_key = self.create_fact_key(operand1, operand2)

        return self.fact_repository.upsert_fact_performance(
            user_id=user_id,
            fact_key=fact_key,
            is_correct=is_correct,
            response_time_ms=response_time_ms,
            timestamp=timestamp,
        )

    def get_fact_performance(
        self, user_id: str, operand1: int, operand2: int
    ) -> Optional[AdditionFactPerformance]:
        """Get performance data for a specific addition fact.

        Args:
            user_id: ID of the user
            operand1: First operand
            operand2: Second operand

        Returns:
            AdditionFactPerformance if exists, None otherwise
        """
        fact_key = self.create_fact_key(operand1, operand2)
        return self.fact_repository.get_user_fact_performance(user_id, fact_key)

    def get_weak_facts(
        self,
        user_id: str,
        min_attempts: int = 3,
        max_accuracy: float = 80.0,
        limit: int = 10,
    ) -> List[AdditionFactPerformance]:
        """Get addition facts that need more practice.

        Args:
            user_id: ID of the user
            min_attempts: Minimum attempts to consider a fact
            max_accuracy: Maximum accuracy to consider "weak" (percentage)
            limit: Maximum number of weak facts to return

        Returns:
            List of weak addition facts
        """
        facts = self.fact_repository.get_weak_facts(
            user_id, min_attempts, max_accuracy, limit
        )
        return facts if facts is not None else []

    def get_mastered_facts(
        self, user_id: str, limit: int = 50
    ) -> List[AdditionFactPerformance]:
        """Get addition facts that have been mastered.

        Args:
            user_id: ID of the user
            limit: Maximum number of mastered facts to return

        Returns:
            List of mastered addition facts
        """
        facts = self.fact_repository.get_mastered_facts(user_id, limit)
        return facts if facts is not None else []

    def get_performance_summary(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive performance summary.

        Args:
            user_id: ID of the user

        Returns:
            Dictionary with performance statistics and insights
        """
        summary = self.fact_repository.get_performance_summary(user_id)

        if summary is None:
            # Return default summary if no data available
            return {
                "total_facts": 0,
                "mastered": 0,
                "practicing": 0,
                "learning": 0,
                "mastery_percentage": 0.0,
                "proficiency_level": "New Learner",
            }

        # Add derived insights
        total_facts = summary["total_facts"]
        if total_facts > 0:
            mastery_percentage = (summary["mastered"] / total_facts) * 100
            summary["mastery_percentage"] = round(mastery_percentage, 1)

            # Determine overall proficiency level
            if mastery_percentage >= 80:
                summary["proficiency_level"] = "Expert"
            elif mastery_percentage >= 60:
                summary["proficiency_level"] = "Advanced"
            elif mastery_percentage >= 40:
                summary["proficiency_level"] = "Intermediate"
            elif mastery_percentage >= 20:
                summary["proficiency_level"] = "Developing"
            else:
                summary["proficiency_level"] = "Beginner"
        else:
            summary["mastery_percentage"] = 0.0
            summary["proficiency_level"] = "New Learner"

        return summary

    def get_practice_recommendations(
        self, user_id: str, session_range: Tuple[int, int]
    ) -> Dict[str, Any]:
        """Get personalized practice recommendations.

        Args:
            user_id: ID of the user
            session_range: Tuple of (low, high) range for the session

        Returns:
            Dictionary with practice recommendations
        """
        low, high = session_range

        # Get weak facts in the session range
        all_weak_facts = self.get_weak_facts(user_id, limit=50)

        # Filter for facts in the current session range
        range_weak_facts = []
        for fact in all_weak_facts:
            try:
                operands = fact.fact_key.split("+")
                op1, op2 = int(operands[0]), int(operands[1])
                if low <= op1 <= high and low <= op2 <= high:
                    range_weak_facts.append(fact)
            except (ValueError, IndexError):
                continue

        # Get mastered facts in range
        all_mastered = self.get_mastered_facts(user_id)
        range_mastered_facts = []
        for fact in all_mastered:
            try:
                operands = fact.fact_key.split("+")
                op1, op2 = int(operands[0]), int(operands[1])
                if low <= op1 <= high and low <= op2 <= high:
                    range_mastered_facts.append(fact)
            except (ValueError, IndexError):
                continue

        # Calculate total possible facts in range
        total_possible = (high - low + 1) ** 2

        return {
            "session_range": f"{low} to {high}",
            "total_possible_facts": total_possible,
            "weak_facts_count": len(range_weak_facts),
            "mastered_facts_count": len(range_mastered_facts),
            "weak_facts": range_weak_facts[:5],  # Top 5 weakest
            "recommendation": self._generate_recommendation_text(
                len(range_weak_facts), len(range_mastered_facts), total_possible
            ),
        }

    def _generate_recommendation_text(
        self, weak_count: int, mastered_count: int, total_possible: int
    ) -> str:
        """Generate recommendation text based on performance.

        Args:
            weak_count: Number of weak facts
            mastered_count: Number of mastered facts
            total_possible: Total possible facts in range

        Returns:
            Recommendation text string
        """
        if weak_count == 0 and mastered_count == total_possible:
            return "🎉 Excellent! You've mastered all facts in this range. Consider trying a harder range."
        elif weak_count == 0:
            return "🌟 Great work! No weak facts detected. Keep practicing to master the remaining facts."
        elif weak_count <= 3:
            return f"💪 Focus on these {weak_count} facts that need more practice."
        elif weak_count <= 10:
            return f"📚 You have {weak_count} facts to work on. Take your time with each one."
        else:
            return f"🎯 {weak_count} facts need attention. Consider practicing smaller ranges for better focus."

    def analyze_session_performance(
        self, user_id: str, session_attempts: List[Tuple[int, int, bool, int]]
    ) -> Dict[str, Any]:
        """Analyze performance for a completed session.

        Args:
            user_id: ID of the user
            session_attempts: List of (operand1, operand2, is_correct, response_time_ms)

        Returns:
            Dictionary with session analysis and updated performance data
        """
        if not session_attempts:
            return {"error": "No attempts to analyze"}

        # Track all attempts using batch operation for better performance
        updated_facts = self.fact_repository.batch_upsert_fact_performances(
            user_id, session_attempts
        )
        if updated_facts is None:
            return {"error": "Failed to process session attempts"}

        # Analyze session results
        total_attempts = len(session_attempts)
        correct_attempts = sum(
            1 for _, _, is_correct, _ in session_attempts if is_correct
        )
        session_accuracy = (
            (correct_attempts / total_attempts) * 100 if total_attempts > 0 else 0
        )

        # Group by mastery level changes
        mastery_improvements = []
        facts_to_practice = []

        for fact in updated_facts:
            if (
                fact.mastery_level == MasteryLevel.MASTERED
                and fact.total_attempts >= 10
            ):
                mastery_improvements.append(fact.fact_key)
            elif fact.accuracy < 80 and fact.total_attempts >= 3:
                facts_to_practice.append(fact.fact_key)

        return {
            "session_accuracy": round(session_accuracy, 1),
            "total_attempts": total_attempts,
            "correct_attempts": correct_attempts,
            "facts_practiced": len(
                set(
                    self.create_fact_key(op1, op2)
                    for op1, op2, _, _ in session_attempts
                )
            ),
            "mastery_improvements": mastery_improvements,
            "facts_needing_practice": facts_to_practice[:5],  # Top 5
            "updated_performances": updated_facts,
        }
