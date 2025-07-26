"""Comprehensive tests for ProblemAttempt model."""

import pytest
from datetime import datetime
from src.domain.models.problem_attempt import ProblemAttempt


@pytest.fixture
def sample_timestamp():
    """Create sample timestamp for testing."""
    return datetime(2023, 1, 1, 12, 15, 30)


@pytest.fixture
def sample_problem_attempt(sample_timestamp):
    """Create sample problem attempt for testing."""
    return ProblemAttempt(
        id="attempt-123",
        session_id="session-456",
        problem="2 + 3 = ?",
        correct_answer=5,
        is_correct=True,
        response_time_ms=2500,
        timestamp=sample_timestamp,
        user_answer=5,
    )


class TestProblemAttemptInit:
    """Test ProblemAttempt initialization."""

    def test_init_with_all_fields(self, sample_timestamp):
        """Test initialization with all fields provided."""
        attempt = ProblemAttempt(
            id="attempt-123",
            session_id="session-456",
            problem="4 + 7 = ?",
            correct_answer=11,
            is_correct=True,
            response_time_ms=3000,
            timestamp=sample_timestamp,
            user_answer=11,
        )

        assert attempt.id == "attempt-123"
        assert attempt.session_id == "session-456"
        assert attempt.problem == "4 + 7 = ?"
        assert attempt.correct_answer == 11
        assert attempt.is_correct is True
        assert attempt.response_time_ms == 3000
        assert attempt.timestamp == sample_timestamp
        assert attempt.user_answer == 11

    def test_init_without_user_answer(self, sample_timestamp):
        """Test initialization without user_answer (default None)."""
        attempt = ProblemAttempt(
            id="attempt-123",
            session_id="session-456",
            problem="8 - 3 = ?",
            correct_answer=5,
            is_correct=False,
            response_time_ms=1500,
            timestamp=sample_timestamp,
        )

        assert attempt.user_answer is None
        assert attempt.is_correct is False

    def test_init_with_none_user_answer(self, sample_timestamp):
        """Test initialization with explicitly None user_answer."""
        attempt = ProblemAttempt(
            id="attempt-123",
            session_id="session-456",
            problem="9 + 1 = ?",
            correct_answer=10,
            is_correct=False,
            response_time_ms=4000,
            timestamp=sample_timestamp,
            user_answer=None,
        )

        assert attempt.user_answer is None
        assert attempt.is_correct is False

    def test_init_incorrect_answer(self, sample_timestamp):
        """Test initialization with incorrect user answer."""
        attempt = ProblemAttempt(
            id="attempt-123",
            session_id="session-456",
            problem="6 + 4 = ?",
            correct_answer=10,
            is_correct=False,
            response_time_ms=2000,
            timestamp=sample_timestamp,
            user_answer=11,
        )

        assert attempt.user_answer == 11
        assert attempt.correct_answer == 10
        assert attempt.is_correct is False


class TestProblemAttemptProperties:
    """Test ProblemAttempt properties."""

    def test_response_time_seconds_property(self, sample_timestamp):
        """Test response_time_seconds property calculation."""
        attempt = ProblemAttempt(
            id="attempt-123",
            session_id="session-456",
            problem="5 + 5 = ?",
            correct_answer=10,
            is_correct=True,
            response_time_ms=2500,
            timestamp=sample_timestamp,
            user_answer=10,
        )

        assert attempt.response_time_seconds == 2.5

    def test_response_time_seconds_zero_ms(self, sample_timestamp):
        """Test response_time_seconds with zero milliseconds."""
        attempt = ProblemAttempt(
            id="attempt-123",
            session_id="session-456",
            problem="1 + 1 = ?",
            correct_answer=2,
            is_correct=True,
            response_time_ms=0,
            timestamp=sample_timestamp,
            user_answer=2,
        )

        assert attempt.response_time_seconds == 0.0

    def test_response_time_seconds_large_value(self, sample_timestamp):
        """Test response_time_seconds with large millisecond value."""
        attempt = ProblemAttempt(
            id="attempt-123",
            session_id="session-456",
            problem="10 + 10 = ?",
            correct_answer=20,
            is_correct=True,
            response_time_ms=60000,  # 60 seconds
            timestamp=sample_timestamp,
            user_answer=20,
        )

        assert attempt.response_time_seconds == 60.0

    def test_response_time_seconds_fractional(self, sample_timestamp):
        """Test response_time_seconds with value that creates fraction."""
        attempt = ProblemAttempt(
            id="attempt-123",
            session_id="session-456",
            problem="7 + 3 = ?",
            correct_answer=10,
            is_correct=True,
            response_time_ms=1500,  # 1.5 seconds
            timestamp=sample_timestamp,
            user_answer=10,
        )

        assert attempt.response_time_seconds == 1.5


