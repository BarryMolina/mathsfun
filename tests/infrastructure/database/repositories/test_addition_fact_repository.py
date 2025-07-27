"""Tests for AdditionFactRepository batch operations."""

import pytest
from unittest.mock import Mock, MagicMock, call
from datetime import datetime
from src.infrastructure.database.repositories.addition_fact_repository import (
    AdditionFactRepository,
)
from src.domain.models.addition_fact_performance import AdditionFactPerformance
from src.domain.models.mastery_level import MasteryLevel


@pytest.fixture
def mock_supabase_manager():
    """Create mock Supabase manager for testing."""
    manager = Mock()
    manager.is_authenticated.return_value = True
    return manager


@pytest.fixture
def mock_client():
    """Create mock Supabase client."""
    client = Mock()
    return client


@pytest.fixture
def repository(mock_supabase_manager, mock_client):
    """Create repository with mock dependencies."""
    mock_supabase_manager.get_client.return_value = mock_client
    return AdditionFactRepository(mock_supabase_manager)


@pytest.fixture
def sample_session_attempts():
    """Create sample session attempts for testing."""
    return [
        (3, 5, True, 2500),  # 3+5 correct
        (3, 5, False, 4000),  # 3+5 incorrect
        (7, 8, True, 3000),  # 7+8 correct
        (1, 9, False, 5000),  # 1+9 incorrect
        (3, 5, True, 2200),  # 3+5 correct again
    ]


