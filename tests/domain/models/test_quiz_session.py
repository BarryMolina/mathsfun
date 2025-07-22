"""Comprehensive tests for QuizSession model."""

import pytest
from datetime import datetime
from src.domain.models.quiz_session import QuizSession, QuizType, SessionStatus


@pytest.fixture
def sample_start_time():
    """Create sample start time for testing."""
    return datetime(2023, 1, 1, 12, 0, 0)


@pytest.fixture
def sample_end_time():
    """Create sample end time for testing."""
    return datetime(2023, 1, 1, 12, 30, 0)


@pytest.fixture
def sample_quiz_session(sample_start_time, sample_end_time):
    """Create sample quiz session for testing."""
    return QuizSession(
        id="session-123",
        user_id="user-456",
        quiz_type=QuizType.ADDITION,
        difficulty_level=2,
        start_time=sample_start_time,
        total_problems=10,
        correct_answers=8,
        status=SessionStatus.COMPLETED,
        end_time=sample_end_time
    )


class TestQuizType:
    """Test QuizType enumeration."""

    def test_quiz_type_values(self):
        """Test QuizType enum values."""
        assert QuizType.ADDITION.value == "addition"
        assert QuizType.TABLES.value == "tables"

    def test_quiz_type_from_string(self):
        """Test creating QuizType from string."""
        assert QuizType("addition") == QuizType.ADDITION
        assert QuizType("tables") == QuizType.TABLES

    def test_quiz_type_invalid_value(self):
        """Test creating QuizType with invalid value."""
        with pytest.raises(ValueError):
            QuizType("invalid")


class TestSessionStatus:
    """Test SessionStatus enumeration."""

    def test_session_status_values(self):
        """Test SessionStatus enum values."""
        assert SessionStatus.ACTIVE.value == "active"
        assert SessionStatus.COMPLETED.value == "completed"
        assert SessionStatus.ABANDONED.value == "abandoned"

    def test_session_status_from_string(self):
        """Test creating SessionStatus from string."""
        assert SessionStatus("active") == SessionStatus.ACTIVE
        assert SessionStatus("completed") == SessionStatus.COMPLETED
        assert SessionStatus("abandoned") == SessionStatus.ABANDONED

    def test_session_status_invalid_value(self):
        """Test creating SessionStatus with invalid value."""
        with pytest.raises(ValueError):
            SessionStatus("invalid")


class TestQuizSessionInit:
    """Test QuizSession initialization."""

    def test_init_minimal_required_fields(self, sample_start_time):
        """Test initialization with minimal required fields."""
        session = QuizSession(
            id="test-id",
            user_id="test-user",
            quiz_type=QuizType.ADDITION,
            difficulty_level=1,
            start_time=sample_start_time
        )
        
        assert session.id == "test-id"
        assert session.user_id == "test-user"
        assert session.quiz_type == QuizType.ADDITION
        assert session.difficulty_level == 1
        assert session.start_time == sample_start_time
        assert session.total_problems == 0  # Default value
        assert session.correct_answers == 0  # Default value
        assert session.status == SessionStatus.ACTIVE  # Default value
        assert session.end_time is None  # Default value

    def test_init_all_fields(self, sample_start_time, sample_end_time):
        """Test initialization with all fields."""
        session = QuizSession(
            id="test-id",
            user_id="test-user",
            quiz_type=QuizType.TABLES,
            difficulty_level=3,
            start_time=sample_start_time,
            total_problems=15,
            correct_answers=12,
            status=SessionStatus.COMPLETED,
            end_time=sample_end_time
        )
        
        assert session.id == "test-id"
        assert session.user_id == "test-user"
        assert session.quiz_type == QuizType.TABLES
        assert session.difficulty_level == 3
        assert session.start_time == sample_start_time
        assert session.total_problems == 15
        assert session.correct_answers == 12
        assert session.status == SessionStatus.COMPLETED
        assert session.end_time == sample_end_time


