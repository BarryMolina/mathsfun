"""Tests for AdditionFactPerformance model."""

import pytest
from datetime import datetime
from src.domain.models.addition_fact_performance import AdditionFactPerformance
from src.domain.models.mastery_level import MasteryLevel


@pytest.fixture
def sample_timestamp():
    """Create sample timestamp for testing."""
    return datetime(2023, 1, 1, 12, 15, 30)


@pytest.fixture
def sample_performance(sample_timestamp):
    """Create sample addition fact performance for testing."""
    return AdditionFactPerformance(
        id="perf-123",
        user_id="user-456",
        fact_key="7+8",
        total_attempts=10,
        correct_attempts=8,
        total_response_time_ms=25000,  # 25 seconds total
        fastest_response_ms=2500,
        slowest_response_ms=4000,
        last_attempted=sample_timestamp,
        mastery_level=MasteryLevel.PRACTICING,
        created_at=sample_timestamp,
        updated_at=sample_timestamp
    )


class TestAdditionFactPerformanceInit:
    """Test AdditionFactPerformance initialization."""

    def test_init_minimal_required_fields(self):
        """Test initialization with minimal required fields."""
        performance = AdditionFactPerformance(
            id="test-id",
            user_id="test-user",
            fact_key="3+5"
        )
        
        assert performance.id == "test-id"
        assert performance.user_id == "test-user"
        assert performance.fact_key == "3+5"
        assert performance.total_attempts == 0
        assert performance.correct_attempts == 0
        assert performance.total_response_time_ms == 0
        assert performance.fastest_response_ms is None
        assert performance.slowest_response_ms is None
        assert performance.last_attempted is None
        assert performance.mastery_level == MasteryLevel.LEARNING
        assert performance.created_at is None
        assert performance.updated_at is None

    def test_init_all_fields(self, sample_timestamp):
        """Test initialization with all fields."""
        performance = AdditionFactPerformance(
            id="test-id",
            user_id="test-user",
            fact_key="9+9",
            total_attempts=5,
            correct_attempts=4,
            total_response_time_ms=12000,
            fastest_response_ms=2000,
            slowest_response_ms=3500,
            last_attempted=sample_timestamp,
            mastery_level=MasteryLevel.MASTERED,
            created_at=sample_timestamp,
            updated_at=sample_timestamp
        )
        
        assert performance.id == "test-id"
        assert performance.user_id == "test-user"
        assert performance.fact_key == "9+9"
        assert performance.total_attempts == 5
        assert performance.correct_attempts == 4
        assert performance.total_response_time_ms == 12000
        assert performance.fastest_response_ms == 2000
        assert performance.slowest_response_ms == 3500
        assert performance.last_attempted == sample_timestamp
        assert performance.mastery_level == MasteryLevel.MASTERED
        assert performance.created_at == sample_timestamp
        assert performance.updated_at == sample_timestamp


class TestAdditionFactPerformanceProperties:
    """Test AdditionFactPerformance computed properties."""

    def test_accuracy_property_normal_case(self):
        """Test accuracy calculation for normal case."""
        performance = AdditionFactPerformance(
            id="test-id",
            user_id="test-user", 
            fact_key="6+4",
            total_attempts=10,
            correct_attempts=8
        )
        
        assert performance.accuracy == 80.0

    def test_accuracy_property_perfect_score(self):
        """Test accuracy calculation for perfect score."""
        performance = AdditionFactPerformance(
            id="test-id",
            user_id="test-user",
            fact_key="6+4", 
            total_attempts=5,
            correct_attempts=5
        )
        
        assert performance.accuracy == 100.0

    def test_accuracy_property_zero_attempts(self):
        """Test accuracy calculation when no attempts."""
        performance = AdditionFactPerformance(
            id="test-id",
            user_id="test-user",
            fact_key="6+4",
            total_attempts=0,
            correct_attempts=0
        )
        
        assert performance.accuracy == 0.0

    def test_average_response_time_ms_property(self):
        """Test average response time calculation."""
        performance = AdditionFactPerformance(
            id="test-id",
            user_id="test-user",
            fact_key="6+4",
            correct_attempts=4,
            total_response_time_ms=12000  # 12 seconds total
        )
        
        assert performance.average_response_time_ms == 3000.0  # 3 seconds average

    def test_average_response_time_ms_no_correct(self):
        """Test average response time when no correct attempts."""
        performance = AdditionFactPerformance(
            id="test-id",
            user_id="test-user",
            fact_key="6+4",
            correct_attempts=0,
            total_response_time_ms=0
        )
        
        assert performance.average_response_time_ms == 0.0

    def test_average_response_time_seconds_property(self):
        """Test average response time in seconds."""
        performance = AdditionFactPerformance(
            id="test-id",
            user_id="test-user", 
            fact_key="6+4",
            correct_attempts=2,
            total_response_time_ms=5000  # 5 seconds total
        )
        
        assert performance.average_response_time_seconds == 2.5  # 2.5 seconds average


