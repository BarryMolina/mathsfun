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

    def test_batch_upsert_id_consistency_mixed_records(
        self, repository, mock_client, sample_session_attempts
    ):
        """Test that all records in batch upsert have consistent ID handling."""
        # Mock existing performance for 3+5 with an ID
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

        # Mock bulk get returning one existing performance (3+5)
        mock_table.select.return_value.eq.return_value.in_.return_value.execute.return_value.data = [
            existing_perf_data
        ]

        # Mock successful upsert
        mock_table.upsert.return_value.execute.return_value = Mock()

        repository.batch_upsert_fact_performances("user-123", sample_session_attempts)

        # Verify upsert was called
        mock_table.upsert.assert_called_once()

        # Get the records that were passed to upsert
        upsert_call_args = mock_table.upsert.call_args
        upsert_records = upsert_call_args[0][0]  # First positional argument

        # All records should have consistent ID handling - either all have IDs or none do
        # For proper upsert behavior with on_conflict, all records should NOT have IDs
        for record in upsert_records:
            assert "id" not in record, f"Record should not contain 'id' field: {record}"
            # Verify required fields are present
            assert "user_id" in record
            assert "fact_key" in record
            assert "total_attempts" in record

    def test_batch_upsert_id_consistency_all_new_records(
        self, repository, mock_client, sample_session_attempts
    ):
        """Test that new records do not contain ID fields."""
        mock_table = Mock()
        mock_client.table.return_value = mock_table

        # Mock no existing performances
        mock_table.select.return_value.eq.return_value.in_.return_value.execute.return_value.data = (
            []
        )

        # Mock successful upsert
        mock_table.upsert.return_value.execute.return_value = Mock()

        repository.batch_upsert_fact_performances("user-123", sample_session_attempts)

        # Verify upsert was called
        mock_table.upsert.assert_called_once()

        # Get the records that were passed to upsert
        upsert_call_args = mock_table.upsert.call_args
        upsert_records = upsert_call_args[0][0]  # First positional argument

        # All records should be new (no IDs)
        for record in upsert_records:
            assert (
                "id" not in record
            ), f"New record should not contain 'id' field: {record}"
            assert "user_id" in record
            assert "fact_key" in record

    def test_batch_upsert_id_consistency_all_existing_records(
        self, repository, mock_client
    ):
        """Test that existing records do not contain ID fields when batched."""
        # Create session with only one fact that exists
        session_attempts = [(3, 5, True, 2500), (3, 5, False, 3000)]

        # Mock existing performance for 3+5 with an ID
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

        # Mock bulk get returning the existing performance
        mock_table.select.return_value.eq.return_value.in_.return_value.execute.return_value.data = [
            existing_perf_data
        ]

        # Mock successful upsert
        mock_table.upsert.return_value.execute.return_value = Mock()

        repository.batch_upsert_fact_performances("user-123", session_attempts)

        # Verify upsert was called
        mock_table.upsert.assert_called_once()

        # Get the records that were passed to upsert
        upsert_call_args = mock_table.upsert.call_args
        upsert_records = upsert_call_args[0][0]  # First positional argument

        # Even existing records should not have IDs in the upsert payload
        assert len(upsert_records) == 1
        record = upsert_records[0]
        assert (
            "id" not in record
        ), f"Existing record should not contain 'id' field: {record}"
        assert record["user_id"] == "user-123"
        assert record["fact_key"] == "3+5"


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


