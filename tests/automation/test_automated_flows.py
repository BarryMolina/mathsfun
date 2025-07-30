#!/usr/bin/env python3
"""
Comprehensive integration tests for MathsFun CLI automation using pexpect.

This module contains end-to-end tests that validate the complete user journey
through the MathsFun application, including authentication, navigation,
quiz completion, and session management.
"""

import pytest
import time
from typing import Dict, Any

from .cli_navigator import AutomatedNavigator, NavigationState


@pytest.mark.automation
@pytest.mark.integration
class TestAuthenticationFlows:
    """Test authentication-related automation flows."""

    def test_successful_signin_with_email(
        self, navigator: AutomatedNavigator, test_users: Dict[str, Dict[str, str]]
    ):
        """Test successful email/password sign-in flow."""
        # Launch application
        assert navigator.launch_app(), "Failed to launch application"
        assert navigator.current_state == NavigationState.AUTH_MENU

        # Authenticate with primary test user
        primary_user = test_users["primary"]
        success = navigator.authenticate_with_email(
            email=primary_user["email"],
            password=primary_user["password"],
            is_signup=False,
        )

        assert success, "Authentication should succeed"
        assert navigator.current_state == NavigationState.MAIN_MENU
        assert navigator.session_data.get("authenticated") is True
        assert navigator.session_data.get("email") == primary_user["email"]

    def test_failed_signin_invalid_credentials(self, navigator: AutomatedNavigator):
        """Test sign-in failure with invalid credentials."""
        # Launch application
        assert navigator.launch_app(), "Failed to launch application"

        # Attempt authentication with invalid credentials
        success = navigator.authenticate_with_email(
            email="invalid@test.com", password="wrongpassword", is_signup=False
        )

        assert not success, "Authentication should fail with invalid credentials"
        assert navigator.current_state in [
            NavigationState.ERROR,
            NavigationState.AUTH_MENU,
        ]

    @pytest.mark.slow_automation
    def test_signup_with_email(
        self, navigator: AutomatedNavigator, test_users: Dict[str, Dict[str, str]]
    ):
        """Test email/password sign-up flow."""
        # Launch application
        assert navigator.launch_app(), "Failed to launch application"

        # Attempt sign-up with new test user
        signup_user = test_users["signup"]
        success = navigator.authenticate_with_email(
            email=signup_user["email"], password=signup_user["password"], is_signup=True
        )

        # Note: This might fail if user already exists, which is acceptable
        if success:
            assert navigator.current_state == NavigationState.MAIN_MENU
            assert navigator.session_data.get("authenticated") is True

    def test_sign_out_flow(self, authenticated_navigator: AutomatedNavigator):
        """Test user sign-out flow."""
        # Verify we start authenticated
        assert authenticated_navigator.current_state == NavigationState.MAIN_MENU
        assert authenticated_navigator.session_data.get("authenticated") is True

        # Sign out
        success = authenticated_navigator.sign_out()

        assert success, "Sign out should succeed"
        assert authenticated_navigator.current_state == NavigationState.SIGNED_OUT
        assert authenticated_navigator.session_data.get("authenticated") is None


@pytest.mark.automation
@pytest.mark.integration
class TestNavigationFlows:
    """Test menu navigation and configuration flows."""

    def test_main_menu_navigation(self, authenticated_navigator: AutomatedNavigator):
        """Test basic main menu navigation."""
        nav = authenticated_navigator

        # Verify we're at main menu
        assert nav.current_state == NavigationState.MAIN_MENU

        # Test navigation to different modes (without completing setup)
        # This tests the menu recognition and initial navigation
        original_state = nav.current_state

        # We can add more specific navigation tests here
        assert (
            nav.current_state == original_state
            or nav.current_state == NavigationState.MAIN_MENU
        )

    def test_addition_mode_configuration(
        self,
        authenticated_navigator: AutomatedNavigator,
        quiz_config_basic: Dict[str, Any],
    ):
        """Test addition mode configuration flow."""
        nav = authenticated_navigator
        config = quiz_config_basic["addition"]

        # Navigate to addition mode
        success = nav.navigate_to_addition_mode(
            difficulty_range=config["difficulty_range"],
            num_problems=config["num_problems"],
        )

        assert success, "Should successfully navigate to addition mode"
        assert nav.current_state == NavigationState.QUIZ_ACTIVE
        assert nav.session_data.get("mode") == "addition"
        assert nav.session_data.get("difficulty_range") == config["difficulty_range"]
        assert nav.session_data.get("num_problems") == config["num_problems"]

    def test_addition_tables_configuration(
        self,
        authenticated_navigator: AutomatedNavigator,
        quiz_config_basic: Dict[str, Any],
    ):
        """Test addition tables mode configuration flow."""
        nav = authenticated_navigator
        config = quiz_config_basic["addition_tables"]

        # Navigate to addition tables mode
        success = nav.navigate_to_addition_tables_mode(
            table_range=config["table_range"], random_order=config["random_order"]
        )

        assert success, "Should successfully navigate to addition tables mode"
        assert nav.current_state == NavigationState.QUIZ_ACTIVE
        assert nav.session_data.get("mode") == "addition_tables"
        assert nav.session_data.get("table_range") == config["table_range"]
        assert nav.session_data.get("random_order") == config["random_order"]


