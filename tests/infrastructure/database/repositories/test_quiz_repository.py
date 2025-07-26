"""Comprehensive tests for QuizRepository class."""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from src.infrastructure.database.repositories.quiz_repository import QuizRepository
from src.domain.models.quiz_session import QuizSession, SessionStatus, QuizType
from src.domain.models.problem_attempt import ProblemAttempt


@pytest.fixture
def mock_supabase_manager():
    """Create mock Supabase manager."""
    mock_manager = Mock()
    mock_manager.is_authenticated.return_value = True
    return mock_manager


@pytest.fixture
def mock_client():
    """Create mock Supabase client."""
    return Mock()


@pytest.fixture
def quiz_repository(mock_supabase_manager, mock_client):
    """Create QuizRepository instance with mocked dependencies."""
    mock_supabase_manager.get_client.return_value = mock_client
    return QuizRepository(mock_supabase_manager)


@pytest.fixture
def sample_quiz_session():
    """Create sample quiz session for testing."""
    return QuizSession(
        id="session-123",
        user_id="user-456",
        quiz_type=QuizType.ADDITION,
        difficulty_level=1,
        start_time=datetime(2023, 1, 1, 12, 0, 0),
        end_time=datetime(2023, 1, 1, 12, 30, 0),
        status=SessionStatus.COMPLETED,
        total_problems=10,
        correct_answers=8,
    )


@pytest.fixture
def sample_session_dict():
    """Create sample session dictionary for API responses."""
    return {
        "id": "session-123",
        "user_id": "user-456",
        "start_time": "2023-01-01T12:00:00",
        "end_time": "2023-01-01T12:30:00",
        "status": "completed",
        "total_problems": 10,
        "correct_answers": 8,
        "difficulty_level": 1,  # Changed from difficulty_low/high to difficulty_level
        "quiz_type": "addition",  # Changed from problem_type to quiz_type
    }


@pytest.fixture
def sample_problem_attempt():
    """Create sample problem attempt for testing."""
    return ProblemAttempt(
        id="attempt-123",
        session_id="session-456",
        problem="2 + 3 = ?",
        correct_answer=5,
        user_answer=5,
        is_correct=True,
        timestamp=datetime(2023, 1, 1, 12, 15, 0),
        response_time_ms=2500,
    )


@pytest.fixture
def sample_attempt_dict():
    """Create sample attempt dictionary for API responses."""
    return {
        "id": "attempt-123",
        "session_id": "session-456",
        "problem": "2 + 3 = ?",
        "correct_answer": 5,
        "user_answer": 5,
        "is_correct": True,
        "timestamp": "2023-01-01T12:15:00",
        "response_time_ms": 2500,
    }


class TestQuizRepositoryInit:
    """Test QuizRepository initialization."""

    def test_init(self, mock_supabase_manager):
        """Test QuizRepository initialization."""
        repository = QuizRepository(mock_supabase_manager)
        assert repository.supabase_manager == mock_supabase_manager


