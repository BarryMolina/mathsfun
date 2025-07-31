"""Math fact performance repository with SM-2 spaced repetition support."""

from typing import List, Optional, Tuple, Dict
from datetime import datetime
from .base import BaseRepository, requires_authentication
from src.domain.models.math_fact_performance import MathFactPerformance
from src.domain.models.math_fact_attempt import MathFactAttempt


class MathFactRepository(BaseRepository):
    """Repository for math fact performance and attempt database operations."""

    @requires_authentication
    def get_user_fact_performance(
        self, user_id: str, fact_key: str
    ) -> Optional[MathFactPerformance]:
        """Get performance data for a specific math fact.

        Args:
            user_id: ID of the user
            fact_key: The math fact (e.g., "7+8")

        Returns:
            MathFactPerformance if found, None otherwise
        """
        try:
            response = (
                self.supabase_manager.get_client()
                .table("math_fact_performances")
                .select("*")
                .eq("user_id", user_id)
                .eq("fact_key", fact_key)
                .execute()
            )
            data = self._handle_single_response(response)
            return MathFactPerformance.from_dict(data) if data else None
        except Exception as e:
            print(f"Error fetching fact performance: {e}")
            return None

    @requires_authentication
    def get_all_user_performances(self, user_id: str) -> List[MathFactPerformance]:
        """Get all fact performances for a user.

        Args:
            user_id: ID of the user

        Returns:
            List of MathFactPerformance instances
        """
        try:
            response = (
                self.supabase_manager.get_client()
                .table("math_fact_performances")
                .select("*")
                .eq("user_id", user_id)
                .order("last_attempted", desc=True)
                .execute()
            )
            data = self._handle_response(response)
            return [MathFactPerformance.from_dict(item) for item in data]
        except Exception as e:
            print(f"Error fetching user performances: {e}")
            return []

    @requires_authentication
    def get_facts_due_for_review(
        self, user_id: str, limit: Optional[int] = None
    ) -> List[MathFactPerformance]:
        """Get facts that are due for review based on SM-2 scheduling.

        Args:
            user_id: ID of the user
            limit: Maximum number of facts to return

        Returns:
            List of facts due for review, ordered by next_review_date
        """
        try:
            query = (
                self.supabase_manager.get_client()
                .table("math_fact_performances")
                .select("*")
                .eq("user_id", user_id)
                .lte("next_review_date", datetime.now().isoformat())
                .order("next_review_date", desc=False)
            )

            if limit:
                query = query.limit(limit)

            response = query.execute()
            data = self._handle_response(response)
            return [MathFactPerformance.from_dict(item) for item in data]
        except Exception as e:
            print(f"Error fetching facts due for review: {e}")
            return []

    @requires_authentication
    def get_weak_facts(
        self,
        user_id: str,
        difficulty_range: Optional[Tuple[int, int]] = None,
        limit: int = 10,
    ) -> List[MathFactPerformance]:
        """Get facts that need practice based on low ease factor or frequent resets.

        Args:
            user_id: ID of the user
            difficulty_range: Optional tuple of (low, high) difficulty levels (not used in SM-2)
            limit: Maximum number of facts to return

        Returns:
            List of facts that need practice, ordered by ease factor ascending
        """
        try:
            query = (
                self.supabase_manager.get_client()
                .table("math_fact_performances")
                .select("*")
                .eq("user_id", user_id)
                .order("easiness_factor", desc=False)  # Lowest ease factor first
                .limit(limit)
            )

            response = query.execute()
            data = self._handle_response(response)
            return [MathFactPerformance.from_dict(item) for item in data]
        except Exception as e:
            print(f"Error fetching weak facts: {e}")
            return []

    @requires_authentication
    def upsert_fact_performance(
        self, performance: MathFactPerformance
    ) -> Optional[MathFactPerformance]:
        """Insert or update a fact performance record.

        Args:
            performance: MathFactPerformance instance to save

        Returns:
            Updated MathFactPerformance instance or None if failed
        """
        try:
            performance_data = performance.to_dict()
            performance_data["updated_at"] = datetime.now().isoformat()

            response = (
                self.supabase_manager.get_client()
                .table("math_fact_performances")
                .upsert(performance_data)
                .execute()
            )

            data = self._handle_single_response(response)
            return MathFactPerformance.from_dict(data) if data else None
        except Exception as e:
            print(f"Error upserting fact performance: {e}")
            return None

    @requires_authentication
    def create_fact_attempt(
        self, attempt: MathFactAttempt
    ) -> Optional[MathFactAttempt]:
        """Create a new fact attempt record.

        Args:
            attempt: MathFactAttempt instance to save

        Returns:
            Created MathFactAttempt instance or None if failed
        """
        try:
            attempt_data = attempt.to_dict()

            response = (
                self.supabase_manager.get_client()
                .table("math_fact_attempts")
                .insert(attempt_data)
                .execute()
            )

            data = self._handle_single_response(response)
            return MathFactAttempt.from_dict(data) if data else None
        except Exception as e:
            print(f"Error creating fact attempt: {e}")
            return None

    @requires_authentication
    def upsert_fact_performance_with_attempt(
        self, performance: MathFactPerformance, attempt: MathFactAttempt
    ) -> Optional[MathFactPerformance]:
        """Atomically update fact performance and create attempt record.

        This ensures data consistency when updating SM-2 data.

        Args:
            performance: MathFactPerformance instance to save
            attempt: MathFactAttempt instance to save

        Returns:
            Updated MathFactPerformance instance or None if failed
        """
        try:
            client = self.supabase_manager.get_client()

            # Update performance record
            performance_data = performance.to_dict()
            performance_data["updated_at"] = datetime.now().isoformat()

            performance_response = (
                client.table("math_fact_performances")
                .upsert(performance_data)
                .execute()
            )

            # Create attempt record
            attempt_data = attempt.to_dict()
            client.table("math_fact_attempts").insert(attempt_data).execute()

            # Return updated performance
            data = self._handle_single_response(performance_response)
            return MathFactPerformance.from_dict(data) if data else None

        except Exception as e:
            print(f"Error in atomic upsert: {e}")
            return None

    @requires_authentication
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
        try:
            query = (
                self.supabase_manager.get_client()
                .table("math_fact_attempts")
                .select("*")
                .eq("user_id", user_id)
                .order("attempted_at", desc=True)
            )

            if fact_key:
                query = query.eq("fact_key", fact_key)

            if limit:
                query = query.limit(limit)

            response = query.execute()
            data = self._handle_response(response)
            return [MathFactAttempt.from_dict(item) for item in data]
        except Exception as e:
            print(f"Error fetching fact attempts: {e}")
            return []

    @requires_authentication
    def batch_upsert_fact_performances(
        self, user_id: str, session_attempts: List[Tuple[int, int, bool, int, int]]
    ) -> List[MathFactPerformance]:
        """Batch process session attempts and update fact performances.

        Args:
            user_id: ID of the user
            session_attempts: List of (operand1, operand2, is_correct, response_time_ms, incorrect_attempts)

        Returns:
            List of updated MathFactPerformance instances
        """
        try:
            client = self.supabase_manager.get_client()
            performances_to_update = []
            attempts_to_create = []

            # Group attempts by fact key
            fact_attempts: Dict[str, List[Tuple[int, int, bool, int, int]]] = {}
            for (
                operand1,
                operand2,
                is_correct,
                response_time_ms,
                incorrect_attempts,
            ) in session_attempts:
                fact_key = f"{operand1}+{operand2}"
                if fact_key not in fact_attempts:
                    fact_attempts[fact_key] = []
                fact_attempts[fact_key].append(
                    (
                        operand1,
                        operand2,
                        is_correct,
                        response_time_ms,
                        incorrect_attempts,
                    )
                )

            # Process each unique fact
            for fact_key, attempts in fact_attempts.items():
                # Get existing performance or create new one
                performance = self.get_user_fact_performance(user_id, fact_key)
                if performance is None:
                    operand1, operand2 = map(int, fact_key.split("+"))
                    performance = MathFactPerformance.create_new(user_id, fact_key)

                # Apply all attempts for this fact
                for (
                    operand1,
                    operand2,
                    is_correct,
                    response_time_ms,
                    incorrect_attempts,
                ) in attempts:
                    # Update performance metrics
                    performance.update_performance(is_correct, response_time_ms)

                    # Calculate SM-2 grade and apply algorithm
                    sm2_grade = performance.calculate_sm2_grade(
                        response_time_ms, incorrect_attempts
                    )
                    performance.apply_sm2_algorithm(sm2_grade)

                    # Create attempt record
                    attempt = MathFactAttempt.create_new(
                        user_id=user_id,
                        fact_key=fact_key,
                        operand1=operand1,
                        operand2=operand2,
                        user_answer=operand1 + operand2 if is_correct else None,
                        correct_answer=operand1 + operand2,
                        is_correct=is_correct,
                        response_time_ms=response_time_ms,
                        incorrect_attempts_in_session=incorrect_attempts,
                        sm2_grade=sm2_grade,
                    )
                    attempts_to_create.append(attempt.to_dict())

                performances_to_update.append(performance.to_dict())

            # Batch update performances
            if performances_to_update:
                for perf_data in performances_to_update:
                    perf_data["updated_at"] = datetime.now().isoformat()

                client.table("math_fact_performances").upsert(
                    performances_to_update
                ).execute()

            # Batch create attempts
            if attempts_to_create:
                client.table("math_fact_attempts").insert(attempts_to_create).execute()

            # Return updated performances
            result = []
            for fact_key in fact_attempts.keys():
                updated_performance = self.get_user_fact_performance(user_id, fact_key)
                if updated_performance:
                    result.append(updated_performance)

            return result

        except Exception as e:
            print(f"Error in batch upsert: {e}")
            return []