class TestAdditionFactPerformanceUpdatePerformance:
    """Test update_performance method."""

    def test_update_performance_correct_attempt(self, sample_timestamp):
        """Test updating performance with correct attempt."""
        performance = AdditionFactPerformance(
            id="test-id",
            user_id="test-user",
            fact_key="5+3",
            total_attempts=2,
            correct_attempts=1,
            total_response_time_ms=3000,
            fastest_response_ms=3000,
            slowest_response_ms=3000
        )
        
        performance.update_performance(True, 2500, sample_timestamp)
        
        assert performance.total_attempts == 3
        assert performance.correct_attempts == 2
        assert performance.total_response_time_ms == 5500
        assert performance.fastest_response_ms == 2500  # New fastest
        assert performance.slowest_response_ms == 3000  # Still slowest
        assert performance.last_attempted == sample_timestamp

    def test_update_performance_incorrect_attempt(self, sample_timestamp):
        """Test updating performance with incorrect attempt."""
        performance = AdditionFactPerformance(
            id="test-id",
            user_id="test-user",
            fact_key="5+3",
            total_attempts=2,
            correct_attempts=2,
            total_response_time_ms=6000,
            fastest_response_ms=2500,
            slowest_response_ms=3500
        )
        
        performance.update_performance(False, 4000, sample_timestamp)
        
        assert performance.total_attempts == 3
        assert performance.correct_attempts == 2  # No change
        assert performance.total_response_time_ms == 6000  # No change
        assert performance.fastest_response_ms == 2500  # No change
        assert performance.slowest_response_ms == 3500  # No change
        assert performance.last_attempted == sample_timestamp

    def test_update_performance_first_correct_attempt(self):
        """Test updating performance for first correct attempt."""
        performance = AdditionFactPerformance(
            id="test-id",
            user_id="test-user",
            fact_key="5+3"
        )
        
        performance.update_performance(True, 3000)
        
        assert performance.total_attempts == 1
        assert performance.correct_attempts == 1
        assert performance.total_response_time_ms == 3000
        assert performance.fastest_response_ms == 3000
        assert performance.slowest_response_ms == 3000
        assert performance.last_attempted is not None


class TestAdditionFactPerformanceMasteryLevel:
    """Test mastery level determination."""

    def test_determine_mastery_level_learning_few_attempts(self):
        """Test mastery determination with few attempts."""
        performance = AdditionFactPerformance(
            id="test-id",
            user_id="test-user",
            fact_key="5+3",
            total_attempts=3,
            correct_attempts=3
        )
        
        assert performance.determine_mastery_level() == MasteryLevel.LEARNING

    def test_determine_mastery_level_learning_low_accuracy(self):
        """Test mastery determination with low accuracy."""
        performance = AdditionFactPerformance(
            id="test-id",
            user_id="test-user",
            fact_key="5+3", 
            total_attempts=10,
            correct_attempts=6  # 60% accuracy
        )
        
        assert performance.determine_mastery_level() == MasteryLevel.LEARNING

    def test_determine_mastery_level_practicing(self):
        """Test mastery determination for practicing level."""
        performance = AdditionFactPerformance(
            id="test-id",
            user_id="test-user",
            fact_key="5+3",
            total_attempts=8,
            correct_attempts=7  # 87.5% accuracy
        )
        
        assert performance.determine_mastery_level() == MasteryLevel.PRACTICING

    def test_determine_mastery_level_mastered(self):
        """Test mastery determination for mastered level."""
        performance = AdditionFactPerformance(
            id="test-id",
            user_id="test-user",
            fact_key="5+3",
            total_attempts=10,
            correct_attempts=10  # 100% accuracy
        )
        
        assert performance.determine_mastery_level() == MasteryLevel.MASTERED

    def test_determine_mastery_level_mastered_high_accuracy(self):
        """Test mastery determination with 95%+ accuracy."""
        performance = AdditionFactPerformance(
            id="test-id",
            user_id="test-user",
            fact_key="5+3",
            total_attempts=20,
            correct_attempts=19  # 95% accuracy
        )
        
        assert performance.determine_mastery_level() == MasteryLevel.MASTERED


class TestAdditionFactPerformanceCreateNew:
    """Test create_new class method."""

    def test_create_new_minimal(self):
        """Test creating new performance with minimal parameters."""
        performance = AdditionFactPerformance.create_new("user-123", "4+6")
        
        assert performance.user_id == "user-123"
        assert performance.fact_key == "4+6"
        assert performance.total_attempts == 0
        assert performance.correct_attempts == 0
        assert performance.mastery_level == MasteryLevel.LEARNING
        assert performance.created_at is not None
        assert performance.id is not None

    def test_create_new_with_id(self):
        """Test creating new performance with specific ID."""
        performance = AdditionFactPerformance.create_new(
            "user-123", "4+6", id="custom-id"
        )
        
        assert performance.id == "custom-id"
        assert performance.user_id == "user-123"
        assert performance.fact_key == "4+6"


