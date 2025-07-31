"""Tests for MathFactRepository with SM-2 functionality."""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime, timedelta
from decimal import Decimal
from src.infrastructure.database.repositories.math_fact_repository import (
    MathFactRepository,
)
from src.domain.models.math_fact_performance import MathFactPerformance
from src.domain.models.math_fact_attempt import MathFactAttempt


class TestMathFactRepository:
    """Test MathFactRepository functionality."""

    @pytest.fixture
    def mock_supabase_manager(self):
        """Create a mock Supabase manager."""
        manager = Mock()
        client = Mock()
        manager.get_client.return_value = client
        manager.is_authenticated.return_value = True
        return manager

    @pytest.fixture
    def repository(self, mock_supabase_manager):
        """Create a MathFactRepository with mock Supabase manager."""
        return MathFactRepository(mock_supabase_manager)

    def test_get_user_fact_performance_found(self, repository, mock_supabase_manager):
        """Test getting user fact performance when record exists."""
        # Mock response data
        mock_data = {
            "id": "mock-uuid-123",
            "user_id": "user123",
            "fact_key": "7+8",
            "total_attempts": 5,
            "correct_attempts": 4,
            "average_response_time_ms": 2500,
            "repetition_number": 2,
            "easiness_factor": "2.60",
            "interval_days": 6,
            "next_review_date": datetime.now().isoformat(),
            "last_attempted": datetime.now().isoformat(),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }

        # Mock Supabase response
        mock_response = Mock()
        mock_response.data = [mock_data]

        mock_table = Mock()
        mock_table.select.return_value = mock_table
        mock_table.eq.return_value = mock_table
        mock_table.execute.return_value = mock_response

        mock_supabase_manager.get_client.return_value.table.return_value = mock_table

        result = repository.get_user_fact_performance("user123", "7+8")

        assert result is not None
        assert result.user_id == "user123"
        assert result.fact_key == "7+8"
        assert result.total_attempts == 5
        assert result.easiness_factor == Decimal("2.60")

    def test_get_user_fact_performance_not_found(
        self, repository, mock_supabase_manager
    ):
        """Test getting user fact performance when record doesn't exist."""
        # Mock empty response
        mock_response = Mock()
        mock_response.data = []

        mock_table = Mock()
        mock_table.select.return_value = mock_table
        mock_table.eq.return_value = mock_table
        mock_table.execute.return_value = mock_response

        mock_supabase_manager.get_client.return_value.table.return_value = mock_table

        result = repository.get_user_fact_performance("user123", "7+8")

        assert result is None

    def test_get_all_user_performances(self, repository, mock_supabase_manager):
        """Test getting all user performances."""
        # Mock response data
        mock_data = [
            {
                "id": "mock-uuid-1",
                "user_id": "user123",
                "fact_key": "7+8",
                "total_attempts": 5,
                "correct_attempts": 4,
                "average_response_time_ms": 2500,
                "repetition_number": 2,
                "easiness_factor": "2.60",
                "interval_days": 6,
                "next_review_date": datetime.now().isoformat(),
                "last_attempted": datetime.now().isoformat(),
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
            },
            {
                "id": "mock-uuid-2",
                "user_id": "user123",
                "fact_key": "9+6",
                "total_attempts": 3,
                "correct_attempts": 2,
                "average_response_time_ms": 3500,
                "repetition_number": 1,
                "easiness_factor": "2.30",
                "interval_days": 1,
                "next_review_date": datetime.now().isoformat(),
                "last_attempted": datetime.now().isoformat(),
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
            },
        ]

        # Mock Supabase response
        mock_response = Mock()
        mock_response.data = mock_data

        mock_table = Mock()
        mock_table.select.return_value = mock_table
        mock_table.eq.return_value = mock_table
        mock_table.order.return_value = mock_table
        mock_table.execute.return_value = mock_response

        mock_supabase_manager.get_client.return_value.table.return_value = mock_table

        result = repository.get_all_user_performances("user123")

        assert len(result) == 2
        assert result[0].fact_key == "7+8"
        assert result[1].fact_key == "9+6"

    def test_get_facts_due_for_review(self, repository, mock_supabase_manager):
        """Test getting facts due for review."""
        # Mock response data for facts due
        yesterday = datetime.now() - timedelta(days=1)
        mock_data = [
            {
                "id": "mock-uuid-due",
                "user_id": "user123",
                "fact_key": "7+8",
                "total_attempts": 5,
                "correct_attempts": 4,
                "average_response_time_ms": 2500,
                "repetition_number": 2,
                "easiness_factor": "2.60",
                "interval_days": 6,
                "next_review_date": yesterday.isoformat(),
                "last_attempted": yesterday.isoformat(),
                "created_at": yesterday.isoformat(),
                "updated_at": yesterday.isoformat(),
            }
        ]

        # Mock Supabase response
        mock_response = Mock()
        mock_response.data = mock_data

        mock_table = Mock()
        mock_table.select.return_value = mock_table
        mock_table.eq.return_value = mock_table
        mock_table.lte.return_value = mock_table
        mock_table.order.return_value = mock_table
        mock_table.limit.return_value = mock_table
        mock_table.execute.return_value = mock_response

        mock_supabase_manager.get_client.return_value.table.return_value = mock_table

        result = repository.get_facts_due_for_review("user123", limit=10)

        assert len(result) == 1
        assert result[0].fact_key == "7+8"
        # Verify the query used lte (less than or equal) with current time
        mock_table.lte.assert_called_once()

    def test_get_weak_facts(self, repository, mock_supabase_manager):
        """Test getting weak facts (low ease factor)."""
        # Mock response data for weak facts
        mock_data = [
            {
                "id": "mock-uuid-weak",
                "user_id": "user123",
                "fact_key": "9+8",
                "total_attempts": 10,
                "correct_attempts": 3,
                "average_response_time_ms": 5500,
                "repetition_number": 0,
                "easiness_factor": "1.50",  # Low ease factor
                "interval_days": 1,
                "next_review_date": datetime.now().isoformat(),
                "last_attempted": datetime.now().isoformat(),
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
            }
        ]

        # Mock Supabase response
        mock_response = Mock()
        mock_response.data = mock_data

        mock_table = Mock()
        mock_table.select.return_value = mock_table
        mock_table.eq.return_value = mock_table
        mock_table.order.return_value = mock_table
        mock_table.limit.return_value = mock_table
        mock_table.execute.return_value = mock_response

        mock_supabase_manager.get_client.return_value.table.return_value = mock_table

        result = repository.get_weak_facts("user123", (1, 10), 5)

        assert len(result) == 1
        assert result[0].fact_key == "9+8"
        assert result[0].easiness_factor == Decimal("1.50")
        # Verify ordering by ease factor ascending (weakest first)
        mock_table.order.assert_called_with("easiness_factor", desc=False)

    def test_upsert_fact_performance(self, repository, mock_supabase_manager):
        """Test upserting fact performance."""
        # Create performance to upsert
        performance = MathFactPerformance.create_new("user123", "7+8")
        performance.update_performance(True, 2500)

        # Mock response
        mock_response = Mock()
        mock_response.data = [performance.to_dict()]

        mock_table = Mock()
        mock_table.upsert.return_value = mock_table
        mock_table.execute.return_value = mock_response

        mock_supabase_manager.get_client.return_value.table.return_value = mock_table

        result = repository.upsert_fact_performance(performance)

        assert result is not None
        assert result.user_id == "user123"
        assert result.fact_key == "7+8"
        mock_table.upsert.assert_called_once()

    def test_create_fact_attempt(self, repository, mock_supabase_manager):
        """Test creating fact attempt."""
        # Create attempt
        attempt = MathFactAttempt.create_new(
            user_id="user123",
            fact_key="7+8",
            operand1=7,
            operand2=8,
            user_answer=15,
            correct_answer=15,
            is_correct=True,
            response_time_ms=2500,
            sm2_grade=4,
        )

        # Mock response
        mock_response = Mock()
        mock_response.data = [attempt.to_dict()]

        mock_table = Mock()
        mock_table.insert.return_value = mock_table
        mock_table.execute.return_value = mock_response

        mock_supabase_manager.get_client.return_value.table.return_value = mock_table

        result = repository.create_fact_attempt(attempt)

        assert result is not None
        assert result.user_id == "user123"
        assert result.fact_key == "7+8"
        mock_table.insert.assert_called_once()

    def test_upsert_fact_performance_with_attempt(
        self, repository, mock_supabase_manager
    ):
        """Test atomic upsert of performance with attempt."""
        # Create performance and attempt
        performance = MathFactPerformance.create_new("user123", "7+8")
        performance.update_performance(True, 2500)

        attempt = MathFactAttempt.create_new(
            user_id="user123",
            fact_key="7+8",
            operand1=7,
            operand2=8,
            user_answer=15,
            correct_answer=15,
            is_correct=True,
            response_time_ms=2500,
            sm2_grade=4,
        )

        # Mock responses
        mock_performance_response = Mock()
        mock_performance_response.data = [performance.to_dict()]

        mock_attempt_response = Mock()
        mock_attempt_response.data = [attempt.to_dict()]

        # Mock client and tables
        mock_client = Mock()
        mock_performance_table = Mock()
        mock_attempt_table = Mock()

        mock_performance_table.upsert.return_value = mock_performance_table
        mock_performance_table.execute.return_value = mock_performance_response

        mock_attempt_table.insert.return_value = mock_attempt_table
        mock_attempt_table.execute.return_value = mock_attempt_response

        def table_selector(table_name):
            if table_name == "math_fact_performances":
                return mock_performance_table
            elif table_name == "math_fact_attempts":
                return mock_attempt_table
            return Mock()

        mock_client.table.side_effect = table_selector
        mock_supabase_manager.get_client.return_value = mock_client

        result = repository.upsert_fact_performance_with_attempt(performance, attempt)

        assert result is not None
        mock_performance_table.upsert.assert_called_once()
        mock_attempt_table.insert.assert_called_once()

    def test_get_user_fact_attempts(self, repository, mock_supabase_manager):
        """Test getting user fact attempts."""
        # Mock response data
        mock_data = [
            {
                "id": 1,
                "user_id": "user123",
                "fact_key": "7+8",
                "operand1": 7,
                "operand2": 8,
                "user_answer": 15,
                "correct_answer": 15,
                "is_correct": True,
                "response_time_ms": 2500,
                "incorrect_attempts_in_session": 0,
                "sm2_grade": 4,
                "attempted_at": datetime.now().isoformat(),
            }
        ]

        # Mock Supabase response
        mock_response = Mock()
        mock_response.data = mock_data

        mock_table = Mock()
        mock_table.select.return_value = mock_table
        mock_table.eq.return_value = mock_table
        mock_table.order.return_value = mock_table
        mock_table.limit.return_value = mock_table
        mock_table.execute.return_value = mock_response

        mock_supabase_manager.get_client.return_value.table.return_value = mock_table

        result = repository.get_user_fact_attempts("user123", fact_key="7+8", limit=10)

        assert len(result) == 1
        assert result[0].user_id == "user123"
        assert result[0].fact_key == "7+8"
        assert result[0].is_correct is True

    def test_batch_upsert_fact_performances(self, repository, mock_supabase_manager):
        """Test batch upserting fact performances."""
        session_attempts = [
            (7, 8, True, 2500, 0),  # 7+8 correct
            (9, 6, False, 5000, 2),  # 9+6 incorrect after 2 tries
            (7, 8, True, 2000, 1),  # 7+8 correct again after 1 mistake
        ]

        # Mock responses for batch operations
        mock_upsert_response = Mock()
        mock_upsert_response.data = []

        mock_insert_response = Mock()
        mock_insert_response.data = []

        # Mock client and tables
        mock_client = Mock()
        mock_performance_table = Mock()
        mock_attempt_table = Mock()

        mock_performance_table.upsert.return_value = mock_performance_table
        mock_performance_table.execute.return_value = mock_upsert_response

        mock_attempt_table.insert.return_value = mock_attempt_table
        mock_attempt_table.execute.return_value = mock_insert_response

        def table_selector(table_name):
            if table_name == "math_fact_performances":
                return mock_performance_table
            elif table_name == "math_fact_attempts":
                return mock_attempt_table
            return Mock()

        mock_client.table.side_effect = table_selector
        mock_supabase_manager.get_client.return_value = mock_client

        # Mock get_user_fact_performance calls:
        # First calls during processing return None (new facts)
        # Final calls return updated performances
        updated_performances = [
            MathFactPerformance.create_new("user123", "7+8"),
            MathFactPerformance.create_new("user123", "9+6"),
        ]

        # Mock sequence: None for initial checks, then return updated performances for final results
        get_calls = [None, None, updated_performances[0], updated_performances[1]]
        repository.get_user_fact_performance = Mock(side_effect=get_calls)

        result = repository.batch_upsert_fact_performances("user123", session_attempts)

        assert len(result) == 2
        mock_performance_table.upsert.assert_called_once()
        mock_attempt_table.insert.assert_called_once()

    def test_authentication_required(self, mock_supabase_manager):
        """Test that authentication is required for repository operations."""
        # Mock unauthenticated state
        mock_supabase_manager.is_authenticated.return_value = False

        repository = MathFactRepository(mock_supabase_manager)

        # Should return None for unauthenticated calls (decorator behavior)
        result = repository.get_user_fact_performance("user123", "7+8")
        assert result is None

    def test_error_handling(self, repository, mock_supabase_manager):
        """Test error handling in repository operations."""
        # Mock exception during database operation
        mock_table = Mock()
        mock_table.select.side_effect = Exception("Database error")
        mock_supabase_manager.get_client.return_value.table.return_value = mock_table

        result = repository.get_user_fact_performance("user123", "7+8")

        # Should return None on error
        assert result is None