class TestQuizSessionProperties:
    """Test QuizSession properties."""

    def test_accuracy_property_normal_case(self, sample_start_time):
        """Test accuracy calculation for normal case."""
        session = QuizSession(
            id="test-id",
            user_id="test-user",
            quiz_type=QuizType.ADDITION,
            difficulty_level=1,
            start_time=sample_start_time,
            total_problems=10,
            correct_answers=8
        )
        
        assert session.accuracy == 80.0

    def test_accuracy_property_perfect_score(self, sample_start_time):
        """Test accuracy calculation for perfect score."""
        session = QuizSession(
            id="test-id",
            user_id="test-user",
            quiz_type=QuizType.ADDITION,
            difficulty_level=1,
            start_time=sample_start_time,
            total_problems=5,
            correct_answers=5
        )
        
        assert session.accuracy == 100.0

    def test_accuracy_property_zero_correct(self, sample_start_time):
        """Test accuracy calculation when no answers are correct."""
        session = QuizSession(
            id="test-id",
            user_id="test-user",
            quiz_type=QuizType.ADDITION,
            difficulty_level=1,
            start_time=sample_start_time,
            total_problems=10,
            correct_answers=0
        )
        
        assert session.accuracy == 0.0

    def test_accuracy_property_zero_problems(self, sample_start_time):
        """Test accuracy calculation when no problems attempted."""
        session = QuizSession(
            id="test-id",
            user_id="test-user",
            quiz_type=QuizType.ADDITION,
            difficulty_level=1,
            start_time=sample_start_time,
            total_problems=0,
            correct_answers=0
        )
        
        assert session.accuracy == 0.0

    def test_duration_seconds_property_with_end_time(self, sample_start_time, sample_end_time):
        """Test duration calculation when end_time is set."""
        session = QuizSession(
            id="test-id",
            user_id="test-user",
            quiz_type=QuizType.ADDITION,
            difficulty_level=1,
            start_time=sample_start_time,
            end_time=sample_end_time
        )
        
        # 30 minutes = 1800 seconds
        assert session.duration_seconds == 1800.0

    def test_duration_seconds_property_without_end_time(self, sample_start_time):
        """Test duration calculation when end_time is not set."""
        session = QuizSession(
            id="test-id",
            user_id="test-user",
            quiz_type=QuizType.ADDITION,
            difficulty_level=1,
            start_time=sample_start_time,
            end_time=None
        )
        
        assert session.duration_seconds is None

    def test_duration_seconds_property_same_start_end_time(self, sample_start_time):
        """Test duration calculation when start and end times are the same."""
        session = QuizSession(
            id="test-id",
            user_id="test-user",
            quiz_type=QuizType.ADDITION,
            difficulty_level=1,
            start_time=sample_start_time,
            end_time=sample_start_time
        )
        
        assert session.duration_seconds == 0.0

    def test_is_completed_property_true(self, sample_start_time):
        """Test is_completed property when session is completed."""
        session = QuizSession(
            id="test-id",
            user_id="test-user",
            quiz_type=QuizType.ADDITION,
            difficulty_level=1,
            start_time=sample_start_time,
            status=SessionStatus.COMPLETED
        )
        
        assert session.is_completed is True

    def test_is_completed_property_false_active(self, sample_start_time):
        """Test is_completed property when session is active."""
        session = QuizSession(
            id="test-id",
            user_id="test-user",
            quiz_type=QuizType.ADDITION,
            difficulty_level=1,
            start_time=sample_start_time,
            status=SessionStatus.ACTIVE
        )
        
        assert session.is_completed is False

    def test_is_completed_property_false_abandoned(self, sample_start_time):
        """Test is_completed property when session is abandoned."""
        session = QuizSession(
            id="test-id",
            user_id="test-user",
            quiz_type=QuizType.ADDITION,
            difficulty_level=1,
            start_time=sample_start_time,
            status=SessionStatus.ABANDONED
        )
        
        assert session.is_completed is False


