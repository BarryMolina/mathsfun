"""Addition fact performance repository for MathsFun application."""

from typing import List, Optional
from datetime import datetime
from .base import BaseRepository, requires_authentication
from src.domain.models.addition_fact_performance import AdditionFactPerformance
from src.domain.models.mastery_level import MasteryLevel


class AdditionFactRepository(BaseRepository):
    """Repository for addition fact performance database operations."""

    @requires_authentication
    def get_user_fact_performance(
        self, user_id: str, fact_key: str
    ) -> Optional[AdditionFactPerformance]:
        """Get performance data for a specific addition fact.

        Args:
            user_id: ID of the user
            fact_key: The addition fact (e.g., "7+8")

        Returns:
            AdditionFactPerformance if found, None otherwise
        """
        try:
            response = (
                self.supabase_manager.get_client()
                .table("addition_fact_performances")
                .select("*")
                .eq("user_id", user_id)
                .eq("fact_key", fact_key)
                .execute()
            )
            data = self._handle_single_response(response)
            return AdditionFactPerformance.from_dict(data) if data else None
        except Exception as e:
            print(f"Error fetching fact performance: {e}")
            return None

    @requires_authentication
    def get_user_fact_performances(
        self,
        user_id: str,
        mastery_level: Optional[MasteryLevel] = None,
        limit: int = 100,
    ) -> List[AdditionFactPerformance]:
        """Get all fact performances for a user.

        Args:
            user_id: ID of the user
            mastery_level: Optional filter by mastery level
            limit: Maximum number of records to return

        Returns:
            List of AdditionFactPerformance instances
        """
        try:
            query = (
                self.supabase_manager.get_client()
                .table("addition_fact_performances")
                .select("*")
                .eq("user_id", user_id)
            )

            if mastery_level:
                query = query.eq("mastery_level", mastery_level.value)

            response = query.order("last_attempted", desc=True).limit(limit).execute()
            data = self._handle_response(response)

            if data and isinstance(data, list):
                return [AdditionFactPerformance.from_dict(fact) for fact in data]
            return []
        except Exception as e:
            print(f"Error fetching user fact performances: {e}")
            return []

    @requires_authentication
    def create_fact_performance(
        self, performance: AdditionFactPerformance
    ) -> Optional[AdditionFactPerformance]:
        """Create a new addition fact performance record.

        Args:
            performance: AdditionFactPerformance instance to create

        Returns:
            Created AdditionFactPerformance with database ID
        """
        try:
            performance_data = performance.to_dict()
            performance_data.pop("id", None)  # Let database generate ID

            response = (
                self.supabase_manager.get_client()
                .table("addition_fact_performances")
                .insert(performance_data)
                .execute()
            )
            data = self._handle_single_response(response)
            return AdditionFactPerformance.from_dict(data) if data else None
        except Exception as e:
            print(f"Error creating fact performance: {e}")
            return None

    @requires_authentication
    def update_fact_performance(
        self, performance: AdditionFactPerformance
    ) -> Optional[AdditionFactPerformance]:
        """Update existing addition fact performance.

        Args:
            performance: AdditionFactPerformance instance to update

        Returns:
            Updated AdditionFactPerformance instance
        """
        try:
            performance_data = performance.to_dict()
            performance_data["updated_at"] = datetime.now().isoformat()

            response = (
                self.supabase_manager.get_client()
                .table("addition_fact_performances")
                .update(performance_data)
                .eq("id", performance.id)
                .execute()
            )
            data = self._handle_single_response(response)
            return AdditionFactPerformance.from_dict(data) if data else None
        except Exception as e:
            print(f"Error updating fact performance: {e}")
            return None

    @requires_authentication
    def upsert_fact_performance(
        self,
        user_id: str,
        fact_key: str,
        is_correct: bool,
        response_time_ms: int,
        timestamp: Optional[datetime] = None,
    ) -> Optional[AdditionFactPerformance]:
        """Create or update fact performance based on a new attempt.

        Args:
            user_id: ID of the user
            fact_key: The addition fact (e.g., "7+8")
            is_correct: Whether the attempt was correct
            response_time_ms: Response time in milliseconds
            timestamp: When the attempt was made (defaults to now)

        Returns:
            Updated or created AdditionFactPerformance instance
        """
        # Try to get existing performance
        existing = self.get_user_fact_performance(user_id, fact_key)

        if existing:
            # Update existing performance
            existing.update_performance(is_correct, response_time_ms, timestamp)
            # Update mastery level based on new performance
            existing.mastery_level = existing.determine_mastery_level()
            return self.update_fact_performance(existing)
        else:
            # Create new performance record
            new_performance = AdditionFactPerformance.create_new(user_id, fact_key)
            new_performance.update_performance(is_correct, response_time_ms, timestamp)
            new_performance.mastery_level = new_performance.determine_mastery_level()
            return self.create_fact_performance(new_performance)

    @requires_authentication
    def get_weak_facts(
        self,
        user_id: str,
        min_attempts: int = 3,
        max_accuracy: float = 80.0,
        limit: int = 10,
    ) -> List[AdditionFactPerformance]:
        """Get facts that need more practice.

        Args:
            user_id: ID of the user
            min_attempts: Minimum attempts to consider a fact
            max_accuracy: Maximum accuracy to consider "weak" (percentage)
            limit: Maximum number of weak facts to return

        Returns:
            List of AdditionFactPerformance instances for weak facts
        """
        try:
            # Get all facts for the user
            all_facts = self.get_user_fact_performances(user_id)
            if not all_facts:
                return []

            # Filter for weak facts
            weak_facts = [
                fact
                for fact in all_facts
                if fact.total_attempts >= min_attempts and fact.accuracy <= max_accuracy
            ]

            # Sort by accuracy (worst first) and limit
            weak_facts.sort(key=lambda f: f.accuracy)
            return weak_facts[:limit]
        except Exception as e:
            print(f"Error fetching weak facts: {e}")
            return []

    @requires_authentication
    def get_mastered_facts(
        self, user_id: str, limit: int = 50
    ) -> List[AdditionFactPerformance]:
        """Get facts that have been mastered.

        Args:
            user_id: ID of the user
            limit: Maximum number of mastered facts to return

        Returns:
            List of mastered AdditionFactPerformance instances
        """
        facts = self.get_user_fact_performances(
            user_id, mastery_level=MasteryLevel.MASTERED, limit=limit
        )
        return facts if facts is not None else []

    @requires_authentication
    def get_performance_summary(self, user_id: str) -> dict:
        """Get a summary of fact performance for a user.

        Args:
            user_id: ID of the user

        Returns:
            Dictionary with performance summary statistics
        """
        try:
            all_facts = self.get_user_fact_performances(user_id)

            if not all_facts:
                return {
                    "total_facts": 0,
                    "learning": 0,
                    "practicing": 0,
                    "mastered": 0,
                    "overall_accuracy": 0.0,
                    "total_attempts": 0,
                }

            # Count by mastery level
            mastery_counts = {
                "learning": len(
                    [f for f in all_facts if f.mastery_level == MasteryLevel.LEARNING]
                ),
                "practicing": len(
                    [f for f in all_facts if f.mastery_level == MasteryLevel.PRACTICING]
                ),
                "mastered": len(
                    [f for f in all_facts if f.mastery_level == MasteryLevel.MASTERED]
                ),
            }

            # Calculate overall statistics
            total_attempts = sum(f.total_attempts for f in all_facts)
            total_correct = sum(f.correct_attempts for f in all_facts)
            overall_accuracy = (
                (total_correct / total_attempts * 100) if total_attempts > 0 else 0.0
            )

            return {
                "total_facts": len(all_facts),
                "learning": mastery_counts["learning"],
                "practicing": mastery_counts["practicing"],
                "mastered": mastery_counts["mastered"],
                "overall_accuracy": round(overall_accuracy, 1),
                "total_attempts": total_attempts,
            }
        except Exception as e:
            print(f"Error getting performance summary: {e}")
            return {
                "total_facts": 0,
                "learning": 0,
                "practicing": 0,
                "mastered": 0,
                "overall_accuracy": 0.0,
                "total_attempts": 0,
            }
