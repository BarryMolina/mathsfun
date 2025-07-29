#!/usr/bin/env python3
"""
Core automation utilities for navigating the MathsFun CLI using pexpect.

This module provides the AutomatedNavigator class that enables programmatic
interaction with the MathsFun CLI application, supporting authentication,
menu navigation, quiz configuration, and session completion.
"""

import pexpect
import sys
import time
import re
from typing import Optional, List, Dict, Any, Tuple
from enum import Enum
from pathlib import Path


class NavigationState(Enum):
    """Enumeration of possible CLI navigation states."""

    UNKNOWN = "unknown"
    AUTH_MENU = "auth_menu"
    MAIN_MENU = "main_menu"
    ADDITION_CONFIG = "addition_config"
    ADDITION_TABLES_CONFIG = "addition_tables_config"
    QUIZ_ACTIVE = "quiz_active"
    QUIZ_RESULTS = "quiz_results"
    SIGNED_OUT = "signed_out"
    ERROR = "error"
    TERMINATED = "terminated"


class AutomatedNavigator:
    """
    Automated navigator for the MathsFun CLI application using pexpect.

    Provides methods to:
    - Launch and control the CLI process
    - Authenticate users with email/password
    - Navigate menus and configure quiz sessions
    - Complete quizzes with configurable strategies
    - Parse results and session data
    """

    # Pattern constants for CLI state detection
    PATTERNS = {
        "auth_menu": r"🔐 Authentication Required",
        "main_menu": r"📚 Main Menu:",
        "email_prompt": r"Email: ",
        "password_prompt": r"Password: ",
        "confirm_password_prompt": r"Confirm password: ",
        "select_option": r"Select an option \(\d+-\d+\): ",
        "addition_difficulty": r"Select difficulty range \(1-5\): ",
        "problem_count": r"How many problems\? \(0 for unlimited\): ",
        "table_range": r"Select table range \(1-100\): ",
        "table_order": r"Practice order.*\(1-2\): ",
        "quiz_problem": r"\d+\s*[+×]\s*\d+\s*=\s*",
        "quiz_result": r"(Correct!|Incorrect\.)",
        "session_complete": r"🎉 Session complete!",
        "results_summary": r"📊 Session Results",
        "press_enter": r"Press Enter",
        "invalid_input": r"Invalid (input|choice|email)",
        "auth_error": r"(Authentication failed|Error)",
        "signed_out": r"👋 You have been signed out",
    }

    def __init__(self, timeout: int = 10, encoding: str = "utf-8"):
        """
        Initialize the AutomatedNavigator.

        Args:
            timeout: Default timeout for pexpect operations
            encoding: Character encoding for the process
        """
        self.timeout = timeout
        self.encoding = encoding
        self.process: Optional[pexpect.spawn] = None
        self.current_state = NavigationState.UNKNOWN
        self.session_data: Dict[str, Any] = {}

    def launch_app(self, working_dir: Optional[str] = None) -> bool:
        """
        Launch the MathsFun CLI application.

        Args:
            working_dir: Working directory for the application

        Returns:
            True if launch successful, False otherwise
        """
        try:
            if working_dir:
                original_dir = Path.cwd()
                Path(working_dir).mkdir(parents=True, exist_ok=True)

            # Launch the main application with explicit environment
            import os
            env = os.environ.copy()
            env['PYTHONUNBUFFERED'] = '1'
            env['MATHSFUN_TEST_MODE'] = '1'  # Enable test mode for password input
            
            # Use local Supabase environment for automation testing
            env['ENVIRONMENT'] = 'local'
            env['SUPABASE_URL'] = 'http://127.0.0.1:54321'
            env['SUPABASE_ANON_KEY'] = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6ImFub24iLCJleHAiOjE5ODM4MTI5OTZ9.CRXP1A7WOeoJeXxjNni43kdQwgnWNReilDMblYTn_I0'
            env['SUPABASE_HEALTH_ENDPOINT'] = '/rest/v1/'  # Use REST API endpoint for health check
            
            cmd = f"{sys.executable} main.py"
            self.process = pexpect.spawn(
                cmd, 
                timeout=self.timeout, 
                encoding=self.encoding,
                env=env,
                dimensions=(24, 80)  # Set terminal dimensions
            )

            # Enable logging for debugging
            if hasattr(self.process, "logfile_read"):
                self.process.logfile_read = sys.stdout

            # Wait for initial state
            self._detect_current_state()
            return True

        except Exception as e:
            print(f"Failed to launch application: {e}")
            return False

    def _detect_current_state(self) -> NavigationState:
        """
        Detect the current state of the CLI application.

        Returns:
            Current navigation state
        """
        if not self.process or not self.process.isalive():
            self.current_state = NavigationState.TERMINATED
            return self.current_state

        try:
            # Try to match against known patterns
            patterns = list(self.PATTERNS.values())
            pattern_keys = list(self.PATTERNS.keys())

            timeout_eof_patterns = [pexpect.TIMEOUT, pexpect.EOF]
            all_patterns = patterns + timeout_eof_patterns
            index = self.process.expect(all_patterns, timeout=2)  # type: ignore[arg-type]

            if index < len(patterns):
                matched_pattern = pattern_keys[index]

                if matched_pattern == "auth_menu":
                    self.current_state = NavigationState.AUTH_MENU
                elif matched_pattern == "main_menu":
                    self.current_state = NavigationState.MAIN_MENU
                elif matched_pattern in ["quiz_problem", "quiz_result"]:
                    self.current_state = NavigationState.QUIZ_ACTIVE
                elif matched_pattern in ["session_complete", "results_summary"]:
                    self.current_state = NavigationState.QUIZ_RESULTS
                elif matched_pattern == "signed_out":
                    self.current_state = NavigationState.SIGNED_OUT
                elif matched_pattern in ["auth_error", "invalid_input"]:
                    self.current_state = NavigationState.ERROR
                else:
                    self.current_state = NavigationState.UNKNOWN

            elif index == len(patterns):  # TIMEOUT
                self.current_state = NavigationState.UNKNOWN
            else:  # EOF
                self.current_state = NavigationState.TERMINATED

        except Exception as e:
            print(f"State detection error: {e}")
            self.current_state = NavigationState.ERROR

        return self.current_state

    def wait_for_pattern(self, pattern: str, timeout: Optional[int] = None) -> bool:
        """
        Wait for a specific pattern to appear in the output.

        Args:
            pattern: Regular expression pattern to match
            timeout: Optional timeout override

        Returns:
            True if pattern found, False on timeout
        """
        if not self.process:
            return False

        try:
            self.process.expect(pattern, timeout=timeout or self.timeout)
            return True
        except (pexpect.TIMEOUT, pexpect.EOF):
            return False

    def send_input(self, text: str, expect_pattern: Optional[str] = None) -> bool:
        """
        Send input to the CLI process.

        Args:
            text: Text to send (without newline)
            expect_pattern: Optional pattern to wait for after sending

        Returns:
            True if successful, False otherwise
        """
        if not self.process:
            return False

        try:
            self.process.sendline(text)

            if expect_pattern:
                return self.wait_for_pattern(expect_pattern)

            # Small delay to allow processing
            time.sleep(0.1)
            return True

        except Exception as e:
            print(f"Input error: {e}")
            return False

    def authenticate_with_email(
        self, email: str, password: str, is_signup: bool = False
    ) -> bool:
        """
        Authenticate using email and password.

        Args:
            email: User email address
            password: User password
            is_signup: True for signup, False for signin

        Returns:
            True if authentication successful, False otherwise
        """
        if self.current_state != NavigationState.AUTH_MENU:
            if not self.wait_for_pattern(self.PATTERNS["auth_menu"]):
                return False

        try:
            # Select email/password option (2 for signin, 3 for signup)
            option = "3" if is_signup else "2"
            if not self.send_input(option, self.PATTERNS["email_prompt"]):
                return False

            # Enter email
            if not self.send_input(email, self.PATTERNS["password_prompt"]):
                return False

            # Enter password
            if is_signup:
                if not self.send_input(
                    password, self.PATTERNS["confirm_password_prompt"]
                ):
                    return False
                # Confirm password for signup
                if not self.send_input(password):
                    return False
            else:
                if not self.send_input(password):
                    return False

            # Wait for successful authentication (main menu)
            if self.wait_for_pattern(self.PATTERNS["main_menu"], timeout=15):
                self.current_state = NavigationState.MAIN_MENU
                self.session_data["authenticated"] = True
                self.session_data["email"] = email
                return True
            else:
                # Check for authentication error
                if self.wait_for_pattern(self.PATTERNS["auth_error"], timeout=5):
                    self.current_state = NavigationState.ERROR
                return False

        except Exception as e:
            print(f"Authentication error: {e}")
            return False

    def navigate_to_addition_mode(
        self, difficulty_range: Tuple[int, int] = (1, 3), num_problems: int = 5
    ) -> bool:
        """
        Navigate to addition practice mode with configuration.

        Args:
            difficulty_range: Tuple of (min_difficulty, max_difficulty) 1-5
            num_problems: Number of problems (0 for unlimited)

        Returns:
            True if navigation successful, False otherwise
        """
        if self.current_state != NavigationState.MAIN_MENU:
            if not self.wait_for_pattern(self.PATTERNS["main_menu"]):
                return False

        try:
            # Select Addition Practice (option 1)
            if not self.send_input("1", self.PATTERNS["addition_difficulty"]):
                return False

            # Configure difficulty range
            min_diff, max_diff = difficulty_range
            range_input = (
                f"{min_diff}-{max_diff}" if min_diff != max_diff else str(min_diff)
            )

            if not self.send_input(range_input, self.PATTERNS["problem_count"]):
                return False

            # Configure problem count
            if not self.send_input(str(num_problems)):
                return False

            # Wait for quiz to start
            if self.wait_for_pattern(self.PATTERNS["quiz_problem"], timeout=10):
                self.current_state = NavigationState.QUIZ_ACTIVE
                self.session_data["mode"] = "addition"
                self.session_data["difficulty_range"] = difficulty_range
                self.session_data["num_problems"] = num_problems
                return True

        except Exception as e:
            print(f"Addition mode navigation error: {e}")

        return False

    def navigate_to_addition_tables_mode(
        self, table_range: Tuple[int, int] = (1, 12), random_order: bool = True
    ) -> bool:
        """
        Navigate to addition tables mode with configuration.

        Args:
            table_range: Tuple of (min_table, max_table) 1-100
            random_order: True for random order, False for sequential

        Returns:
            True if navigation successful, False otherwise
        """
        if self.current_state != NavigationState.MAIN_MENU:
            if not self.wait_for_pattern(self.PATTERNS["main_menu"]):
                return False

        try:
            # Select Addition Tables (option 2)
            if not self.send_input("2", self.PATTERNS["table_range"]):
                return False

            # Configure table range
            min_table, max_table = table_range
            range_input = (
                f"{min_table}-{max_table}" if min_table != max_table else str(min_table)
            )

            if not self.send_input(range_input, self.PATTERNS["table_order"]):
                return False

            # Configure practice order (1=sequential, 2=random)
            order_option = "2" if random_order else "1"
            if not self.send_input(order_option):
                return False

            # Wait for quiz to start
            if self.wait_for_pattern(self.PATTERNS["quiz_problem"], timeout=10):
                self.current_state = NavigationState.QUIZ_ACTIVE
                self.session_data["mode"] = "addition_tables"
                self.session_data["table_range"] = table_range
                self.session_data["random_order"] = random_order
                return True

        except Exception as e:
            print(f"Addition tables navigation error: {e}")

        return False

    def complete_quiz_session(self, strategy: str = "perfect") -> bool:
        """
        Complete a quiz session using the specified strategy.

        Args:
            strategy: Quiz completion strategy:
                     - "perfect": Answer all questions correctly
                     - "mixed": Mix of correct/incorrect answers
                     - "incorrect": Answer all questions incorrectly
                     - "commands": Test quiz commands (next, stop)

        Returns:
            True if session completed successfully, False otherwise
        """
        if self.current_state != NavigationState.QUIZ_ACTIVE:
            return False

        problems_solved = 0
        max_problems = self.session_data.get("num_problems", 100)

        try:
            while (
                self.current_state == NavigationState.QUIZ_ACTIVE
                and problems_solved < max_problems
            ):
                # Wait for a quiz problem
                if not self.wait_for_pattern(self.PATTERNS["quiz_problem"], timeout=5):
                    # Check if we've reached results
                    if self.wait_for_pattern(
                        self.PATTERNS["session_complete"], timeout=2
                    ):
                        self.current_state = NavigationState.QUIZ_RESULTS
                        break
                    continue

                # Extract the math problem from the output
                if self.process:
                    before = str(self.process.before) if self.process.before else ""
                    after = str(self.process.after) if self.process.after else ""
                    problem_match = re.search(
                        r"(\d+)\s*([+×])\s*(\d+)\s*=\s*", before + after
                    )
                else:
                    problem_match = None

                if problem_match:
                    num1, operator, num2 = problem_match.groups()
                    answer = self._calculate_answer(int(num1), operator, int(num2))

                    # Apply strategy
                    if strategy == "perfect":
                        response = str(answer)
                    elif strategy == "incorrect":
                        response = str(answer + 1)  # Deliberately wrong
                    elif strategy == "mixed":
                        # Alternate between correct and incorrect
                        if problems_solved % 2 == 0:
                            response = str(answer)
                        else:
                            response = str(answer + 1)
                    elif strategy == "commands":
                        # Test commands every few problems
                        if problems_solved % 5 == 0 and problems_solved > 0:
                            response = "next"  # Skip problem
                        elif problems_solved % 10 == 0 and problems_solved > 5:
                            response = "stop"  # End session early
                            break
                        else:
                            response = str(answer)
                    else:
                        response = str(answer)  # Default to correct

                    # Send the response
                    self.send_input(response)
                    problems_solved += 1

                    # Brief pause between problems
                    time.sleep(0.2)
                else:
                    # Could not parse problem, try to continue
                    self.send_input("0")

            # Wait for session completion
            if self.wait_for_pattern(self.PATTERNS["session_complete"], timeout=10):
                self.current_state = NavigationState.QUIZ_RESULTS
                self.session_data["problems_completed"] = problems_solved
                self.session_data["strategy"] = strategy
                return True

        except Exception as e:
            print(f"Quiz completion error: {e}")

        return False

    def _calculate_answer(self, num1: int, operator: str, num2: int) -> int:
        """Calculate the answer to a math problem."""
        if operator == "+":
            return num1 + num2
        elif operator == "×":
            return num1 * num2
        else:
            return 0  # Unknown operator

    def get_session_results(self) -> Dict[str, Any]:
        """
        Parse and return session results.

        Returns:
            Dictionary containing session results and metrics
        """
        if self.current_state != NavigationState.QUIZ_RESULTS:
            return {}

        results = dict(self.session_data)

        try:
            # Wait for results summary
            if self.wait_for_pattern(self.PATTERNS["results_summary"], timeout=5):
                # Extract results from output (simplified parsing)
                if self.process:
                    before = str(self.process.before) if self.process.before else ""
                    after = str(self.process.after) if self.process.after else ""
                    output = before + after
                else:
                    output = ""

                # Look for common result patterns
                accuracy_match = re.search(r"Accuracy: (\d+)%", output)
                if accuracy_match:
                    results["accuracy"] = int(accuracy_match.group(1))

                time_match = re.search(r"Total time: ([\d.]+)", output)
                if time_match:
                    results["total_time"] = float(time_match.group(1))

                results["results_parsed"] = True
            else:
                results["results_parsed"] = False

        except Exception as e:
            print(f"Results parsing error: {e}")
            results["parsing_error"] = str(e)

        return results

    def return_to_main_menu(self) -> bool:
        """
        Return to the main menu from current state.

        Returns:
            True if successfully returned to main menu, False otherwise
        """
        try:
            # Handle different states
            if self.current_state == NavigationState.QUIZ_RESULTS:
                # Usually just need to press Enter to continue
                if self.wait_for_pattern(self.PATTERNS["press_enter"], timeout=5):
                    self.send_input("")

            # Wait for main menu
            if self.wait_for_pattern(self.PATTERNS["main_menu"], timeout=10):
                self.current_state = NavigationState.MAIN_MENU
                return True

        except Exception as e:
            print(f"Main menu navigation error: {e}")

        return False

    def sign_out(self) -> bool:
        """
        Sign out the current user.

        Returns:
            True if sign out successful, False otherwise
        """
        if self.current_state != NavigationState.MAIN_MENU:
            if not self.return_to_main_menu():
                return False

        try:
            # Select sign out option (usually option 3)
            if not self.send_input("3"):
                return False

            # Wait for sign out confirmation
            if self.wait_for_pattern(self.PATTERNS["signed_out"], timeout=10):
                self.current_state = NavigationState.SIGNED_OUT
                self.session_data.clear()
                return True

        except Exception as e:
            print(f"Sign out error: {e}")

        return False

    def terminate(self) -> None:
        """Terminate the CLI process and cleanup."""
        if self.process and self.process.isalive():
            try:
                # Try graceful exit first
                self.process.sendcontrol("c")
                self.process.expect(pexpect.EOF, timeout=5)
            except:
                # Force termination
                self.process.terminate(force=True)

        self.process = None
        self.current_state = NavigationState.TERMINATED
        self.session_data.clear()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit with cleanup."""
        self.terminate()
