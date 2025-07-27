"""Tests for AdditionFactService."""

import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime
from src.domain.services.addition_fact_service import AdditionFactService
from src.domain.models.addition_fact_performance import AdditionFactPerformance
from src.domain.models.mastery_level import MasteryLevel


@pytest.fixture
def mock_repository():
    """Create mock repository for testing."""
    return Mock()


@pytest.fixture
def service(mock_repository):
    """Create service with mock repository."""
    return AdditionFactService(mock_repository)


@pytest.fixture
def sample_performance():
    """Create sample performance for testing."""
    return AdditionFactPerformance(
        id="perf-123",
        user_id="user-456",
        fact_key="7+8",
        total_attempts=10,
        correct_attempts=8,
        total_response_time_ms=25000,
        mastery_level=MasteryLevel.PRACTICING,
    )


class TestAdditionFactServiceCreateFactKey:
    """Test fact key creation without normalization."""

    def test_create_fact_key_ascending_order(self, service):
        """Test fact key creation preserves operand order."""
        result = service.create_fact_key(3, 8)
        assert result == "3+8"

    def test_create_fact_key_descending_order(self, service):
        """Test fact key creation preserves operand order (no reordering)."""
        result = service.create_fact_key(8, 3)
        assert result == "8+3"

    def test_create_fact_key_equal_numbers(self, service):
        """Test fact key creation with equal numbers."""
        result = service.create_fact_key(5, 5)
        assert result == "5+5"

    def test_create_fact_key_zero(self, service):
        """Test fact key creation with zero."""
        result = service.create_fact_key(0, 7)
        assert result == "0+7"

        result = service.create_fact_key(7, 0)
        assert result == "7+0"


class TestAdditionFactServiceTrackAttempt:
    """Test attempt tracking."""

    def test_track_attempt_success(self, service, mock_repository, sample_performance):
        """Test successful attempt tracking."""
        mock_repository.upsert_fact_performance.return_value = sample_performance

        result = service.track_attempt(
            user_id="user-456",
            operand1=7,
            operand2=8,
            is_correct=True,
            response_time_ms=3000,
        )

        assert result == sample_performance
        mock_repository.upsert_fact_performance.assert_called_once_with(
            user_id="user-456",
            fact_key="7+8",
            is_correct=True,
            response_time_ms=3000,
            timestamp=None,
        )

    def test_track_attempt_with_timestamp(self, service, mock_repository):
        """Test attempt tracking with specific timestamp."""
        timestamp = datetime.now()
        mock_repository.upsert_fact_performance.return_value = None

        service.track_attempt(
            user_id="user-456",
            operand1=8,
            operand2=3,  # Preserves order as 8+3
            is_correct=False,
            response_time_ms=5000,
            timestamp=timestamp,
        )

        mock_repository.upsert_fact_performance.assert_called_once_with(
            user_id="user-456",
            fact_key="8+3",
            is_correct=False,
            response_time_ms=5000,
            timestamp=timestamp,
        )


class TestAdditionFactServiceGetFactPerformance:
    """Test getting fact performance."""

    def test_get_fact_performance_success(
        self, service, mock_repository, sample_performance
    ):
        """Test successful fact performance retrieval."""
        mock_repository.get_user_fact_performance.return_value = sample_performance

        result = service.get_fact_performance("user-456", 7, 8)

        assert result == sample_performance
        mock_repository.get_user_fact_performance.assert_called_once_with(
            "user-456", "7+8"
        )

    def test_get_fact_performance_preserves_operands(self, service, mock_repository):
        """Test that operands are preserved when getting performance."""
        mock_repository.get_user_fact_performance.return_value = None

        service.get_fact_performance("user-456", 8, 3)  # Preserves order as 8+3

        mock_repository.get_user_fact_performance.assert_called_once_with(
            "user-456", "8+3"
        )


class TestAdditionFactServiceWeakFacts:
    """Test weak facts retrieval."""

    def test_get_weak_facts_default_parameters(
        self, service, mock_repository, sample_performance
    ):
        """Test getting weak facts with default parameters."""
        weak_facts = [sample_performance]
        mock_repository.get_weak_facts.return_value = weak_facts

        result = service.get_weak_facts("user-456")

        assert result == weak_facts
        mock_repository.get_weak_facts.assert_called_once_with("user-456", 3, 80.0, 10)

    def test_get_weak_facts_custom_parameters(self, service, mock_repository):
        """Test getting weak facts with custom parameters."""
        mock_repository.get_weak_facts.return_value = []

        service.get_weak_facts("user-456", min_attempts=5, max_accuracy=70.0, limit=5)

        mock_repository.get_weak_facts.assert_called_once_with("user-456", 5, 70.0, 5)