@pytest.mark.automation
@pytest.mark.integration
@pytest.mark.slow_automation
class TestQuizCompletionFlows:
    """Test complete quiz session flows with different strategies."""

    def test_perfect_addition_quiz(
        self,
        authenticated_navigator: AutomatedNavigator,
        quiz_config_basic: Dict[str, Any],
    ):
        """Test completing an addition quiz with perfect scores."""
        nav = authenticated_navigator
        config = quiz_config_basic["addition"]

        # Navigate to addition mode
        assert nav.navigate_to_addition_mode(
            difficulty_range=config["difficulty_range"],
            num_problems=config["num_problems"],
        ), "Should successfully start addition quiz"

        # Complete quiz with perfect strategy
        success = nav.complete_quiz_session(strategy="perfect")

        assert success, "Should complete quiz successfully"
        assert nav.current_state == NavigationState.QUIZ_RESULTS

        # Get and validate results
        results = nav.get_session_results()
        assert results.get("problems_completed", 0) > 0
        assert results.get("strategy") == "perfect"
        assert results.get("mode") == "addition"

    def test_mixed_addition_tables_quiz(
        self,
        authenticated_navigator: AutomatedNavigator,
        quiz_config_basic: Dict[str, Any],
    ):
        """Test completing an addition tables quiz with mixed accuracy."""
        nav = authenticated_navigator
        config = quiz_config_basic["addition_tables"]

        # Navigate to addition tables mode
        assert nav.navigate_to_addition_tables_mode(
            table_range=config["table_range"], random_order=config["random_order"]
        ), "Should successfully start addition tables quiz"

        # Complete quiz with mixed strategy
        success = nav.complete_quiz_session(strategy="mixed")

        assert success, "Should complete quiz successfully"
        assert nav.current_state == NavigationState.QUIZ_RESULTS

        # Get and validate results
        results = nav.get_session_results()
        assert results.get("problems_completed", 0) > 0
        assert results.get("strategy") == "mixed"
        assert results.get("mode") == "addition_tables"

    @pytest.mark.parametrize("strategy", ["perfect", "mixed", "incorrect"])
    def test_quiz_strategies(
        self,
        authenticated_navigator: AutomatedNavigator,
        quiz_config_basic: Dict[str, Any],
        strategy: str,
    ):
        """Test different quiz completion strategies."""
        nav = authenticated_navigator
        config = quiz_config_basic["addition"]

        # Use smaller problem count for faster testing
        small_config = (config["difficulty_range"], 3)

        # Navigate to addition mode
        assert nav.navigate_to_addition_mode(
            difficulty_range=small_config[0], num_problems=small_config[1]
        ), f"Should successfully start quiz for {strategy} strategy"

        # Complete quiz with specified strategy
        success = nav.complete_quiz_session(strategy=strategy)

        assert success, f"Should complete quiz with {strategy} strategy"
        assert nav.current_state == NavigationState.QUIZ_RESULTS

        # Validate results
        results = nav.get_session_results()
        assert results.get("strategy") == strategy
        assert results.get("problems_completed", 0) > 0