class TestQuizSessionFromDict:
    """Test QuizSession.from_dict method."""

    def test_from_dict_minimal_data(self):
        """Test creating QuizSession from minimal dictionary data."""
        data = {
            "id": "session-123",
            "user_id": "user-456",
            "quiz_type": "addition",
            "difficulty_level": 2,
            "start_time": "2023-01-01T12:00:00"
        }
        
        session = QuizSession.from_dict(data)
        
        assert session.id == "session-123"
        assert session.user_id == "user-456"
        assert session.quiz_type == QuizType.ADDITION
        assert session.difficulty_level == 2
        assert session.start_time == datetime(2023, 1, 1, 12, 0, 0)
        assert session.total_problems == 0  # Default from get()
        assert session.correct_answers == 0  # Default from get()
        assert session.status == SessionStatus.ACTIVE  # Default from get()
        assert session.end_time is None

    def test_from_dict_complete_data(self):
        """Test creating QuizSession from complete dictionary data."""
        data = {
            "id": "session-123",
            "user_id": "user-456",
            "quiz_type": "tables",
            "difficulty_level": 3,
            "start_time": "2023-01-01T12:00:00",
            "total_problems": 15,
            "correct_answers": 12,
            "status": "completed",
            "end_time": "2023-01-01T12:30:00"
        }
        
        session = QuizSession.from_dict(data)
        
        assert session.id == "session-123"
        assert session.user_id == "user-456"
        assert session.quiz_type == QuizType.TABLES
        assert session.difficulty_level == 3
        assert session.start_time == datetime(2023, 1, 1, 12, 0, 0)
        assert session.total_problems == 15
        assert session.correct_answers == 12
        assert session.status == SessionStatus.COMPLETED
        assert session.end_time == datetime(2023, 1, 1, 12, 30, 0)

    def test_from_dict_with_z_suffix_timestamps(self):
        """Test creating QuizSession with Z-suffix timestamps."""
        data = {
            "id": "session-123",
            "user_id": "user-456",
            "quiz_type": "addition",
            "difficulty_level": 1,
            "start_time": "2023-01-01T12:00:00Z",
            "end_time": "2023-01-01T12:30:00Z"
        }
        
        session = QuizSession.from_dict(data)
        
        # Z should be replaced with +00:00 timezone info
        from datetime import timezone
        assert session.start_time == datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        assert session.end_time == datetime(2023, 1, 1, 12, 30, 0, tzinfo=timezone.utc)

    def test_from_dict_with_timezone_timestamps(self):
        """Test creating QuizSession with timezone-aware timestamps."""
        data = {
            "id": "session-123",
            "user_id": "user-456",
            "quiz_type": "addition",
            "difficulty_level": 1,
            "start_time": "2023-01-01T12:00:00+00:00",
            "end_time": "2023-01-01T12:30:00+00:00"
        }
        
        session = QuizSession.from_dict(data)
        
        from datetime import timezone
        assert session.start_time == datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        assert session.end_time == datetime(2023, 1, 1, 12, 30, 0, tzinfo=timezone.utc)

    def test_from_dict_invalid_quiz_type(self):
        """Test creating QuizSession with invalid quiz type."""
        data = {
            "id": "session-123",
            "user_id": "user-456",
            "quiz_type": "invalid_type",
            "difficulty_level": 1,
            "start_time": "2023-01-01T12:00:00"
        }
        
        with pytest.raises(ValueError):
            QuizSession.from_dict(data)

    def test_from_dict_invalid_status(self):
        """Test creating QuizSession with invalid status."""
        data = {
            "id": "session-123",
            "user_id": "user-456",
            "quiz_type": "addition",
            "difficulty_level": 1,
            "start_time": "2023-01-01T12:00:00",
            "status": "invalid_status"
        }
        
        with pytest.raises(ValueError):
            QuizSession.from_dict(data)

    def test_from_dict_invalid_datetime_format(self):
        """Test creating QuizSession with invalid datetime format."""
        data = {
            "id": "session-123",
            "user_id": "user-456",
            "quiz_type": "addition",
            "difficulty_level": 1,
            "start_time": "invalid-datetime"
        }
        
        with pytest.raises(ValueError):
            QuizSession.from_dict(data)

    def test_from_dict_missing_required_field(self):
        """Test creating QuizSession with missing required field."""
        data = {
            "id": "session-123",
            "user_id": "user-456",
            "quiz_type": "addition",
            # Missing difficulty_level
            "start_time": "2023-01-01T12:00:00"
        }
        
        with pytest.raises(KeyError):
            QuizSession.from_dict(data)


