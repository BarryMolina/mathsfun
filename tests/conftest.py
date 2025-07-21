#!/usr/bin/env python3
"""Shared test fixtures and utilities for MathsFun tests."""

import pytest
from unittest.mock import Mock
from src.presentation.controllers.addition import ProblemGenerator

# Import fixtures from fixtures module
from tests.fixtures.user_fixtures import *


@pytest.fixture
def mock_generator():
    """Create a mock problem generator for testing."""
    generator = Mock()
    generator.is_unlimited = False
    generator.num_problems = 5
    generator.get_total_generated.return_value = 3
    return generator


@pytest.fixture
def unlimited_generator():
    """Create a mock unlimited problem generator for testing."""
    generator = Mock()
    generator.is_unlimited = True
    generator.get_total_generated.return_value = 10
    return generator


@pytest.fixture
def real_generator():
    """Create a real problem generator for integration tests."""
    return ProblemGenerator(low_difficulty=1, high_difficulty=2, num_problems=3)


@pytest.fixture
def sample_quiz_results():
    """Sample quiz results for testing result display."""
    return {
        "correct": 8,
        "total": 10,
        "duration": 125.5,  # 2m 5.5s
    }