class TestAdditionFactPerformanceSerialization:
    """Test serialization methods."""

    def test_to_dict(self, sample_performance):
        """Test converting to dictionary."""
        result = sample_performance.to_dict()
        
        expected = {
            "id": "perf-123",
            "user_id": "user-456",
            "fact_key": "7+8",
            "total_attempts": 10,
            "correct_attempts": 8,
            "total_response_time_ms": 25000,
            "fastest_response_ms": 2500,
            "slowest_response_ms": 4000,
            "last_attempted": "2023-01-01T12:15:30",
            "mastery_level": "practicing",
            "created_at": "2023-01-01T12:15:30",
            "updated_at": "2023-01-01T12:15:30"
        }
        
        assert result == expected

    def test_to_dict_with_none_values(self):
        """Test converting to dictionary with None values."""
        performance = AdditionFactPerformance(
            id="test-id",
            user_id="test-user",
            fact_key="1+1"
        )
        
        result = performance.to_dict()
        
        assert result["fastest_response_ms"] is None
        assert result["slowest_response_ms"] is None
        assert result["last_attempted"] is None
        assert result["created_at"] is None
        assert result["updated_at"] is None

    def test_from_dict_complete(self):
        """Test creating from complete dictionary."""
        data = {
            "id": "perf-456",
            "user_id": "user-789",
            "fact_key": "9+2",
            "total_attempts": 5,
            "correct_attempts": 4,
            "total_response_time_ms": 15000,
            "fastest_response_ms": 3000,
            "slowest_response_ms": 4000,
            "last_attempted": "2023-01-01T12:15:30",
            "mastery_level": "mastered",
            "created_at": "2023-01-01T12:15:30",
            "updated_at": "2023-01-01T12:15:30"
        }
        
        performance = AdditionFactPerformance.from_dict(data)
        
        assert performance.id == "perf-456"
        assert performance.user_id == "user-789"
        assert performance.fact_key == "9+2"
        assert performance.total_attempts == 5
        assert performance.correct_attempts == 4
        assert performance.total_response_time_ms == 15000
        assert performance.fastest_response_ms == 3000
        assert performance.slowest_response_ms == 4000
        assert performance.last_attempted == datetime(2023, 1, 1, 12, 15, 30)
        assert performance.mastery_level == MasteryLevel.MASTERED
        assert performance.created_at == datetime(2023, 1, 1, 12, 15, 30)
        assert performance.updated_at == datetime(2023, 1, 1, 12, 15, 30)

    def test_from_dict_with_z_suffix_timestamps(self):
        """Test creating from dictionary with Z-suffix timestamps."""
        data = {
            "id": "perf-456",
            "user_id": "user-789",
            "fact_key": "9+2",
            "last_attempted": "2023-01-01T12:15:30Z",
            "created_at": "2023-01-01T12:15:30Z",
            "updated_at": "2023-01-01T12:15:30Z",
            "mastery_level": "learning"
        }
        
        performance = AdditionFactPerformance.from_dict(data)
        
        from datetime import timezone
        expected_timestamp = datetime(2023, 1, 1, 12, 15, 30, tzinfo=timezone.utc)
        assert performance.last_attempted == expected_timestamp
        assert performance.created_at == expected_timestamp
        assert performance.updated_at == expected_timestamp

    def test_round_trip_conversion(self, sample_performance):
        """Test round-trip conversion."""
        dict_data = sample_performance.to_dict()
        restored_performance = AdditionFactPerformance.from_dict(dict_data)
        
        assert restored_performance.id == sample_performance.id
        assert restored_performance.user_id == sample_performance.user_id
        assert restored_performance.fact_key == sample_performance.fact_key
        assert restored_performance.total_attempts == sample_performance.total_attempts
        assert restored_performance.correct_attempts == sample_performance.correct_attempts
        assert restored_performance.mastery_level == sample_performance.mastery_level
        assert restored_performance.accuracy == sample_performance.accuracy


@pytest.mark.unit
class TestAdditionFactPerformanceUnit:
    """Unit tests for AdditionFactPerformance."""

    def test_dataclass_equality(self, sample_timestamp):
        """Test that equal performances are considered equal."""
        perf1 = AdditionFactPerformance(
            id="test-id",
            user_id="test-user",
            fact_key="5+5",
            total_attempts=5,
            correct_attempts=4,
            mastery_level=MasteryLevel.PRACTICING,
            created_at=sample_timestamp
        )
        
        perf2 = AdditionFactPerformance(
            id="test-id",
            user_id="test-user", 
            fact_key="5+5",
            total_attempts=5,
            correct_attempts=4,
            mastery_level=MasteryLevel.PRACTICING,
            created_at=sample_timestamp
        )
        
        assert perf1 == perf2

    def test_dataclass_inequality(self, sample_timestamp):
        """Test that different performances are not equal."""
        perf1 = AdditionFactPerformance(
            id="test-id-1",
            user_id="test-user",
            fact_key="5+5",
            created_at=sample_timestamp
        )
        
        perf2 = AdditionFactPerformance(
            id="test-id-2",  # Different ID
            user_id="test-user",
            fact_key="5+5",
            created_at=sample_timestamp
        )
        
        assert perf1 != perf2