class TestCreateSession:
    """Test create_session method."""

    def test_create_session_success(
        self, quiz_repository, mock_client, sample_quiz_session, sample_session_dict
    ):
        """Test successful session creation."""
        # Setup mock response
        mock_response = Mock()
        mock_response.data = [sample_session_dict]
        mock_client.table.return_value.insert.return_value.execute.return_value = (
            mock_response
        )

        # Execute
        result = quiz_repository.create_session(sample_quiz_session)

        # Verify
        assert result is not None
        assert isinstance(result, QuizSession)
        assert result.id == "session-123"
        assert result.user_id == "user-456"

        # Verify API calls
        mock_client.table.assert_called_once_with("quiz_sessions")
        insert_call = mock_client.table.return_value.insert
        insert_call.assert_called_once()

        # Verify that ID was removed from the data (to let database generate it)
        inserted_data = insert_call.call_args[0][0]
        assert "id" not in inserted_data

    def test_create_session_not_authenticated(self, mock_supabase_manager, mock_client):
        """Test create_session when not authenticated."""
        mock_supabase_manager.is_authenticated.return_value = False
        repository = QuizRepository(mock_supabase_manager)

        with patch("builtins.print") as mock_print:
            result = repository.create_session(Mock())

        assert result is None
        mock_print.assert_called_once_with("User not authenticated")

    def test_create_session_exception(
        self, quiz_repository, mock_client, sample_quiz_session
    ):
        """Test create_session with database exception."""
        mock_client.table.return_value.insert.return_value.execute.side_effect = (
            Exception("DB Error")
        )

        with patch("builtins.print") as mock_print:
            result = quiz_repository.create_session(sample_quiz_session)

        assert result is None
        mock_print.assert_called_once_with("Error creating quiz session: DB Error")

    def test_create_session_no_data_returned(
        self, quiz_repository, mock_client, sample_quiz_session
    ):
        """Test create_session when no data is returned."""
        mock_response = Mock()
        mock_response.data = None
        mock_client.table.return_value.insert.return_value.execute.return_value = (
            mock_response
        )

        result = quiz_repository.create_session(sample_quiz_session)
        assert result is None


class TestGetSession:
    """Test get_session method."""

    def test_get_session_success(
        self, quiz_repository, mock_client, sample_session_dict
    ):
        """Test successful session retrieval."""
        mock_response = Mock()
        mock_response.data = [sample_session_dict]
        mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value = (
            mock_response
        )

        result = quiz_repository.get_session("session-123")

        assert result is not None
        assert isinstance(result, QuizSession)
        assert result.id == "session-123"

        # Verify API calls
        mock_client.table.assert_called_once_with("quiz_sessions")
        mock_client.table.return_value.select.assert_called_once_with("*")
        mock_client.table.return_value.select.return_value.eq.assert_called_once_with(
            "id", "session-123"
        )

    def test_get_session_not_found(self, quiz_repository, mock_client):
        """Test get_session when session not found."""
        mock_response = Mock()
        mock_response.data = []
        mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value = (
            mock_response
        )

        result = quiz_repository.get_session("nonexistent")
        assert result is None

    def test_get_session_not_authenticated(self, mock_supabase_manager, mock_client):
        """Test get_session when not authenticated."""
        mock_supabase_manager.is_authenticated.return_value = False
        repository = QuizRepository(mock_supabase_manager)

        with patch("builtins.print") as mock_print:
            result = repository.get_session("session-123")

        assert result is None
        mock_print.assert_called_once_with("User not authenticated")

    def test_get_session_exception(self, quiz_repository, mock_client):
        """Test get_session with database exception."""
        mock_client.table.return_value.select.return_value.eq.return_value.execute.side_effect = Exception(
            "DB Error"
        )

        with patch("builtins.print") as mock_print:
            result = quiz_repository.get_session("session-123")

        assert result is None
        mock_print.assert_called_once_with("Error fetching quiz session: DB Error")