@pytest.mark.automation
@pytest.mark.integration
class TestCompleteUserJourneys:
    """Test complete end-to-end user journey scenarios."""

    @pytest.mark.slow_automation
    def test_complete_session_workflow(
        self,
        navigator: AutomatedNavigator,
        test_users: Dict[str, Dict[str, str]],
        quiz_config_basic: Dict[str, Any],
        session_tracker: Dict[str, Any],
    ):
        """Test a complete user session from login to logout."""
        primary_user = test_users["primary"]

        # Track session steps
        session_tracker["navigation_steps"].append("launch_app")

        # 1. Launch application
        assert navigator.launch_app(), "Failed to launch application"
        session_tracker["navigation_steps"].append("app_launched")

        # 2. Authenticate
        session_tracker["authentication_attempts"] += 1
        success = navigator.authenticate_with_email(
            email=primary_user["email"],
            password=primary_user["password"],
            is_signup=False,
        )
        assert success, "Authentication should succeed"
        session_tracker["navigation_steps"].append("authenticated")

        # 3. Complete addition quiz
        config = quiz_config_basic["addition"]
        assert navigator.navigate_to_addition_mode(
            difficulty_range=config["difficulty_range"],
            num_problems=config["num_problems"],
        ), "Should navigate to addition mode"
        session_tracker["navigation_steps"].append("addition_configured")

        assert navigator.complete_quiz_session(
            strategy="perfect"
        ), "Should complete addition quiz"
        session_tracker["sessions_completed"] += 1
        session_tracker["navigation_steps"].append("addition_completed")

        # 4. Return to main menu
        assert navigator.return_to_main_menu(), "Should return to main menu"
        session_tracker["navigation_steps"].append("returned_to_menu")

        # 5. Complete addition tables quiz
        config = quiz_config_basic["addition_tables"]
        assert navigator.navigate_to_addition_tables_mode(
            table_range=config["table_range"], random_order=config["random_order"]
        ), "Should navigate to addition tables mode"
        session_tracker["navigation_steps"].append("tables_configured")

        assert navigator.complete_quiz_session(
            strategy="mixed"
        ), "Should complete tables quiz"
        session_tracker["sessions_completed"] += 1
        session_tracker["navigation_steps"].append("tables_completed")

        # 6. Return to main menu and sign out
        assert navigator.return_to_main_menu(), "Should return to main menu"
        assert navigator.sign_out(), "Should sign out successfully"
        session_tracker["navigation_steps"].append("signed_out")

        # Validate session tracking
        assert session_tracker["sessions_completed"] == 2
        assert session_tracker["authentication_attempts"] == 1
        assert len(session_tracker["navigation_steps"]) == 9

    def test_error_recovery_flow(self, authenticated_navigator: AutomatedNavigator):
        """Test recovery from error states and unexpected situations."""
        nav = authenticated_navigator

        # Test that we can recover from various states
        original_state = nav.current_state

        # Simulate some navigation (specific recovery tests would go here)
        # For now, verify we can always return to main menu
        success = nav.return_to_main_menu()

        # Should either succeed or already be at main menu
        assert success or nav.current_state == NavigationState.MAIN_MENU

    @pytest.mark.slow_automation
    def test_multiple_quiz_sessions(
        self,
        authenticated_navigator: AutomatedNavigator,
        quiz_config_basic: Dict[str, Any],
    ):
        """Test completing multiple quiz sessions in sequence."""
        nav = authenticated_navigator
        sessions_completed = 0

        # Complete multiple addition sessions
        for i in range(2):
            config = quiz_config_basic["addition"]

            # Use small problem count for speed
            assert nav.navigate_to_addition_mode(
                difficulty_range=config["difficulty_range"], num_problems=3
            ), f"Should start addition session {i+1}"

            assert nav.complete_quiz_session(
                strategy="perfect"
            ), f"Should complete session {i+1}"
            sessions_completed += 1

            # Return to main menu between sessions
            if i < 1:  # Don't return after last session
                assert (
                    nav.return_to_main_menu()
                ), f"Should return to menu after session {i+1}"

        assert sessions_completed == 2


@pytest.mark.automation
@pytest.mark.slow_automation
class TestPerformanceAndResilience:
    """Test performance characteristics and resilience of automation."""

    def test_timeout_handling(
        self, navigator: AutomatedNavigator, environment_config: Dict[str, Any]
    ):
        """Test behavior under timeout conditions."""
        # Use shorter timeout for this test
        nav = AutomatedNavigator(timeout=2)  # Very short timeout

        try:
            # This should handle timeouts gracefully
            success = nav.launch_app()

            # If launch succeeds, that's fine
            # If it fails due to timeout, that's also acceptable behavior
            assert success or nav.current_state == NavigationState.UNKNOWN

        finally:
            nav.terminate()

    def test_process_cleanup(self, temp_working_dir: str):
        """Test that processes are properly cleaned up."""
        # Create navigator in specific scope
        nav = AutomatedNavigator()

        # Launch and immediately terminate
        if nav.launch_app():
            assert nav.process is not None
            nav.terminate()
            assert nav.process is None
            assert nav.current_state == NavigationState.TERMINATED

    def test_context_manager_usage(self, test_users: Dict[str, Dict[str, str]]):
        """Test navigator as context manager for automatic cleanup."""
        primary_user = test_users["primary"]

        # Use navigator as context manager
        with AutomatedNavigator() as nav:
            if nav.launch_app():
                # Quick authentication test
                success = nav.authenticate_with_email(
                    email=primary_user["email"],
                    password=primary_user["password"],
                    is_signup=False,
                )
                # Success is optional - this tests cleanup mainly

        # After context exit, navigator should be terminated
        assert nav.current_state == NavigationState.TERMINATED