class TestQuizSessionToDict:
    """Test QuizSession.to_dict method."""

    def test_to_dict_complete_session(self, sample_quiz_session):
        """Test converting complete QuizSession to dictionary."""
        result = sample_quiz_session.to_dict()
        
        expected = {
            "id": "session-123",
            "user_id": "user-456",
            "quiz_type": "addition",
            "difficulty_level": 2,
            "start_time": "2023-01-01T12:00:00",
            "total_problems": 10,
            "correct_answers": 8,
            "status": "completed",
            "end_time": "2023-01-01T12:30:00"
        }
        
        assert result == expected

    def test_to_dict_no_end_time(self, sample_start_time):
        """Test converting QuizSession without end_time to dictionary."""
        session = QuizSession(
            id="session-123",
            user_id="user-456",
            quiz_type=QuizType.TABLES,
            difficulty_level=3,
            start_time=sample_start_time,
            total_problems=5,
            correct_answers=3,
            status=SessionStatus.ACTIVE,
            end_time=None
        )
        
        result = session.to_dict()
        
        expected = {
            "id": "session-123",
            "user_id": "user-456",
            "quiz_type": "tables",
            "difficulty_level": 3,
            "start_time": "2023-01-01T12:00:00",
            "total_problems": 5,
            "correct_answers": 3,
            "status": "active",
            "end_time": None
        }
        
        assert result == expected

    def test_to_dict_minimal_session(self, sample_start_time):
        """Test converting minimal QuizSession to dictionary."""
        session = QuizSession(
            id="test-id",
            user_id="test-user",
            quiz_type=QuizType.ADDITION,
            difficulty_level=1,
            start_time=sample_start_time
        )
        
        result = session.to_dict()
        
        expected = {
            "id": "test-id",
            "user_id": "test-user",
            "quiz_type": "addition",
            "difficulty_level": 1,
            "start_time": "2023-01-01T12:00:00",
            "total_problems": 0,
            "correct_answers": 0,
            "status": "active",
            "end_time": None
        }
        
        assert result == expected


class TestQuizSessionRoundTrip:
    """Test round-trip conversion between QuizSession and dictionary."""

    def test_round_trip_conversion_complete(self, sample_quiz_session):
        """Test round-trip conversion for complete session."""
        # Convert to dict and back
        dict_data = sample_quiz_session.to_dict()
        restored_session = QuizSession.from_dict(dict_data)
        
        # Should be identical
        assert restored_session.id == sample_quiz_session.id
        assert restored_session.user_id == sample_quiz_session.user_id
        assert restored_session.quiz_type == sample_quiz_session.quiz_type
        assert restored_session.difficulty_level == sample_quiz_session.difficulty_level
        assert restored_session.start_time == sample_quiz_session.start_time
        assert restored_session.total_problems == sample_quiz_session.total_problems
        assert restored_session.correct_answers == sample_quiz_session.correct_answers
        assert restored_session.status == sample_quiz_session.status
        assert restored_session.end_time == sample_quiz_session.end_time

    def test_round_trip_conversion_minimal(self, sample_start_time):
        """Test round-trip conversion for minimal session."""
        original_session = QuizSession(
            id="test-id",
            user_id="test-user",
            quiz_type=QuizType.TABLES,
            difficulty_level=2,
            start_time=sample_start_time
        )
        
        # Convert to dict and back
        dict_data = original_session.to_dict()
        restored_session = QuizSession.from_dict(dict_data)
        
        # Should be identical
        assert restored_session.id == original_session.id
        assert restored_session.user_id == original_session.user_id
        assert restored_session.quiz_type == original_session.quiz_type
        assert restored_session.difficulty_level == original_session.difficulty_level
        assert restored_session.start_time == original_session.start_time
        assert restored_session.total_problems == original_session.total_problems
        assert restored_session.correct_answers == original_session.correct_answers
        assert restored_session.status == original_session.status
        assert restored_session.end_time == original_session.end_time