class TestUpdateSession:
    """Test update_session method."""

    def test_update_session_success(
        self, quiz_repository, mock_client, sample_quiz_session, sample_session_dict
    ):
        """Test successful session update."""
        mock_response = Mock()
        mock_response.data = [sample_session_dict]
        mock_client.table.return_value.update.return_value.eq.return_value.execute.return_value = (
            mock_response
        )

        result = quiz_repository.update_session(sample_quiz_session)

        assert result is not None
        assert isinstance(result, QuizSession)
        assert result.id == "session-123"

        # Verify API calls
        mock_client.table.assert_called_once_with("quiz_sessions")
        mock_client.table.return_value.update.assert_called_once()
        mock_client.table.return_value.update.return_value.eq.assert_called_once_with(
            "id", "session-123"
        )

    def test_update_session_not_authenticated(self, mock_supabase_manager, mock_client):
        """Test update_session when not authenticated."""
        mock_supabase_manager.is_authenticated.return_value = False
        repository = QuizRepository(mock_supabase_manager)

        with patch("builtins.print") as mock_print:
            result = repository.update_session(Mock())

        assert result is None
        mock_print.assert_called_once_with("User not authenticated")

    def test_update_session_exception(
        self, quiz_repository, mock_client, sample_quiz_session
    ):
        """Test update_session with database exception."""
        mock_client.table.return_value.update.return_value.eq.return_value.execute.side_effect = Exception(
            "DB Error"
        )

        with patch("builtins.print") as mock_print:
            result = quiz_repository.update_session(sample_quiz_session)

        assert result is None
        mock_print.assert_called_once_with("Error updating quiz session: DB Error")

    def test_update_session_no_data_returned(
        self, quiz_repository, mock_client, sample_quiz_session
    ):
        """Test update_session when no data is returned."""
        mock_response = Mock()
        mock_response.data = None
        mock_client.table.return_value.update.return_value.eq.return_value.execute.return_value = (
            mock_response
        )

        result = quiz_repository.update_session(sample_quiz_session)
        assert result is None


class TestCompleteSession:
    """Test complete_session method."""

    def test_complete_session_success(
        self, quiz_repository, mock_client, sample_session_dict
    ):
        """Test successful session completion."""
        mock_response = Mock()
        mock_response.data = [sample_session_dict]
        mock_client.table.return_value.update.return_value.eq.return_value.execute.return_value = (
            mock_response
        )

        with patch(
            "src.infrastructure.database.repositories.quiz_repository.datetime"
        ) as mock_datetime:
            mock_datetime.now.return_value.isoformat.return_value = (
                "2023-01-01T12:30:00"
            )
            result = quiz_repository.complete_session("session-123")

        assert result is not None
        assert isinstance(result, QuizSession)

        # Verify API calls
        mock_client.table.assert_called_once_with("quiz_sessions")
        update_call = mock_client.table.return_value.update
        update_call.assert_called_once()

        # Verify update data
        update_data = update_call.call_args[0][0]
        assert update_data["status"] == SessionStatus.COMPLETED.value
        assert "end_time" in update_data

    def test_complete_session_not_authenticated(
        self, mock_supabase_manager, mock_client
    ):
        """Test complete_session when not authenticated."""
        mock_supabase_manager.is_authenticated.return_value = False
        repository = QuizRepository(mock_supabase_manager)

        with patch("builtins.print") as mock_print:
            result = repository.complete_session("session-123")

        assert result is None
        mock_print.assert_called_once_with("User not authenticated")

    def test_complete_session_exception(self, quiz_repository, mock_client):
        """Test complete_session with database exception."""
        mock_client.table.return_value.update.return_value.eq.return_value.execute.side_effect = Exception(
            "DB Error"
        )

        with patch("builtins.print") as mock_print:
            result = quiz_repository.complete_session("session-123")

        assert result is None
        mock_print.assert_called_once_with("Error completing quiz session: DB Error")