class TestAdditionFactRepositoryBatchOperations:
    """Test batch operations for performance improvement."""

    def test_batch_upsert_fact_performances_empty_attempts(self, repository):
        """Test batch upsert with empty attempts list."""
        result = repository.batch_upsert_fact_performances("user-123", [])
        assert result == []

    def test_batch_upsert_fact_performances_new_facts(
        self, repository, mock_client, sample_session_attempts
    ):
        """Test batch upsert with all new facts."""
        # Mock no existing performances
        mock_table = Mock()
        mock_client.table.return_value = mock_table

        # Mock bulk get returning empty
        mock_table.select.return_value.eq.return_value.in_.return_value.execute.return_value.data = (
            []
        )

        # Mock successful upsert
        mock_table.upsert.return_value.execute.return_value = Mock()

        result = repository.batch_upsert_fact_performances(
            "user-123", sample_session_attempts
        )

        # Should return 3 unique facts (3+5, 7+8, 1+9)
        assert len(result) == 3

        # Verify fact keys are correct
        fact_keys = {perf.fact_key for perf in result}
        assert fact_keys == {"3+5", "7+8", "1+9"}

        # Verify bulk operations were called
        mock_table.select.assert_called_once()
        mock_table.upsert.assert_called_once()

    def test_batch_upsert_fact_performances_existing_facts(
        self, repository, mock_client, sample_session_attempts
    ):
        """Test batch upsert with existing facts."""
        # Mock existing performance for 3+5
        existing_perf_data = {
            "id": "perf-123",
            "user_id": "user-123",
            "fact_key": "3+5",
            "total_attempts": 5,
            "correct_attempts": 3,
            "total_response_time_ms": 15000,
            "mastery_level": "learning",
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00",
            "last_attempted": "2024-01-01T00:00:00",
        }

        mock_table = Mock()
        mock_client.table.return_value = mock_table

        # Mock bulk get returning existing performance
        mock_table.select.return_value.eq.return_value.in_.return_value.execute.return_value.data = [
            existing_perf_data
        ]

        # Mock successful upsert
        mock_table.upsert.return_value.execute.return_value = Mock()

        result = repository.batch_upsert_fact_performances(
            "user-123", sample_session_attempts
        )

        # Should return 3 unique facts
        assert len(result) == 3

        # Verify existing fact was updated (3+5 had 3 more attempts: 2 correct, 1 incorrect)
        fact_3_5 = next(perf for perf in result if perf.fact_key == "3+5")
        assert fact_3_5.total_attempts == 8  # 5 existing + 3 new
        assert fact_3_5.correct_attempts == 5  # 3 existing + 2 new correct

    def test_aggregate_session_attempts(self, repository, sample_session_attempts):
        """Test session attempts aggregation logic."""
        aggregates = repository._aggregate_session_attempts(sample_session_attempts)

        # Should have 3 unique facts
        assert len(aggregates) == 3
        assert "3+5" in aggregates
        assert "7+8" in aggregates
        assert "1+9" in aggregates

        # Check 3+5 aggregation (3 attempts: 2 correct, 1 incorrect)
        fact_3_5 = aggregates["3+5"]
        assert fact_3_5["total_count"] == 3
        assert fact_3_5["correct_count"] == 2
        assert len(fact_3_5["response_times"]) == 3
        assert fact_3_5["response_times"] == [2500, 4000, 2200]

        # Check 7+8 aggregation (1 attempt: 1 correct)
        fact_7_8 = aggregates["7+8"]
        assert fact_7_8["total_count"] == 1
        assert fact_7_8["correct_count"] == 1

        # Check 1+9 aggregation (1 attempt: 0 correct)
        fact_1_9 = aggregates["1+9"]
        assert fact_1_9["total_count"] == 1
        assert fact_1_9["correct_count"] == 0

    def test_bulk_get_fact_performances(self, repository, mock_client):
        """Test bulk fetching of existing performances."""
        mock_table = Mock()
        mock_client.table.return_value = mock_table

        # Mock response with performance data
        perf_data = [
            {
                "id": "perf-123",
                "user_id": "user-123",
                "fact_key": "3+5",
                "total_attempts": 5,
                "correct_attempts": 3,
                "total_response_time_ms": 15000,
                "mastery_level": "learning",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
                "last_attempted": "2024-01-01T00:00:00",
            }
        ]
        mock_table.select.return_value.eq.return_value.in_.return_value.execute.return_value.data = (
            perf_data
        )

        fact_keys = ["3+5", "7+8"]
        result = repository._bulk_get_fact_performances("user-123", fact_keys)

        assert result is not None
        assert len(result) == 1
        assert result[0].fact_key == "3+5"
        assert result[0].total_attempts == 5

        # Verify correct query was made
        mock_table.select.assert_called_with("*")
        mock_table.select.return_value.eq.assert_called_with("user_id", "user-123")
        mock_table.select.return_value.eq.return_value.in_.assert_called_with(
            "fact_key", fact_keys
        )

    def test_apply_aggregated_stats(self, repository):
        """Test applying aggregated statistics to performance object."""
        # Create a performance object
        perf = AdditionFactPerformance.create_new("user-123", "3+5")

        # Create aggregated stats
        stats = {
            "total_count": 3,
            "correct_count": 2,
            "response_times": [2500, 4000, 2200],
            "timestamps": [datetime.now()] * 3,
        }

        # Apply stats
        repository._apply_aggregated_stats(perf, stats)

        # Verify the performance was updated correctly
        assert perf.total_attempts == 3
        assert perf.correct_attempts == 2
        assert abs(perf.accuracy - 66.7) < 0.1  # 2/3 * 100, approximately 66.7

    def test_bulk_upsert_records(self, repository, mock_client):
        """Test bulk upsert database operation."""
        mock_table = Mock()
        mock_client.table.return_value = mock_table
        mock_table.upsert.return_value.execute.return_value = Mock()

        records = [
            {"user_id": "user-123", "fact_key": "3+5", "total_attempts": 3},
            {"user_id": "user-123", "fact_key": "7+8", "total_attempts": 1},
        ]

        repository._bulk_upsert_records(records)

        # Verify upsert was called with correct parameters
        mock_table.upsert.assert_called_once_with(
            records, on_conflict="user_id,fact_key"
        )

    def test_batch_upsert_not_authenticated(self, mock_supabase_manager):
        """Test batch upsert when user is not authenticated."""
        mock_supabase_manager.is_authenticated.return_value = False
        repository = AdditionFactRepository(mock_supabase_manager)

        result = repository.batch_upsert_fact_performances(
            "user-123", [(3, 5, True, 2500)]
        )

        assert result is None  # Should return None when not authenticated

    def test_batch_upsert_database_error(self, repository, mock_client):
        """Test batch upsert handling database errors."""
        mock_table = Mock()
        mock_client.table.return_value = mock_table

        # Mock database error
        mock_table.select.return_value.eq.return_value.in_.return_value.execute.side_effect = Exception(
            "DB Error"
        )

        result = repository.batch_upsert_fact_performances(
            "user-123", [(3, 5, True, 2500)]
        )

        assert result == []  # Should return empty list on error


@pytest.mark.repository
class TestAdditionFactRepositoryBatchIntegration:
    """Integration tests for batch operations."""

    def test_batch_operations_performance_improvement(self, repository, mock_client):
        """Test that batch operations reduce database calls."""
        # Simulate 100 attempts (10x10 addition table)
        large_session = [
            (i, j, i + j < 15, 2000 + (i * j * 10))
            for i in range(1, 11)
            for j in range(1, 11)
        ]

        mock_table = Mock()
        mock_client.table.return_value = mock_table

        # Mock empty existing performances
        mock_table.select.return_value.eq.return_value.in_.return_value.execute.return_value.data = (
            []
        )
        mock_table.upsert.return_value.execute.return_value = Mock()

        repository.batch_upsert_fact_performances("user-123", large_session)

        # Verify only 2 database operations total:
        # 1. One bulk SELECT to fetch existing performances
        # 2. One bulk UPSERT to update all performances
        assert mock_table.select.call_count == 1
        assert mock_table.upsert.call_count == 1

        # This replaces what would have been 200+ individual database calls
        # (2 calls per attempt: 1 SELECT + 1 UPDATE/INSERT for each of 100 attempts)
