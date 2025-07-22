"""Comprehensive tests for QuizService class."""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from src.domain.services.quiz_service import QuizService, QuizSessionResult, UserProgress
from src.domain.models.quiz_session import QuizSession, QuizType, SessionStatus
from src.domain.models.problem_attempt import ProblemAttempt
from src.infrastructure.database.repositories.quiz_repository import QuizRepository


@pytest.fixture
def mock_quiz_repository():
    """Create mock quiz repository."""
    return Mock(spec=QuizRepository)


@pytest.fixture
def quiz_service(mock_quiz_repository):
    """Create QuizService instance with mocked dependencies."""
    return QuizService(mock_quiz_repository)


@pytest.fixture
def sample_quiz_session():
    """Create sample quiz session for testing."""
    return QuizSession(
        id="session-123",
        user_id="user-456",
        quiz_type=QuizType.ADDITION,
        difficulty_level=2,
        start_time=datetime(2023, 1, 1, 12, 0, 0),
        end_time=datetime(2023, 1, 1, 12, 30, 0),
        total_problems=10,
        correct_answers=8,
        status=SessionStatus.COMPLETED
    )


@pytest.fixture
def sample_problem_attempt():
    """Create sample problem attempt for testing."""
    return ProblemAttempt(
        id="attempt-123",
        session_id="session-456",
        problem="2 + 3",
        user_answer=5,
        correct_answer=5,
        is_correct=True,
        response_time_ms=2500,
        timestamp=datetime(2023, 1, 1, 12, 15, 0)
    )


@pytest.fixture
def sample_attempts():
    """Create list of sample attempts for testing."""
    return [
        ProblemAttempt(
            id="attempt-1",
            session_id="session-123",
            problem="2 + 3",
            user_answer=5,
            correct_answer=5,
            is_correct=True,
            response_time_ms=2000,
            timestamp=datetime(2023, 1, 1, 12, 15, 0)
        ),
        ProblemAttempt(
            id="attempt-2",
            session_id="session-123",
            problem="4 + 7",
            user_answer=11,
            correct_answer=11,
            is_correct=True,
            response_time_ms=3000,
            timestamp=datetime(2023, 1, 1, 12, 16, 0)
        ),
        ProblemAttempt(
            id="attempt-3",
            session_id="session-123",
            problem="8 + 9",
            user_answer=16,
            correct_answer=17,
            is_correct=False,
            response_time_ms=4000,
            timestamp=datetime(2023, 1, 1, 12, 17, 0)
        )
    ]


class TestQuizServiceInit:
    """Test QuizService initialization."""

    def test_init(self, mock_quiz_repository):
        """Test QuizService initialization."""
        service = QuizService(mock_quiz_repository)
        assert service.quiz_repo == mock_quiz_repository