class TestGetUserSessions:
    """Test get_user_sessions method."""

    def test_get_user_sessions_success(
        self, quiz_repository, mock_client, sample_session_dict
    ):
        """Test successful user sessions retrieval."""
        mock_response = Mock()
        mock_response.data = [sample_session_dict, sample_session_dict]
        mock_client.table.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value = (
            mock_response
        )

        result = quiz_repository.get_user_sessions("user-456")

        assert len(result) == 2
        assert all(isinstance(session, QuizSession) for session in result)

        # Verify API calls
        mock_client.table.assert_called_once_with("quiz_sessions")
        mock_client.table.return_value.select.assert_called_once_with("*")
        mock_client.table.return_value.select.return_value.eq.assert_called_once_with(
            "user_id", "user-456"
        )
        mock_client.table.return_value.select.return_value.eq.return_value.order.assert_called_once_with(
            "start_time", desc=True
        )
        mock_client.table.return_value.select.return_value.eq.return_value.order.return_value.limit.assert_called_once_with(
            50
        )

    def test_get_user_sessions_with_status_filter(
        self, quiz_repository, mock_client, sample_session_dict
    ):
        """Test get_user_sessions with status filter."""
        mock_response = Mock()
        mock_response.data = [sample_session_dict]

        # Mock the chain of method calls for status filtering
        mock_query = Mock()
        mock_query.eq.return_value.order.return_value.limit.return_value.execute.return_value = (
            mock_response
        )
        mock_client.table.return_value.select.return_value.eq.return_value = mock_query

        result = quiz_repository.get_user_sessions(
            "user-456", limit=25, status=SessionStatus.COMPLETED
        )

        assert len(result) == 1

        # Verify status filter was applied
        mock_query.eq.assert_called_with("status", SessionStatus.COMPLETED.value)

    def test_get_user_sessions_custom_limit(
        self, quiz_repository, mock_client, sample_session_dict
    ):
        """Test get_user_sessions with custom limit."""
        mock_response = Mock()
        mock_response.data = [sample_session_dict]
        mock_client.table.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value = (
            mock_response
        )

        result = quiz_repository.get_user_sessions("user-456", limit=25)

        # Verify custom limit was used
        mock_client.table.return_value.select.return_value.eq.return_value.order.return_value.limit.assert_called_once_with(
            25
        )

    def test_get_user_sessions_no_data(self, quiz_repository, mock_client):
        """Test get_user_sessions when no data is returned."""
        mock_response = Mock()
        mock_response.data = None
        mock_client.table.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.return_value = (
            mock_response
        )

        result = quiz_repository.get_user_sessions("user-456")
        assert result == []

    def test_get_user_sessions_not_authenticated(
        self, mock_supabase_manager, mock_client
    ):
        """Test get_user_sessions when not authenticated."""
        mock_supabase_manager.is_authenticated.return_value = False
        repository = QuizRepository(mock_supabase_manager)

        with patch("builtins.print") as mock_print:
            result = repository.get_user_sessions("user-456")

        assert result is None
        mock_print.assert_called_once_with("User not authenticated")

    def test_get_user_sessions_exception(self, quiz_repository, mock_client):
        """Test get_user_sessions with database exception."""
        mock_client.table.return_value.select.return_value.eq.return_value.order.return_value.limit.return_value.execute.side_effect = Exception(
            "DB Error"
        )

        with patch("builtins.print") as mock_print:
            result = quiz_repository.get_user_sessions("user-456")

        assert result == []
        mock_print.assert_called_once_with("Error fetching user sessions: DB Error")


class TestSaveAttempt:
    """Test save_attempt method."""

    def test_save_attempt_success(
        self, quiz_repository, mock_client, sample_problem_attempt, sample_attempt_dict
    ):
        """Test successful attempt saving."""
        mock_response = Mock()
        mock_response.data = [sample_attempt_dict]
        mock_client.table.return_value.insert.return_value.execute.return_value = (
            mock_response
        )

        result = quiz_repository.save_attempt(sample_problem_attempt)

        assert result is not None
        assert isinstance(result, ProblemAttempt)
        assert result.id == "attempt-123"

        # Verify API calls
        mock_client.table.assert_called_once_with("problem_attempts")
        insert_call = mock_client.table.return_value.insert
        insert_call.assert_called_once()

        # Verify that ID was removed from the data
        inserted_data = insert_call.call_args[0][0]
        assert "id" not in inserted_data

    def test_save_attempt_not_authenticated(self, mock_supabase_manager, mock_client):
        """Test save_attempt when not authenticated."""
        mock_supabase_manager.is_authenticated.return_value = False
        repository = QuizRepository(mock_supabase_manager)

        with patch("builtins.print") as mock_print:
            result = repository.save_attempt(Mock())

        assert result is None
        mock_print.assert_called_once_with("User not authenticated")

    def test_save_attempt_exception(
        self, quiz_repository, mock_client, sample_problem_attempt
    ):
        """Test save_attempt with database exception."""
        mock_client.table.return_value.insert.return_value.execute.side_effect = (
            Exception("DB Error")
        )

        with patch("builtins.print") as mock_print:
            result = quiz_repository.save_attempt(sample_problem_attempt)

        assert result is None
        mock_print.assert_called_once_with("Error saving problem attempt: DB Error")

    def test_save_attempt_no_data_returned(
        self, quiz_repository, mock_client, sample_problem_attempt
    ):
        """Test save_attempt when no data is returned."""
        mock_response = Mock()
        mock_response.data = None
        mock_client.table.return_value.insert.return_value.execute.return_value = (
            mock_response
        )

        result = quiz_repository.save_attempt(sample_problem_attempt)
        assert result is None