class TestAdditionFactRepositoryIndividualMethods:
    """Test individual CRUD methods."""

    def test_get_user_fact_performance_success(self, repository, mock_client):
        """Test successful retrieval of a single fact performance."""
        # Mock successful response
        mock_response_data = {
            "id": 1,
            "user_id": "test_user",
            "fact_key": "3+5",
            "addend1": 3,
            "addend2": 5,
            "correct_attempts": 5,
            "total_attempts": 7,
            "total_response_time_ms": 15000,
            "fastest_correct_time_ms": 2000,
            "mastery_level": "practicing",
            "created_at": "2023-01-01T10:00:00Z",
            "last_attempted": "2023-01-01T12:00:00Z"
        }
        mock_client.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = [mock_response_data]
        
        result = repository.get_user_fact_performance("test_user", "3+5")
        
        assert result is not None
        assert result.user_id == "test_user"
        assert result.fact_key == "3+5"
        assert result.addend1 == 3
        assert result.addend2 == 5
        assert result.correct_attempts == 5
        assert result.total_attempts == 7

    def test_get_user_fact_performance_not_found(self, repository, mock_client):
        """Test retrieval when fact performance doesn't exist."""
        # Mock empty response
        mock_client.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = []
        
        result = repository.get_user_fact_performance("test_user", "3+5")
        
        assert result is None

    def test_get_user_fact_performance_exception(self, repository, mock_client):
        """Test retrieval with database exception."""
        # Mock exception
        mock_client.table.return_value.select.return_value.eq.return_value.eq.side_effect = Exception("Database error")
        
        result = repository.get_user_fact_performance("test_user", "3+5")
        
        assert result is None

    def test_get_user_fact_performances_success(self, repository, mock_client):
        """Test successful retrieval of multiple fact performances."""
        # Mock successful response
        mock_response_data = [
            {
                "id": 1,
                "user_id": "test_user",
                "fact_key": "3+5",
                "addend1": 3,
                "addend2": 5,
                "correct_attempts": 5,
                "total_attempts": 7,
                "total_response_time_ms": 15000,
                "fastest_correct_time_ms": 2000,
                "mastery_level": "practicing",
                "created_at": "2023-01-01T10:00:00Z",
                "last_attempted": "2023-01-01T12:00:00Z"
            },
            {
                "id": 2,
                "user_id": "test_user",
                "fact_key": "7+8",
                "addend1": 7,
                "addend2": 8,
                "correct_attempts": 3,
                "total_attempts": 4,
                "total_response_time_ms": 12000,
                "fastest_correct_time_ms": 2800,
                "mastery_level": "learning",
                "created_at": "2023-01-01T10:00:00Z",
                "last_attempted": "2023-01-01T12:00:00Z"
            }
        ]
        mock_client.table.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value.data = mock_response_data
        
        result = repository.get_user_fact_performances("test_user")
        
        assert len(result) == 2
        assert result[0].fact_key == "3+5"
        assert result[1].fact_key == "7+8"

    def test_get_user_fact_performances_with_mastery_filter(self, repository, mock_client):
        """Test retrieval with mastery level filter."""
        mock_response_data = []
        mock_query = mock_client.table.return_value.select.return_value.eq.return_value
        mock_query.eq.return_value.order.return_value.limit.return_value.execute.return_value.data = mock_response_data
        
        result = repository.get_user_fact_performances("test_user", mastery_level=MasteryLevel.PRACTICING)
        
        # Verify mastery level filter was applied
        mock_query.eq.assert_called_with("mastery_level", "practicing")
        assert len(result) == 0

    def test_get_user_fact_performances_exception(self, repository, mock_client):
        """Test retrieval with database exception."""
        # Mock exception
        mock_client.table.return_value.select.return_value.eq.side_effect = Exception("Database error")
        
        result = repository.get_user_fact_performances("test_user")
        
        assert result == []

    def test_create_fact_performance_success(self, repository, mock_client):
        """Test successful creation of fact performance."""
        # Create test performance
        performance = AdditionFactPerformance.create_new(
            user_id="test_user",
            addend1=3,
            addend2=5
        )
        
        # Mock successful response
        mock_response_data = performance.to_dict()
        mock_response_data["id"] = 1
        mock_client.table.return_value.insert.return_value.execute.return_value.data = [mock_response_data]
        
        result = repository.create_fact_performance(performance)
        
        assert result is not None
        assert result.id == 1
        assert result.user_id == "test_user"
        assert result.fact_key == "3+5"

    def test_create_fact_performance_exception(self, repository, mock_client):
        """Test creation with database exception."""
        performance = AdditionFactPerformance.create_new(
            user_id="test_user",
            addend1=3,
            addend2=5
        )
        
        # Mock exception
        mock_client.table.return_value.insert.side_effect = Exception("Database error")
        
        result = repository.create_fact_performance(performance)
        
        assert result is None

    def test_update_fact_performance_success(self, repository, mock_client):
        """Test successful update of fact performance."""
        # Create test performance with ID
        performance = AdditionFactPerformance.create_new(
            user_id="test_user",
            addend1=3,
            addend2=5
        )
        performance.id = 1
        performance.correct_attempts = 10
        
        # Mock successful response
        mock_response_data = performance.to_dict()
        mock_client.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [mock_response_data]
        
        result = repository.update_fact_performance(performance)
        
        assert result is not None
        assert result.correct_attempts == 10

    def test_update_fact_performance_no_id(self, repository):
        """Test update with performance that has no ID."""
        performance = AdditionFactPerformance.create_new(
            user_id="test_user",
            addend1=3,
            addend2=5
        )
        # No ID set
        
        result = repository.update_fact_performance(performance)
        
        assert result is None

    def test_update_fact_performance_exception(self, repository, mock_client):
        """Test update with database exception."""
        performance = AdditionFactPerformance.create_new(
            user_id="test_user",
            addend1=3,
            addend2=5
        )
        performance.id = 1
        
        # Mock exception
        mock_client.table.return_value.update.side_effect = Exception("Database error")
        
        result = repository.update_fact_performance(performance)
        
        assert result is None

    def test_upsert_fact_performance_success(self, repository, mock_client):
        """Test successful upsert of fact performance."""
        performance = AdditionFactPerformance.create_new(
            user_id="test_user",
            addend1=3,
            addend2=5
        )
        
        # Mock successful response
        mock_response_data = performance.to_dict()
        mock_response_data["id"] = 1
        mock_client.table.return_value.upsert.return_value.execute.return_value.data = [mock_response_data]
        
        result = repository.upsert_fact_performance(performance)
        
        assert result is not None
        assert result.id == 1

    def test_upsert_fact_performance_exception(self, repository, mock_client):
        """Test upsert with database exception."""
        performance = AdditionFactPerformance.create_new(
            user_id="test_user",
            addend1=3,
            addend2=5
        )
        
        # Mock exception
        mock_client.table.return_value.upsert.side_effect = Exception("Database error")
        
        result = repository.upsert_fact_performance(performance)
        
        assert result is None

    def test_get_weak_facts_success(self, repository, mock_client):
        """Test successful retrieval of weak facts."""
        mock_response_data = [
            {
                "id": 1,
                "user_id": "test_user",
                "fact_key": "7+8",
                "addend1": 7,
                "addend2": 8,
                "correct_attempts": 2,
                "total_attempts": 10,
                "total_response_time_ms": 30000,
                "fastest_correct_time_ms": 5000,
                "mastery_level": "learning",
                "created_at": "2023-01-01T10:00:00Z",
                "last_attempted": "2023-01-01T12:00:00Z"
            }
        ]
        mock_query = mock_client.table.return_value.select.return_value.eq.return_value
        mock_query.lte.return_value.order.return_value.limit.return_value.execute.return_value.data = mock_response_data
        
        result = repository.get_weak_facts("test_user")
        
        assert len(result) == 1
        assert result[0].fact_key == "7+8"

    def test_get_weak_facts_with_custom_params(self, repository, mock_client):
        """Test retrieval of weak facts with custom parameters."""
        mock_response_data = []
        mock_query = mock_client.table.return_value.select.return_value.eq.return_value
        mock_query.lte.return_value.order.return_value.limit.return_value.execute.return_value.data = mock_response_data
        
        result = repository.get_weak_facts("test_user", accuracy_threshold=0.5, limit=5)
        
        assert result == []

    def test_get_weak_facts_exception(self, repository, mock_client):
        """Test get weak facts with database exception."""
        mock_client.table.return_value.select.return_value.eq.side_effect = Exception("Database error")
        
        result = repository.get_weak_facts("test_user")
        
        assert result == []

    def test_get_mastered_facts_success(self, repository, mock_client):
        """Test successful retrieval of mastered facts."""
        mock_response_data = [
            {
                "id": 1,
                "user_id": "test_user",
                "fact_key": "3+5",
                "addend1": 3,
                "addend2": 5,
                "correct_attempts": 10,
                "total_attempts": 10,
                "total_response_time_ms": 20000,
                "fastest_correct_time_ms": 1500,
                "mastery_level": "mastered",
                "created_at": "2023-01-01T10:00:00Z",
                "last_attempted": "2023-01-01T12:00:00Z"
            }
        ]
        mock_query = mock_client.table.return_value.select.return_value.eq.return_value
        mock_query.gte.return_value.lte.return_value.order.return_value.limit.return_value.execute.return_value.data = mock_response_data
        
        result = repository.get_mastered_facts("test_user")
        
        assert len(result) == 1
        assert result[0].fact_key == "3+5"

    def test_get_mastered_facts_exception(self, repository, mock_client):
        """Test get mastered facts with database exception."""
        mock_client.table.return_value.select.return_value.eq.side_effect = Exception("Database error")
        
        result = repository.get_mastered_facts("test_user")
        
        assert result == []

    def test_get_performance_summary_success(self, repository, mock_client):
        """Test successful retrieval of performance summary."""
        mock_response_data = [
            {
                "id": 1,
                "user_id": "test_user",
                "fact_key": "3+5",
                "correct_attempts": 8,
                "total_attempts": 10,
                "mastery_level": "practicing"
            },
            {
                "id": 2,
                "user_id": "test_user", 
                "fact_key": "7+8",
                "correct_attempts": 10,
                "total_attempts": 10,
                "mastery_level": "mastered"
            }
        ]
        mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = mock_response_data
        
        result = repository.get_performance_summary("test_user")
        
        assert "total_facts" in result
        assert "mastery_breakdown" in result
        assert result["total_facts"] == 2
        assert "mastered" in result["mastery_breakdown"]
        assert "practicing" in result["mastery_breakdown"]

    def test_get_performance_summary_exception(self, repository, mock_client):
        """Test get performance summary with database exception."""
        mock_client.table.return_value.select.side_effect = Exception("Database error")
        
        result = repository.get_performance_summary("test_user")
        
        assert result == {
            "total_facts": 0,
            "mastery_breakdown": {},
            "average_accuracy": 0.0,
            "total_attempts": 0
        }