class TestProblemAttemptFromDict:
    """Test ProblemAttempt.from_dict method."""

    def test_from_dict_complete_data(self):
        """Test creating ProblemAttempt from complete dictionary data."""
        data = {
            "id": "attempt-123",
            "session_id": "session-456",
            "problem": "3 + 4 = ?",
            "correct_answer": 7,
            "is_correct": True,
            "response_time_ms": 2200,
            "timestamp": "2023-01-01T12:15:30",
            "user_answer": 7,
        }

        attempt = ProblemAttempt.from_dict(data)

        assert attempt.id == "attempt-123"
        assert attempt.session_id == "session-456"
        assert attempt.problem == "3 + 4 = ?"
        assert attempt.correct_answer == 7
        assert attempt.is_correct is True
        assert attempt.response_time_ms == 2200
        assert attempt.timestamp == datetime(2023, 1, 1, 12, 15, 30)
        assert attempt.user_answer == 7

    def test_from_dict_without_user_answer(self):
        """Test creating ProblemAttempt without user_answer in data."""
        data = {
            "id": "attempt-123",
            "session_id": "session-456",
            "problem": "8 - 5 = ?",
            "correct_answer": 3,
            "is_correct": False,
            "response_time_ms": 1800,
            "timestamp": "2023-01-01T12:15:30",
            # No user_answer key
        }

        attempt = ProblemAttempt.from_dict(data)

        assert attempt.user_answer is None
        assert attempt.is_correct is False

    def test_from_dict_with_none_user_answer(self):
        """Test creating ProblemAttempt with explicit None user_answer."""
        data = {
            "id": "attempt-123",
            "session_id": "session-456",
            "problem": "12 / 4 = ?",
            "correct_answer": 3,
            "is_correct": False,
            "response_time_ms": 3500,
            "timestamp": "2023-01-01T12:15:30",
            "user_answer": None,
        }

        attempt = ProblemAttempt.from_dict(data)

        assert attempt.user_answer is None

    def test_from_dict_with_z_suffix_timestamp(self):
        """Test creating ProblemAttempt with Z-suffix timestamp."""
        data = {
            "id": "attempt-123",
            "session_id": "session-456",
            "problem": "5 * 2 = ?",
            "correct_answer": 10,
            "is_correct": True,
            "response_time_ms": 2000,
            "timestamp": "2023-01-01T12:15:30Z",
            "user_answer": 10,
        }

        attempt = ProblemAttempt.from_dict(data)

        # Z should be replaced with +00:00 timezone info
        from datetime import timezone

        expected_timestamp = datetime(2023, 1, 1, 12, 15, 30, tzinfo=timezone.utc)
        assert attempt.timestamp == expected_timestamp

    def test_from_dict_with_timezone_timestamp(self):
        """Test creating ProblemAttempt with timezone-aware timestamp."""
        data = {
            "id": "attempt-123",
            "session_id": "session-456",
            "problem": "15 - 8 = ?",
            "correct_answer": 7,
            "is_correct": True,
            "response_time_ms": 1900,
            "timestamp": "2023-01-01T12:15:30+00:00",
            "user_answer": 7,
        }

        attempt = ProblemAttempt.from_dict(data)

        from datetime import timezone

        expected_timestamp = datetime(2023, 1, 1, 12, 15, 30, tzinfo=timezone.utc)
        assert attempt.timestamp == expected_timestamp

    def test_from_dict_invalid_timestamp_format(self):
        """Test creating ProblemAttempt with invalid timestamp format."""
        data = {
            "id": "attempt-123",
            "session_id": "session-456",
            "problem": "6 + 2 = ?",
            "correct_answer": 8,
            "is_correct": True,
            "response_time_ms": 2500,
            "timestamp": "invalid-timestamp",
            "user_answer": 8,
        }

        with pytest.raises(ValueError):
            ProblemAttempt.from_dict(data)

    def test_from_dict_missing_required_field(self):
        """Test creating ProblemAttempt with missing required field."""
        data = {
            "id": "attempt-123",
            "session_id": "session-456",
            "problem": "9 + 1 = ?",
            # Missing correct_answer
            "is_correct": True,
            "response_time_ms": 2100,
            "timestamp": "2023-01-01T12:15:30",
            "user_answer": 10,
        }

        with pytest.raises(KeyError):
            ProblemAttempt.from_dict(data)

    def test_from_dict_boolean_conversion(self):
        """Test that is_correct field is properly handled as boolean."""
        data = {
            "id": "attempt-123",
            "session_id": "session-456",
            "problem": "4 + 4 = ?",
            "correct_answer": 8,
            "is_correct": False,
            "response_time_ms": 3000,
            "timestamp": "2023-01-01T12:15:30",
            "user_answer": 9,
        }

        attempt = ProblemAttempt.from_dict(data)

        assert attempt.is_correct is False
        assert isinstance(attempt.is_correct, bool)