class TestAdditionFactServicePerformanceSummary:
    """Test performance summary."""

    def test_get_performance_summary_with_data(self, service, mock_repository):
        """Test performance summary with data."""
        summary_data = {
            "total_facts": 20,
            "learning": 5,
            "practicing": 8,
            "mastered": 7,
            "overall_accuracy": 85.5,
            "total_attempts": 200,
        }
        mock_repository.get_performance_summary.return_value = summary_data

        result = service.get_performance_summary("user-456")

        assert result["total_facts"] == 20
        assert result["mastery_percentage"] == 35.0  # 7/20 * 100
        assert result["proficiency_level"] == "Developing"  # 35% mastery
        mock_repository.get_performance_summary.assert_called_once_with("user-456")

    def test_get_performance_summary_expert_level(self, service, mock_repository):
        """Test performance summary for expert level."""
        summary_data = {
            "total_facts": 10,
            "mastered": 9,  # 90% mastery
            "learning": 1,
            "practicing": 0,
            "overall_accuracy": 95.0,
            "total_attempts": 100,
        }
        mock_repository.get_performance_summary.return_value = summary_data

        result = service.get_performance_summary("user-456")

        assert result["mastery_percentage"] == 90.0
        assert result["proficiency_level"] == "Expert"

    def test_get_performance_summary_no_facts(self, service, mock_repository):
        """Test performance summary with no facts."""
        summary_data = {
            "total_facts": 0,
            "learning": 0,
            "practicing": 0,
            "mastered": 0,
            "overall_accuracy": 0.0,
            "total_attempts": 0,
        }
        mock_repository.get_performance_summary.return_value = summary_data

        result = service.get_performance_summary("user-456")

        assert result["mastery_percentage"] == 0.0
        assert result["proficiency_level"] == "New Learner"


class TestAdditionFactServicePracticeRecommendations:
    """Test practice recommendations."""

    def test_get_practice_recommendations_with_weak_facts(
        self, service, mock_repository
    ):
        """Test practice recommendations with weak facts in range."""
        weak_fact = AdditionFactPerformance(
            id="perf-1",
            user_id="user-456",
            fact_key="3+5",  # In range 1-10
            total_attempts=5,
            correct_attempts=2,
            mastery_level=MasteryLevel.LEARNING,
        )

        mastered_fact = AdditionFactPerformance(
            id="perf-2",
            user_id="user-456",
            fact_key="2+4",  # In range 1-10
            total_attempts=10,
            correct_attempts=10,
            mastery_level=MasteryLevel.MASTERED,
        )

        mock_repository.get_weak_facts.return_value = [weak_fact]
        mock_repository.get_mastered_facts.return_value = [mastered_fact]

        result = service.get_practice_recommendations("user-456", (1, 10))

        assert result["session_range"] == "1 to 10"
        assert result["total_possible_facts"] == 100  # 10x10
        assert result["weak_facts_count"] == 1
        assert result["mastered_facts_count"] == 1
        assert len(result["weak_facts"]) == 1
        assert result["weak_facts"][0] == weak_fact
        assert "Focus on these 1 facts" in result["recommendation"]

    def test_get_practice_recommendations_all_mastered(self, service, mock_repository):
        """Test recommendations when all facts are mastered."""
        mock_repository.get_weak_facts.return_value = []

        # Mock mastered facts to equal total possible (simple case: 2x2 = 4 facts)
        mastered_facts = [
            AdditionFactPerformance(
                id=f"perf-{i}",
                user_id="user-456",
                fact_key=f"{i}+{j}",
                mastery_level=MasteryLevel.MASTERED,
            )
            for i in range(1, 3)
            for j in range(1, 3)
        ]
        mock_repository.get_mastered_facts.return_value = mastered_facts

        result = service.get_practice_recommendations("user-456", (1, 2))

        assert result["weak_facts_count"] == 0
        assert result["mastered_facts_count"] == 4
        assert result["total_possible_facts"] == 4
        assert "mastered all facts" in result["recommendation"].lower()


class TestAdditionFactServiceSessionAnalysis:
    """Test session analysis."""

    def test_analyze_session_performance_empty_attempts(self, service):
        """Test session analysis with no attempts."""
        result = service.analyze_session_performance("user-456", [])

        assert "error" in result
        assert result["error"] == "No attempts to analyze"

    def test_analyze_session_performance_with_attempts(self, service, mock_repository):
        """Test session analysis with attempts."""
        # Mock the track_attempt calls
        mock_repository.upsert_fact_performance.return_value = AdditionFactPerformance(
            id="perf-1",
            user_id="user-456",
            fact_key="3+5",
            total_attempts=1,
            correct_attempts=1,
            mastery_level=MasteryLevel.LEARNING,
        )

        session_attempts = [
            (3, 5, True, 2500),  # Correct attempt
            (3, 5, False, 4000),  # Incorrect attempt
            (7, 2, True, 3000),  # Correct attempt (preserves order as 7+2)
        ]

        result = service.analyze_session_performance("user-456", session_attempts)

        assert result["total_attempts"] == 3
        assert result["correct_attempts"] == 2
        assert result["session_accuracy"] == 66.7  # 2/3 * 100, rounded
        assert result["facts_practiced"] == 2  # "3+5" and "7+2"
        assert len(result["updated_performances"]) == 3  # 3 tracking calls


@pytest.mark.unit
class TestAdditionFactServiceUnit:
    """Unit tests for AdditionFactService."""

    def test_service_initialization(self, mock_repository):
        """Test service initialization."""
        service = AdditionFactService(mock_repository)
        assert service.fact_repository == mock_repository

    def test_generate_recommendation_text_edge_cases(self, service):
        """Test recommendation text generation edge cases."""
        # Test various scenarios
        assert (
            "mastered all facts"
            in service._generate_recommendation_text(0, 10, 10).lower()
        )
        assert (
            "no weak facts" in service._generate_recommendation_text(0, 5, 10).lower()
        )
        assert (
            "focus on these 2 facts"
            in service._generate_recommendation_text(2, 0, 10).lower()
        )
        assert (
            "facts need attention"
            in service._generate_recommendation_text(15, 0, 20).lower()
        )