class TestStartQuizSession:
    """Test start_quiz_session method."""

    def test_start_quiz_session_success(self, quiz_service, mock_quiz_repository, sample_quiz_session):
        """Test successful quiz session start."""
        mock_quiz_repository.create_session.return_value = sample_quiz_session
        
        with patch('src.domain.services.quiz_service.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2023, 1, 1, 12, 0, 0)
            
            result = quiz_service.start_quiz_session("user-456", "addition", 2)
        
        assert result == sample_quiz_session
        
        # Verify create_session was called with correct data
        mock_quiz_repository.create_session.assert_called_once()
        session_arg = mock_quiz_repository.create_session.call_args[0][0]
        
        assert session_arg.user_id == "user-456"
        assert session_arg.quiz_type == QuizType.ADDITION
        assert session_arg.difficulty_level == 2
        assert session_arg.total_problems == 0
        assert session_arg.correct_answers == 0
        assert session_arg.status == SessionStatus.ACTIVE

    def test_start_quiz_session_repository_failure(self, quiz_service, mock_quiz_repository):
        """Test quiz session start when repository fails."""
        mock_quiz_repository.create_session.return_value = None
        
        result = quiz_service.start_quiz_session("user-456", "addition", 2)
        
        assert result is None

    def test_start_quiz_session_invalid_quiz_type(self, quiz_service, mock_quiz_repository):
        """Test quiz session start with invalid quiz type."""
        # This should raise a ValueError when creating QuizType
        with pytest.raises(ValueError):
            quiz_service.start_quiz_session("user-456", "invalid_type", 2)


class TestRecordAnswer:
    """Test record_answer method."""

    def test_record_answer_correct(self, quiz_service, mock_quiz_repository, sample_problem_attempt):
        """Test recording a correct answer."""
        mock_quiz_repository.save_attempt.return_value = sample_problem_attempt
        mock_quiz_repository.increment_session_stats.return_value = True
        
        with patch('src.domain.services.quiz_service.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2023, 1, 1, 12, 15, 0)
            
            result = quiz_service.record_answer("session-456", "2 + 3", 5, 5, 2500)
        
        assert result is True
        
        # Verify save_attempt was called
        mock_quiz_repository.save_attempt.assert_called_once()
        attempt_arg = mock_quiz_repository.save_attempt.call_args[0][0]
        
        assert attempt_arg.session_id == "session-456"
        assert attempt_arg.problem == "2 + 3"
        assert attempt_arg.user_answer == 5
        assert attempt_arg.correct_answer == 5
        assert attempt_arg.is_correct is True
        assert attempt_arg.response_time_ms == 2500
        
        # Verify stats increment was called
        mock_quiz_repository.increment_session_stats.assert_called_once_with("session-456", True)

    def test_record_answer_incorrect(self, quiz_service, mock_quiz_repository, sample_problem_attempt):
        """Test recording an incorrect answer."""
        incorrect_attempt = ProblemAttempt(
            id="attempt-124",
            session_id="session-456",
            problem="2 + 3",
            user_answer=6,
            correct_answer=5,
            is_correct=False,
            response_time_ms=2500,
            timestamp=datetime(2023, 1, 1, 12, 15, 0)
        )
        mock_quiz_repository.save_attempt.return_value = incorrect_attempt
        mock_quiz_repository.increment_session_stats.return_value = True
        
        with patch('src.domain.services.quiz_service.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2023, 1, 1, 12, 15, 0)
            
            result = quiz_service.record_answer("session-456", "2 + 3", 6, 5, 2500)
        
        assert result is True
        
        # Verify correct answer evaluation
        attempt_arg = mock_quiz_repository.save_attempt.call_args[0][0]
        assert attempt_arg.is_correct is False
        
        # Verify stats increment was called with False
        mock_quiz_repository.increment_session_stats.assert_called_once_with("session-456", False)

    def test_record_answer_none_user_answer(self, quiz_service, mock_quiz_repository, sample_problem_attempt):
        """Test recording when user provides no answer."""
        no_answer_attempt = ProblemAttempt(
            id="attempt-125",
            session_id="session-456",
            problem="2 + 3",
            user_answer=None,
            correct_answer=5,
            is_correct=False,
            response_time_ms=2500,
            timestamp=datetime(2023, 1, 1, 12, 15, 0)
        )
        mock_quiz_repository.save_attempt.return_value = no_answer_attempt
        mock_quiz_repository.increment_session_stats.return_value = True
        
        result = quiz_service.record_answer("session-456", "2 + 3", None, 5, 2500)
        
        assert result is True
        
        # Verify None answer is handled correctly
        attempt_arg = mock_quiz_repository.save_attempt.call_args[0][0]
        assert attempt_arg.user_answer is None
        assert attempt_arg.is_correct is False

    def test_record_answer_save_attempt_fails(self, quiz_service, mock_quiz_repository):
        """Test record_answer when save_attempt fails."""
        mock_quiz_repository.save_attempt.return_value = None
        
        result = quiz_service.record_answer("session-456", "2 + 3", 5, 5, 2500)
        
        assert result is False
        # Should not call increment_session_stats if save_attempt fails
        mock_quiz_repository.increment_session_stats.assert_not_called()

    def test_record_answer_increment_stats_fails(self, quiz_service, mock_quiz_repository, sample_problem_attempt):
        """Test record_answer when increment_session_stats fails."""
        mock_quiz_repository.save_attempt.return_value = sample_problem_attempt
        mock_quiz_repository.increment_session_stats.return_value = False
        
        result = quiz_service.record_answer("session-456", "2 + 3", 5, 5, 2500)
        
        assert result is False


class TestCompleteSession:
    """Test complete_session method."""

    def test_complete_session_success(self, quiz_service, mock_quiz_repository, sample_quiz_session, sample_attempts):
        """Test successful session completion."""
        mock_quiz_repository.complete_session.return_value = sample_quiz_session
        mock_quiz_repository.get_session_attempts.return_value = sample_attempts
        
        result = quiz_service.complete_session("session-123")
        
        assert result is not None
        assert isinstance(result, QuizSessionResult)
        assert result.session == sample_quiz_session
        assert result.attempts == sample_attempts
        
        # Verify statistics calculations
        expected_avg = (2000 + 3000 + 4000) / 3  # 3000ms
        assert result.average_response_time == expected_avg
        assert result.fastest_correct_time == 2000  # Fastest correct answer
        assert result.slowest_correct_time == 3000  # Slowest correct answer

    def test_complete_session_no_attempts(self, quiz_service, mock_quiz_repository, sample_quiz_session):
        """Test session completion with no attempts."""
        mock_quiz_repository.complete_session.return_value = sample_quiz_session
        mock_quiz_repository.get_session_attempts.return_value = []
        
        result = quiz_service.complete_session("session-123")
        
        assert result is not None
        assert result.average_response_time == 0.0
        assert result.fastest_correct_time is None
        assert result.slowest_correct_time is None

    def test_complete_session_only_incorrect_attempts(self, quiz_service, mock_quiz_repository, sample_quiz_session):
        """Test session completion with only incorrect attempts."""
        incorrect_attempts = [
            ProblemAttempt(
                id="attempt-1",
                session_id="session-123",
                problem="2 + 3",
                user_answer=6,
                correct_answer=5,
                is_correct=False,
                response_time_ms=2000,
                timestamp=datetime(2023, 1, 1, 12, 15, 0)
            )
        ]
        
        mock_quiz_repository.complete_session.return_value = sample_quiz_session
        mock_quiz_repository.get_session_attempts.return_value = incorrect_attempts
        
        result = quiz_service.complete_session("session-123")
        
        assert result is not None
        assert result.average_response_time == 2000.0
        assert result.fastest_correct_time is None
        assert result.slowest_correct_time is None

    def test_complete_session_repository_failure(self, quiz_service, mock_quiz_repository):
        """Test session completion when repository fails."""
        mock_quiz_repository.complete_session.return_value = None
        
        result = quiz_service.complete_session("session-123")
        
        assert result is None
        # Should not call get_session_attempts if complete_session fails
        mock_quiz_repository.get_session_attempts.assert_not_called()


class TestAbandonSession:
    """Test abandon_session method."""

    def test_abandon_session_success(self, quiz_service, mock_quiz_repository, sample_quiz_session):
        """Test successful session abandonment."""
        mock_quiz_repository.get_session.return_value = sample_quiz_session
        
        # Create updated session to return
        updated_session = QuizSession(
            id=sample_quiz_session.id,
            user_id=sample_quiz_session.user_id,
            quiz_type=sample_quiz_session.quiz_type,
            difficulty_level=sample_quiz_session.difficulty_level,
            start_time=sample_quiz_session.start_time,
            end_time=datetime(2023, 1, 1, 12, 45, 0),
            total_problems=sample_quiz_session.total_problems,
            correct_answers=sample_quiz_session.correct_answers,
            status=SessionStatus.ABANDONED
        )
        mock_quiz_repository.update_session.return_value = updated_session
        
        with patch('src.domain.services.quiz_service.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2023, 1, 1, 12, 45, 0)
            
            result = quiz_service.abandon_session("session-123")
        
        assert result is True
        
        # Verify session was modified correctly
        mock_quiz_repository.update_session.assert_called_once()
        session_arg = mock_quiz_repository.update_session.call_args[0][0]
        assert session_arg.status == SessionStatus.ABANDONED
        assert session_arg.end_time is not None

    def test_abandon_session_not_found(self, quiz_service, mock_quiz_repository):
        """Test abandoning a session that doesn't exist."""
        mock_quiz_repository.get_session.return_value = None
        
        result = quiz_service.abandon_session("nonexistent")
        
        assert result is False
        mock_quiz_repository.update_session.assert_not_called()

    def test_abandon_session_update_fails(self, quiz_service, mock_quiz_repository, sample_quiz_session):
        """Test abandon_session when update fails."""
        mock_quiz_repository.get_session.return_value = sample_quiz_session
        mock_quiz_repository.update_session.return_value = None
        
        result = quiz_service.abandon_session("session-123")
        
        assert result is False


class TestGetUserProgress:
    """Test get_user_progress method."""

    def test_get_user_progress_with_sessions(self, quiz_service, mock_quiz_repository):
        """Test getting user progress with completed sessions."""
        # Create sample completed sessions
        completed_sessions = [
            QuizSession(
                id="session-1",
                user_id="user-456",
                quiz_type=QuizType.ADDITION,
                difficulty_level=1,
                start_time=datetime(2023, 1, 1, 12, 0, 0),
                end_time=datetime(2023, 1, 1, 12, 10, 0),  # 10 minutes
                total_problems=10,
                correct_answers=8,
                status=SessionStatus.COMPLETED
            ),
            QuizSession(
                id="session-2",
                user_id="user-456",
                quiz_type=QuizType.ADDITION,
                difficulty_level=2,
                start_time=datetime(2023, 1, 2, 12, 0, 0),
                end_time=datetime(2023, 1, 2, 12, 20, 0),  # 20 minutes
                total_problems=15,
                correct_answers=15,
                status=SessionStatus.COMPLETED
            )
        ]
        
        recent_sessions = completed_sessions  # Same for simplicity
        
        mock_quiz_repository.get_user_sessions.side_effect = [
            recent_sessions,  # First call for recent sessions
            completed_sessions  # Second call for completed sessions
        ]
        
        result = quiz_service.get_user_progress("user-456", limit=10)
        
        assert isinstance(result, UserProgress)
        assert result.total_sessions == 2
        assert result.total_problems == 25  # 10 + 15
        assert result.total_correct == 23  # 8 + 15
        assert result.overall_accuracy == 92.0  # 23/25 * 100
        assert result.average_session_time == 900.0  # (600 + 1200) / 2 seconds
        assert result.best_accuracy == 100.0  # Second session was perfect
        assert result.recent_sessions == recent_sessions

    def test_get_user_progress_no_completed_sessions(self, quiz_service, mock_quiz_repository):
        """Test getting user progress with no completed sessions."""
        recent_sessions = [
            QuizSession(
                id="session-1",
                user_id="user-456",
                quiz_type=QuizType.ADDITION,
                difficulty_level=1,
                start_time=datetime(2023, 1, 1, 12, 0, 0),
                end_time=None,
                total_problems=5,
                correct_answers=3,
                status=SessionStatus.ACTIVE
            )
        ]
        
        mock_quiz_repository.get_user_sessions.side_effect = [
            recent_sessions,  # First call for recent sessions
            []  # Second call for completed sessions - empty
        ]
        
        result = quiz_service.get_user_progress("user-456", limit=10)
        
        assert result.total_sessions == 0
        assert result.total_problems == 0
        assert result.total_correct == 0
        assert result.overall_accuracy == 0.0
        assert result.average_session_time == 0.0
        assert result.best_accuracy == 0.0
        assert result.recent_sessions == recent_sessions

    def test_get_user_progress_sessions_with_no_end_time(self, quiz_service, mock_quiz_repository):
        """Test getting user progress when some sessions have no end time."""
        completed_sessions = [
            QuizSession(
                id="session-1",
                user_id="user-456",
                quiz_type=QuizType.ADDITION,
                difficulty_level=1,
                start_time=datetime(2023, 1, 1, 12, 0, 0),
                end_time=datetime(2023, 1, 1, 12, 10, 0),
                total_problems=10,
                correct_answers=8,
                status=SessionStatus.COMPLETED
            ),
            QuizSession(
                id="session-2",
                user_id="user-456",
                quiz_type=QuizType.ADDITION,
                difficulty_level=2,
                start_time=datetime(2023, 1, 2, 12, 0, 0),
                end_time=None,  # No end time
                total_problems=15,
                correct_answers=12,
                status=SessionStatus.COMPLETED
            )
        ]
        
        mock_quiz_repository.get_user_sessions.side_effect = [
            completed_sessions,
            completed_sessions
        ]
        
        result = quiz_service.get_user_progress("user-456", limit=10)
        
        # Should only consider sessions with valid duration for average time
        assert result.average_session_time == 600.0  # Only first session counted
        assert result.total_sessions == 2  # Both sessions counted for totals
        assert result.total_problems == 25  # Both sessions counted

    def test_get_user_progress_zero_problems(self, quiz_service, mock_quiz_repository):
        """Test getting user progress when total problems is zero."""
        completed_sessions = [
            QuizSession(
                id="session-1",
                user_id="user-456",
                quiz_type=QuizType.ADDITION,
                difficulty_level=1,
                start_time=datetime(2023, 1, 1, 12, 0, 0),
                end_time=datetime(2023, 1, 1, 12, 10, 0),
                total_problems=0,  # No problems completed
                correct_answers=0,
                status=SessionStatus.COMPLETED
            )
        ]
        
        mock_quiz_repository.get_user_sessions.side_effect = [
            completed_sessions,
            completed_sessions
        ]
        
        result = quiz_service.get_user_progress("user-456", limit=10)
        
        assert result.overall_accuracy == 0.0  # Should handle division by zero


class TestGetSessionDetails:
    """Test get_session_details method."""

    def test_get_session_details_success(self, quiz_service, mock_quiz_repository, sample_quiz_session, sample_attempts):
        """Test successful session details retrieval."""
        mock_quiz_repository.get_session.return_value = sample_quiz_session
        mock_quiz_repository.get_session_attempts.return_value = sample_attempts
        
        result = quiz_service.get_session_details("session-123")
        
        assert result is not None
        assert isinstance(result, QuizSessionResult)
        assert result.session == sample_quiz_session
        assert result.attempts == sample_attempts
        
        # Verify statistics calculations (same logic as complete_session)
        expected_avg = (2000 + 3000 + 4000) / 3
        assert result.average_response_time == expected_avg
        assert result.fastest_correct_time == 2000
        assert result.slowest_correct_time == 3000

    def test_get_session_details_session_not_found(self, quiz_service, mock_quiz_repository):
        """Test getting details for non-existent session."""
        mock_quiz_repository.get_session.return_value = None
        
        result = quiz_service.get_session_details("nonexistent")
        
        assert result is None
        # Should not call get_session_attempts if session not found
        mock_quiz_repository.get_session_attempts.assert_not_called()

    def test_get_session_details_no_attempts(self, quiz_service, mock_quiz_repository, sample_quiz_session):
        """Test getting details for session with no attempts."""
        mock_quiz_repository.get_session.return_value = sample_quiz_session
        mock_quiz_repository.get_session_attempts.return_value = []
        
        result = quiz_service.get_session_details("session-123")
        
        assert result is not None
        assert result.average_response_time == 0.0
        assert result.fastest_correct_time is None
        assert result.slowest_correct_time is None


class TestQuizSessionResultNamedTuple:
    """Test QuizSessionResult NamedTuple."""

    def test_quiz_session_result_creation(self, sample_quiz_session, sample_attempts):
        """Test creating QuizSessionResult instance."""
        result = QuizSessionResult(
            session=sample_quiz_session,
            attempts=sample_attempts,
            average_response_time=2500.0,
            fastest_correct_time=2000.0,
            slowest_correct_time=3000.0
        )
        
        assert result.session == sample_quiz_session
        assert result.attempts == sample_attempts
        assert result.average_response_time == 2500.0
        assert result.fastest_correct_time == 2000.0
        assert result.slowest_correct_time == 3000.0

    def test_quiz_session_result_fields(self):
        """Test QuizSessionResult field access."""
        result = QuizSessionResult(
            session=Mock(),
            attempts=[],
            average_response_time=0.0,
            fastest_correct_time=None,
            slowest_correct_time=None
        )
        
        # Test all fields are accessible
        assert hasattr(result, 'session')
        assert hasattr(result, 'attempts')
        assert hasattr(result, 'average_response_time')
        assert hasattr(result, 'fastest_correct_time')
        assert hasattr(result, 'slowest_correct_time')


class TestUserProgressNamedTuple:
    """Test UserProgress NamedTuple."""

    def test_user_progress_creation(self):
        """Test creating UserProgress instance."""
        progress = UserProgress(
            total_sessions=10,
            total_problems=100,
            total_correct=85,
            overall_accuracy=85.0,
            average_session_time=300.0,
            best_accuracy=95.0,
            recent_sessions=[]
        )
        
        assert progress.total_sessions == 10
        assert progress.total_problems == 100
        assert progress.total_correct == 85
        assert progress.overall_accuracy == 85.0
        assert progress.average_session_time == 300.0
        assert progress.best_accuracy == 95.0
        assert progress.recent_sessions == []

    def test_user_progress_fields(self):
        """Test UserProgress field access."""
        progress = UserProgress(
            total_sessions=0,
            total_problems=0,
            total_correct=0,
            overall_accuracy=0.0,
            average_session_time=0.0,
            best_accuracy=0.0,
            recent_sessions=[]
        )
        
        # Test all fields are accessible
        assert hasattr(progress, 'total_sessions')
        assert hasattr(progress, 'total_problems')
        assert hasattr(progress, 'total_correct')
        assert hasattr(progress, 'overall_accuracy')
        assert hasattr(progress, 'average_session_time')
        assert hasattr(progress, 'best_accuracy')
        assert hasattr(progress, 'recent_sessions')


@pytest.mark.unit
class TestQuizServiceIntegration:
    """Integration-style tests for QuizService."""

    def test_all_methods_use_repository(self, quiz_service, mock_quiz_repository):
        """Test that all methods interact with the repository appropriately."""
        # This test ensures that the service layer properly abstracts repository calls
        
        # Mock repository responses for various method calls
        mock_quiz_repository.create_session.return_value = Mock()
        mock_quiz_repository.save_attempt.return_value = Mock()
        mock_quiz_repository.increment_session_stats.return_value = True
        mock_quiz_repository.complete_session.return_value = Mock()
        mock_quiz_repository.get_session_attempts.return_value = []
        mock_quiz_repository.get_session.return_value = Mock()
        mock_quiz_repository.update_session.return_value = Mock()
        mock_quiz_repository.get_user_sessions.return_value = []
        
        # Test each service method calls appropriate repository methods
        quiz_service.start_quiz_session("user", "addition", 1)
        assert mock_quiz_repository.create_session.called
        
        quiz_service.record_answer("session", "1+1", 2, 2, 1000)
        assert mock_quiz_repository.save_attempt.called
        assert mock_quiz_repository.increment_session_stats.called
        
        quiz_service.complete_session("session")
        assert mock_quiz_repository.complete_session.called
        
        quiz_service.abandon_session("session")
        assert mock_quiz_repository.get_session.called
        
        quiz_service.get_user_progress("user")
        assert mock_quiz_repository.get_user_sessions.called
        
        quiz_service.get_session_details("session")
        # get_session should have been called multiple times by now
        assert mock_quiz_repository.get_session.call_count >= 2