class TestProblemAttemptToDict:
    """Test ProblemAttempt.to_dict method."""

    def test_to_dict_complete_attempt(self, sample_problem_attempt):
        """Test converting complete ProblemAttempt to dictionary."""
        result = sample_problem_attempt.to_dict()

        expected = {
            "id": "attempt-123",
            "session_id": "session-456",
            "problem": "2 + 3 = ?",
            "user_answer": 5,
            "correct_answer": 5,
            "is_correct": True,
            "response_time_ms": 2500,
            "timestamp": "2023-01-01T12:15:30",
        }

        assert result == expected

    def test_to_dict_without_user_answer(self, sample_timestamp):
        """Test converting ProblemAttempt without user_answer to dictionary."""
        attempt = ProblemAttempt(
            id="attempt-123",
            session_id="session-456",
            problem="10 - 7 = ?",
            correct_answer=3,
            is_correct=False,
            response_time_ms=4000,
            timestamp=sample_timestamp,
            user_answer=None,
        )

        result = attempt.to_dict()

        expected = {
            "id": "attempt-123",
            "session_id": "session-456",
            "problem": "10 - 7 = ?",
            "user_answer": None,
            "correct_answer": 3,
            "is_correct": False,
            "response_time_ms": 4000,
            "timestamp": "2023-01-01T12:15:30",
        }

        assert result == expected

    def test_to_dict_incorrect_attempt(self, sample_timestamp):
        """Test converting incorrect ProblemAttempt to dictionary."""
        attempt = ProblemAttempt(
            id="attempt-456",
            session_id="session-789",
            problem="8 + 7 = ?",
            correct_answer=15,
            is_correct=False,
            response_time_ms=3500,
            timestamp=sample_timestamp,
            user_answer=16,
        )

        result = attempt.to_dict()

        expected = {
            "id": "attempt-456",
            "session_id": "session-789",
            "problem": "8 + 7 = ?",
            "user_answer": 16,
            "correct_answer": 15,
            "is_correct": False,
            "response_time_ms": 3500,
            "timestamp": "2023-01-01T12:15:30",
        }

        assert result == expected

    def test_to_dict_zero_response_time(self, sample_timestamp):
        """Test converting ProblemAttempt with zero response time to dictionary."""
        attempt = ProblemAttempt(
            id="attempt-789",
            session_id="session-123",
            problem="0 + 0 = ?",
            correct_answer=0,
            is_correct=True,
            response_time_ms=0,
            timestamp=sample_timestamp,
            user_answer=0,
        )

        result = attempt.to_dict()

        assert result["response_time_ms"] == 0


class TestProblemAttemptRoundTrip:
    """Test round-trip conversion between ProblemAttempt and dictionary."""

    def test_round_trip_conversion_complete(self, sample_problem_attempt):
        """Test round-trip conversion for complete attempt."""
        # Convert to dict and back
        dict_data = sample_problem_attempt.to_dict()
        restored_attempt = ProblemAttempt.from_dict(dict_data)

        # Should be identical
        assert restored_attempt.id == sample_problem_attempt.id
        assert restored_attempt.session_id == sample_problem_attempt.session_id
        assert restored_attempt.problem == sample_problem_attempt.problem
        assert restored_attempt.user_answer == sample_problem_attempt.user_answer
        assert restored_attempt.correct_answer == sample_problem_attempt.correct_answer
        assert restored_attempt.is_correct == sample_problem_attempt.is_correct
        assert (
            restored_attempt.response_time_ms == sample_problem_attempt.response_time_ms
        )
        assert restored_attempt.timestamp == sample_problem_attempt.timestamp

    def test_round_trip_conversion_no_user_answer(self, sample_timestamp):
        """Test round-trip conversion for attempt without user answer."""
        original_attempt = ProblemAttempt(
            id="attempt-999",
            session_id="session-888",
            problem="20 / 4 = ?",
            correct_answer=5,
            is_correct=False,
            response_time_ms=5000,
            timestamp=sample_timestamp,
            user_answer=None,
        )

        # Convert to dict and back
        dict_data = original_attempt.to_dict()
        restored_attempt = ProblemAttempt.from_dict(dict_data)

        # Should be identical
        assert restored_attempt.id == original_attempt.id
        assert restored_attempt.session_id == original_attempt.session_id
        assert restored_attempt.problem == original_attempt.problem
        assert restored_attempt.user_answer == original_attempt.user_answer
        assert restored_attempt.correct_answer == original_attempt.correct_answer
        assert restored_attempt.is_correct == original_attempt.is_correct
        assert restored_attempt.response_time_ms == original_attempt.response_time_ms
        assert restored_attempt.timestamp == original_attempt.timestamp

    def test_round_trip_preserves_properties(self, sample_problem_attempt):
        """Test that round-trip conversion preserves calculated properties."""
        # Convert to dict and back
        dict_data = sample_problem_attempt.to_dict()
        restored_attempt = ProblemAttempt.from_dict(dict_data)

        # Properties should be identical
        assert (
            restored_attempt.response_time_seconds
            == sample_problem_attempt.response_time_seconds
        )