class TestGetSessionAttempts:
    """Test get_session_attempts method."""

    def test_get_session_attempts_success(
        self, quiz_repository, mock_client, sample_attempt_dict
    ):
        """Test successful session attempts retrieval."""
        mock_response = Mock()
        mock_response.data = [sample_attempt_dict, sample_attempt_dict]
        mock_client.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value = (
            mock_response
        )

        result = quiz_repository.get_session_attempts("session-456")

        assert len(result) == 2
        assert all(isinstance(attempt, ProblemAttempt) for attempt in result)

        # Verify API calls
        mock_client.table.assert_called_once_with("problem_attempts")
        mock_client.table.return_value.select.assert_called_once_with("*")
        mock_client.table.return_value.select.return_value.eq.assert_called_once_with(
            "session_id", "session-456"
        )
        mock_client.table.return_value.select.return_value.eq.return_value.order.assert_called_once_with(
            "timestamp"
        )

    def test_get_session_attempts_no_data(self, quiz_repository, mock_client):
        """Test get_session_attempts when no data is returned."""
        mock_response = Mock()
        mock_response.data = None
        mock_client.table.return_value.select.return_value.eq.return_value.order.return_value.execute.return_value = (
            mock_response
        )

        result = quiz_repository.get_session_attempts("session-456")
        assert result == []

    def test_get_session_attempts_not_authenticated(
        self, mock_supabase_manager, mock_client
    ):
        """Test get_session_attempts when not authenticated."""
        mock_supabase_manager.is_authenticated.return_value = False
        repository = QuizRepository(mock_supabase_manager)

        with patch("builtins.print") as mock_print:
            result = repository.get_session_attempts("session-456")

        assert result is None
        mock_print.assert_called_once_with("User not authenticated")

    def test_get_session_attempts_exception(self, quiz_repository, mock_client):
        """Test get_session_attempts with database exception."""
        mock_client.table.return_value.select.return_value.eq.return_value.order.return_value.execute.side_effect = Exception(
            "DB Error"
        )

        with patch("builtins.print") as mock_print:
            result = quiz_repository.get_session_attempts("session-456")

        assert result == []
        mock_print.assert_called_once_with("Error fetching session attempts: DB Error")