class TestQuizSessionEdgeCases:
    """Test edge cases for QuizSession."""

    def test_accuracy_with_more_correct_than_total(self, sample_start_time):
        """Test accuracy calculation with invalid data (more correct than total)."""
        # This shouldn't happen in normal usage, but test edge case
        session = QuizSession(
            id="test-id",
            user_id="test-user",
            quiz_type=QuizType.ADDITION,
            difficulty_level=1,
            start_time=sample_start_time,
            total_problems=5,
            correct_answers=10  # Invalid: more correct than total
        )
        
        # Should still calculate, even if mathematically incorrect
        assert session.accuracy == 200.0

    def test_very_short_duration(self, sample_start_time):
        """Test duration calculation for very short session."""
        end_time = datetime(2023, 1, 1, 12, 0, 1)  # 1 second later
        session = QuizSession(
            id="test-id",
            user_id="test-user",
            quiz_type=QuizType.ADDITION,
            difficulty_level=1,
            start_time=sample_start_time,
            end_time=end_time
        )
        
        assert session.duration_seconds == 1.0

    def test_large_numbers(self, sample_start_time):
        """Test session with large numbers."""
        session = QuizSession(
            id="test-id",
            user_id="test-user",
            quiz_type=QuizType.ADDITION,
            difficulty_level=1,
            start_time=sample_start_time,
            total_problems=1000000,
            correct_answers=999999
        )
        
        assert session.accuracy == 99.9999


@pytest.mark.unit  
class TestQuizSessionDataclass:
    """Test QuizSession dataclass behavior."""

    def test_dataclass_equality(self, sample_start_time, sample_end_time):
        """Test that equal QuizSessions are considered equal."""
        session1 = QuizSession(
            id="test-id",
            user_id="test-user",
            quiz_type=QuizType.ADDITION,
            difficulty_level=1,
            start_time=sample_start_time,
            end_time=sample_end_time
        )
        
        session2 = QuizSession(
            id="test-id",
            user_id="test-user",
            quiz_type=QuizType.ADDITION,
            difficulty_level=1,
            start_time=sample_start_time,
            end_time=sample_end_time
        )
        
        assert session1 == session2

    def test_dataclass_inequality(self, sample_start_time):
        """Test that different QuizSessions are not equal."""
        session1 = QuizSession(
            id="test-id-1",
            user_id="test-user",
            quiz_type=QuizType.ADDITION,
            difficulty_level=1,
            start_time=sample_start_time
        )
        
        session2 = QuizSession(
            id="test-id-2",  # Different ID
            user_id="test-user",
            quiz_type=QuizType.ADDITION,
            difficulty_level=1,
            start_time=sample_start_time
        )
        
        assert session1 != session2

    def test_dataclass_str_representation(self, sample_start_time):
        """Test string representation of QuizSession."""
        session = QuizSession(
            id="test-id",
            user_id="test-user",
            quiz_type=QuizType.ADDITION,
            difficulty_level=1,
            start_time=sample_start_time
        )
        
        str_repr = str(session)
        
        # Should contain key information
        assert "test-id" in str_repr
        assert "test-user" in str_repr
        assert "QuizType.ADDITION" in str_repr
        assert "difficulty_level=1" in str_repr