class TestProblemAttemptEdgeCases:
    """Test edge cases for ProblemAttempt."""

    def test_very_large_response_time(self, sample_timestamp):
        """Test with very large response time."""
        attempt = ProblemAttempt(
            id="attempt-123",
            session_id="session-456",
            problem="1000 + 1000 = ?",
            correct_answer=2000,
            is_correct=True,
            response_time_ms=999999999,  # Very large response time
            timestamp=sample_timestamp,
            user_answer=2000,
        )

        assert attempt.response_time_ms == 999999999
        assert attempt.response_time_seconds == 999999.999

    def test_negative_numbers_in_problem(self, sample_timestamp):
        """Test with negative numbers in problem and answers."""
        attempt = ProblemAttempt(
            id="attempt-123",
            session_id="session-456",
            problem="5 - 10 = ?",
            correct_answer=-5,
            is_correct=True,
            response_time_ms=3000,
            timestamp=sample_timestamp,
            user_answer=-5,
        )

        assert attempt.correct_answer == -5
        assert attempt.user_answer == -5
        assert attempt.is_correct is True

    def test_complex_problem_text(self, sample_timestamp):
        """Test with complex problem text containing special characters."""
        attempt = ProblemAttempt(
            id="attempt-123",
            session_id="session-456",
            problem="What is 3 × 4? (Hint: multiplication)",
            correct_answer=12,
            is_correct=False,
            response_time_ms=8000,
            timestamp=sample_timestamp,
            user_answer=13,
        )

        assert "×" in attempt.problem
        assert "(" in attempt.problem
        assert attempt.is_correct is False

    def test_zero_values(self, sample_timestamp):
        """Test with zero values for answers and response time."""
        attempt = ProblemAttempt(
            id="attempt-123",
            session_id="session-456",
            problem="0 + 0 = ?",
            correct_answer=0,
            is_correct=True,
            response_time_ms=0,
            timestamp=sample_timestamp,
            user_answer=0,
        )

        assert attempt.correct_answer == 0
        assert attempt.user_answer == 0
        assert attempt.response_time_ms == 0
        assert attempt.response_time_seconds == 0.0


@pytest.mark.unit
class TestProblemAttemptDataclass:
    """Test ProblemAttempt dataclass behavior."""

    def test_dataclass_equality(self, sample_timestamp):
        """Test that equal ProblemAttempts are considered equal."""
        attempt1 = ProblemAttempt(
            id="attempt-123",
            session_id="session-456",
            problem="5 + 5 = ?",
            correct_answer=10,
            is_correct=True,
            response_time_ms=2000,
            timestamp=sample_timestamp,
            user_answer=10,
        )

        attempt2 = ProblemAttempt(
            id="attempt-123",
            session_id="session-456",
            problem="5 + 5 = ?",
            correct_answer=10,
            is_correct=True,
            response_time_ms=2000,
            timestamp=sample_timestamp,
            user_answer=10,
        )

        assert attempt1 == attempt2

    def test_dataclass_inequality(self, sample_timestamp):
        """Test that different ProblemAttempts are not equal."""
        attempt1 = ProblemAttempt(
            id="attempt-123",
            session_id="session-456",
            problem="5 + 5 = ?",
            correct_answer=10,
            is_correct=True,
            response_time_ms=2000,
            timestamp=sample_timestamp,
            user_answer=10,
        )

        attempt2 = ProblemAttempt(
            id="attempt-456",  # Different ID
            session_id="session-456",
            problem="5 + 5 = ?",
            correct_answer=10,
            is_correct=True,
            response_time_ms=2000,
            timestamp=sample_timestamp,
            user_answer=10,
        )

        assert attempt1 != attempt2

    def test_dataclass_str_representation(self, sample_timestamp):
        """Test string representation of ProblemAttempt."""
        attempt = ProblemAttempt(
            id="attempt-123",
            session_id="session-456",
            problem="7 + 3 = ?",
            correct_answer=10,
            is_correct=True,
            response_time_ms=1500,
            timestamp=sample_timestamp,
            user_answer=10,
        )

        str_repr = str(attempt)

        # Should contain key information
        assert "attempt-123" in str_repr
        assert "session-456" in str_repr
        assert "7 + 3 = ?" in str_repr
        assert "is_correct=True" in str_repr