class TestIncrementSessionStats:
    """Test increment_session_stats method."""

    def test_increment_session_stats_success_correct(
        self, quiz_repository, mock_client, sample_quiz_session, sample_session_dict
    ):
        """Test successful stats increment for correct answer."""
        # Mock get_session to return existing session
        with patch.object(
            quiz_repository, "get_session", return_value=sample_quiz_session
        ):
            mock_response = Mock()
            mock_response.data = [sample_session_dict]
            mock_client.table.return_value.update.return_value.eq.return_value.execute.return_value = (
                mock_response
            )

            result = quiz_repository.increment_session_stats(
                "session-123", is_correct=True
            )

        assert result is True

        # Verify API calls
        mock_client.table.assert_called_once_with("quiz_sessions")
        update_call = mock_client.table.return_value.update
        update_call.assert_called_once_with(
            {"total_problems": 11, "correct_answers": 9}  # 10 + 1  # 8 + 1
        )

    def test_increment_session_stats_success_incorrect(
        self, quiz_repository, mock_client, sample_quiz_session, sample_session_dict
    ):
        """Test successful stats increment for incorrect answer."""
        with patch.object(
            quiz_repository, "get_session", return_value=sample_quiz_session
        ):
            mock_response = Mock()
            mock_response.data = [sample_session_dict]
            mock_client.table.return_value.update.return_value.eq.return_value.execute.return_value = (
                mock_response
            )

            result = quiz_repository.increment_session_stats(
                "session-123", is_correct=False
            )

        assert result is True

        # Verify update data
        update_call = mock_client.table.return_value.update
        update_call.assert_called_once_with(
            {"total_problems": 11, "correct_answers": 8}  # 10 + 1  # 8 + 0
        )

    def test_increment_session_stats_session_not_found(
        self, quiz_repository, mock_client
    ):
        """Test increment_session_stats when session is not found."""
        with patch.object(quiz_repository, "get_session", return_value=None):
            result = quiz_repository.increment_session_stats(
                "nonexistent", is_correct=True
            )

        assert result is False
        # Should not make update call
        mock_client.table.assert_not_called()

    def test_increment_session_stats_not_authenticated(
        self, mock_supabase_manager, mock_client
    ):
        """Test increment_session_stats when not authenticated."""
        mock_supabase_manager.is_authenticated.return_value = False
        repository = QuizRepository(mock_supabase_manager)

        with patch("builtins.print") as mock_print:
            result = repository.increment_session_stats("session-123", is_correct=True)

        assert result is None
        mock_print.assert_called_once_with("User not authenticated")

    def test_increment_session_stats_exception(
        self, quiz_repository, mock_client, sample_quiz_session
    ):
        """Test increment_session_stats with database exception."""
        with patch.object(
            quiz_repository, "get_session", return_value=sample_quiz_session
        ):
            mock_client.table.return_value.update.return_value.eq.return_value.execute.side_effect = Exception(
                "DB Error"
            )

            with patch("builtins.print") as mock_print:
                result = quiz_repository.increment_session_stats(
                    "session-123", is_correct=True
                )

        assert result is False
        mock_print.assert_called_once_with("Error incrementing session stats: DB Error")

    def test_increment_session_stats_update_returns_none(
        self, quiz_repository, mock_client, sample_quiz_session
    ):
        """Test increment_session_stats when update returns None."""
        with patch.object(
            quiz_repository, "get_session", return_value=sample_quiz_session
        ):
            mock_response = Mock()
            mock_response.data = None
            mock_client.table.return_value.update.return_value.eq.return_value.execute.return_value = (
                mock_response
            )

            result = quiz_repository.increment_session_stats(
                "session-123", is_correct=True
            )

        assert result is False


@pytest.mark.repository
class TestQuizRepositoryIntegration:
    """Integration-style tests for QuizRepository."""

    def test_repository_inheritance(self, quiz_repository):
        """Test that QuizRepository properly inherits from BaseRepository."""
        from src.infrastructure.database.repositories.base import BaseRepository

        assert isinstance(quiz_repository, BaseRepository)

    def test_all_methods_require_authentication(self):
        """Test that all public methods have authentication requirement."""
        from src.infrastructure.database.repositories.quiz_repository import (
            QuizRepository,
        )
        import inspect

        # Get all public methods
        methods = [
            method
            for method in dir(QuizRepository)
            if not method.startswith("_") and callable(getattr(QuizRepository, method))
        ]

        # Filter out inherited methods from BaseRepository
        quiz_specific_methods = [
            "create_session",
            "get_session",
            "update_session",
            "complete_session",
            "get_user_sessions",
            "save_attempt",
            "get_session_attempts",
            "increment_session_stats",
        ]

        for method_name in quiz_specific_methods:
            method = getattr(QuizRepository, method_name)
            # Check if the method has the requires_authentication decorator
            # This is evidenced by checking the method's wrapper attributes
            assert hasattr(method, "__wrapped__") or "requires_authentication" in str(
                method
            )
