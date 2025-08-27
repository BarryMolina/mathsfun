#!/usr/bin/env python3
"""Base classes and common functionality for math tables (addition, subtraction, etc.)."""

import random
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List, Tuple, Optional, TYPE_CHECKING
from ..cli.ui import get_user_input
from .session import show_results
from .analytics import view_analytics_mode

if TYPE_CHECKING:
    from src.domain.services.math_fact_service import MathFactService


@dataclass
class QuizSessionConfig:
    """Configuration for quiz session behavior and display."""

    header_lines: List[str]
    commands_text: str = (
        "Commands: 'next' (skip), 'stop' (return to menu), 'exit' (quit app)"
    )
    progress_format: str = "Problem {current}/{total}"
    show_results_on_exit: bool = False
    math_fact_service: Optional["MathFactService"] = None
    user_id: Optional[str] = None
    total_facts: Optional[int] = None
    operation_symbol: str = "+"  # Default to addition for backward compatibility


class MathTableGenerator(ABC):
    """Abstract base class for math table problem generators."""

    def __init__(self, randomize: bool):
        self.randomize = randomize
        self.problems: List[Tuple[str, int]] = []
        self.current_index = 0
        self.total_problems = 0
        self.is_unlimited = False
        self.num_problems = 0

    @abstractmethod
    def get_operation_symbol(self) -> str:
        """Get the mathematical operation symbol (e.g., '+', '-')."""
        pass

    @abstractmethod
    def calculate_result(self, operand1: int, operand2: int) -> int:
        """Calculate the result of the operation."""
        pass

    @abstractmethod
    def generate_problems(self) -> List[Tuple[str, int]]:
        """Generate all problems for this table configuration."""
        pass

    @abstractmethod
    def get_range_input_prompt(self) -> List[str]:
        """Get the prompts for range input specific to this operation."""
        pass

    def initialize_problems(self):
        """Initialize the problems list and shuffle if needed."""
        self.problems = self.generate_problems()
        if self.randomize:
            random.shuffle(self.problems)
        self.current_index = 0
        self.total_problems = len(self.problems)
        self.num_problems = self.total_problems

    def get_next_problem(self) -> Tuple[str, int]:
        """Get the next problem from the table."""
        if self.current_index >= len(self.problems):
            raise IndexError("No more problems available")

        problem, answer = self.problems[self.current_index]
        self.current_index += 1
        return problem, answer

    def has_more_problems(self) -> bool:
        """Check if there are more problems available."""
        return self.current_index < len(self.problems)

    def get_total_generated(self) -> int:
        """Get total number of problems generated so far."""
        return self.current_index

    def get_progress_display(self) -> str:
        """Get progress display string."""
        return f"{self.current_index}/{self.total_problems}"


def _run_quiz_session(
    problems: List[Tuple[str, int]], config: QuizSessionConfig
) -> Tuple[int, int, int, float, List[Tuple[int, int, bool, int, int]]]:
    """Core quiz engine that handles the common quiz loop logic.

    Args:
        problems: List of (question_string, correct_answer) tuples
        config: QuizSessionConfig containing session behavior and display options

    Returns:
        Tuple of (correct_count, total_attempted, skipped_count, duration, session_attempts)
    """
    # Display session header
    for line in config.header_lines:
        print(line)
    print(config.commands_text)
    print("=" * 60)

    input("Press Enter when ready to start...")

    start_time = time.time()
    correct_count = 0
    total_attempted = 0
    skipped_count = 0
    session_attempts: List[Tuple[int, int, bool, int, int]] = []

    for i, (problem, correct_answer) in enumerate(problems):
        # Display progress
        progress_display = config.progress_format.format(
            current=i + 1, total=len(problems)
        )
        print(f"\n📝 {progress_display}: {problem}")

        # Parse operands for fact tracking (operation-agnostic)
        # Split on the operation symbol with spaces
        operation_symbol = f" {config.operation_symbol} "
        operands = problem.split(operation_symbol)
        operand1, operand2 = int(operands[0]), int(operands[1])

        problem_start_time = time.time()
        problem_answered = False
        incorrect_attempts_on_problem = 0

        while True:
            user_input = input("Your answer: ").strip().lower()

            if user_input == "exit":
                end_time = time.time()
                duration = end_time - start_time
                if (
                    config.show_results_on_exit
                    and config.math_fact_service
                    and config.user_id is not None
                ):
                    show_review_results(
                        correct_count,
                        total_attempted,
                        skipped_count,
                        duration,
                        session_attempts,
                        config.math_fact_service,
                        config.user_id,
                        config.total_facts or len(problems),
                        config.operation_symbol,
                    )
                return (
                    correct_count,
                    total_attempted,
                    skipped_count,
                    duration,
                    session_attempts,
                )
            elif user_input == "stop":
                end_time = time.time()
                duration = end_time - start_time
                if (
                    config.show_results_on_exit
                    and config.math_fact_service
                    and config.user_id is not None
                ):
                    show_review_results(
                        correct_count,
                        total_attempted,
                        skipped_count,
                        duration,
                        session_attempts,
                        config.math_fact_service,
                        config.user_id,
                        config.total_facts or len(problems),
                        config.operation_symbol,
                    )
                return (
                    correct_count,
                    total_attempted,
                    skipped_count,
                    duration,
                    session_attempts,
                )
            elif user_input == "next":
                print(f"⏭️  Skipped! The answer was {correct_answer}")
                skipped_count += 1
                # If they had incorrect attempts before skipping, record the final failed attempt
                if incorrect_attempts_on_problem > 0:
                    response_time_ms = int((time.time() - problem_start_time) * 1000)
                    session_attempts.append(
                        (
                            operand1,
                            operand2,
                            False,
                            response_time_ms,
                            incorrect_attempts_on_problem,
                        )
                    )
                break

            try:
                user_answer = int(user_input)
                response_time_ms = int((time.time() - problem_start_time) * 1000)
                total_attempted += 1
                is_correct = user_answer == correct_answer

                if is_correct:
                    print("✅ Correct! Great job!")
                    correct_count += 1
                    problem_answered = True
                    # Track the final correct attempt with count of previous incorrect attempts
                    session_attempts.append(
                        (
                            operand1,
                            operand2,
                            True,
                            response_time_ms,
                            incorrect_attempts_on_problem,
                        )
                    )
                    break
                else:
                    print(f"❌ Not quite right. Try again!")
                    print("You can type 'next' to move on to the next problem.")
                    incorrect_attempts_on_problem += 1

            except ValueError:
                print("❌ Please enter a number, 'next', 'stop', or 'exit'")

    # Completed all problems
    end_time = time.time()
    duration = end_time - start_time

    if (
        config.show_results_on_exit
        and config.math_fact_service
        and config.user_id is not None
    ):
        show_review_results(
            correct_count,
            total_attempted,
            skipped_count,
            duration,
            session_attempts,
            config.math_fact_service,
            config.user_id,
            config.total_facts or len(problems),
        )

    return (correct_count, total_attempted, skipped_count, duration, session_attempts)


def show_review_results(
    correct_count: int,
    total_attempted: int,
    skipped_count: int,
    duration: float,
    session_attempts: List[Tuple[int, int, bool, int, int]],
    math_fact_service: "MathFactService",
    user_id: str,
    total_facts: int,
    operation_symbol: str = "+",
) -> None:
    """Show results for review sessions with SM-2 insights."""
    # Show standard results
    accuracy = (correct_count / total_attempted * 100) if total_attempted > 0 else 0
    print("\n" + "=" * 60)
    print("🎯 REVIEW SESSION COMPLETE!")
    print("=" * 60)
    print(f"✅ Correct: {correct_count}")
    print(f"📊 Total Attempted: {total_attempted}")
    print(f"⏭️  Skipped: {skipped_count}")
    print(f"🎯 Accuracy: {accuracy:.1f}%")
    print(f"⏱️  Duration: {duration:.1f} seconds")

    # Show SM-2 insights if available
    if session_attempts:
        print("\n" + "=" * 60)
        print("📊 SM-2 SPACED REPETITION INSIGHTS")
        print("=" * 60)

        # Show facts that may need remedial review
        facts_needing_remedial = []
        for (
            operand1,
            operand2,
            is_correct,
            response_time_ms,
            incorrect_attempts,
        ) in session_attempts:
            if not is_correct or incorrect_attempts >= 2:
                facts_needing_remedial.append(
                    (operand1, operand2, is_correct, incorrect_attempts)
                )

        if facts_needing_remedial:
            print(f"\n⚠️  Facts that may need additional practice:")
            for (
                operand1,
                operand2,
                is_correct,
                incorrect_attempts,
            ) in facts_needing_remedial:
                status = (
                    "❌ Failed"
                    if not is_correct
                    else f"⚠️  Struggled ({incorrect_attempts} attempts)"
                )
                print(f"   {operand1} {operation_symbol} {operand2}: {status}")

        print(f"\n📈 Performance tracking updated for {len(session_attempts)} facts")
        print("🔄 Next review dates scheduled based on your performance")


def get_order_preference() -> bool:
    """Get user preference for problem order. Returns True for random, False for sequential."""
    print("\n🔀 Problem Order:")
    print("1. Sequential")
    print("2. Random order")

    while True:
        try:
            user_input = get_user_input("Select order", "1")
            choice = int(user_input)
            if choice == 1:
                return False
            elif choice == 2:
                return True
            else:
                print("❌ Please enter 1 or 2")
        except ValueError:
            print("❌ Please enter a valid number")


def get_tables_choice(operation_name: str, math_fact_service=None, user_id=None) -> int:
    """Get user's choice for tables submenu."""
    print(f"\n📊 {operation_name} Tables Options:")
    print("1. Practice a specific range")

    # Show review option if user is signed in
    if math_fact_service and user_id:
        # Get count of facts due for review (includes scheduled and remedial)
        facts_due = math_fact_service.get_facts_due_for_review(user_id, limit=100)
        due_count = len(facts_due)
        if due_count > 0:
            print(
                f"2. Review Due Facts ({due_count} facts ready - scheduled & remedial)"
            )
        else:
            print("2. Review Due Facts (none due)")
    else:
        print("2. Review Due Facts (sign in required)")

    # Show analytics option
    if math_fact_service and user_id:
        print("3. View Performance Analytics")
    else:
        print("3. View Performance Analytics (sign in required)")

    print("4. Return to main menu")

    while True:
        try:
            choice = int(get_user_input("Select option", "1"))
            if choice in [1, 2, 3, 4]:
                return choice
            else:
                print("❌ Please enter 1, 2, 3, or 4")
        except ValueError:
            print("❌ Please enter a valid number")


def tables_mode_workflow(
    operation_name: str, practice_function, review_function, container=None, user=None
):
    """Common workflow for any tables mode (addition, subtraction, etc.)."""
    try:
        print(f"\n📊 {operation_name} Tables Mode Selected!")

        # Get math fact service for checking due facts
        math_fact_service = None
        user_id = None
        if container and user:
            math_fact_service = container.math_fact_svc
            user_id = user.id

        while True:
            choice = get_tables_choice(operation_name, math_fact_service, user_id)

            if choice == 1:
                practice_function(container, user)
                break
            elif choice == 2:
                review_function(container, user)
                break
            elif choice == 3:
                view_analytics_mode(container, user)
                break
            elif choice == 4:
                return  # Return to main menu

    except Exception as e:
        print(f"❌ Error: {e}")
        print("Returning to main menu...")


def show_results_with_fact_insights(
    correct: int,
    total: int,
    duration: float,
    generator: MathTableGenerator,
    skipped: int,
    session_attempts: List[Tuple[int, int, bool, int, int]],
    math_fact_service: Optional["MathFactService"] = None,
    user_id: Optional[str] = None,
) -> None:
    """Show results with fact-specific insights if fact tracking is available."""
    # Show standard results first
    show_results(correct, total, duration, generator, skipped_count=skipped)

    # Show fact insights if tracking is available
    if math_fact_service and user_id and session_attempts:
        print("\n" + "=" * 60)
        print("📊 SM-2 SPACED REPETITION INSIGHTS")
        print("=" * 60)

        # Process session attempts for insights
        facts_attempted = len(session_attempts)
        facts_correct = sum(
            1 for _, _, is_correct, _, _ in session_attempts if is_correct
        )
        facts_struggled = sum(
            1 for _, _, _, _, attempts in session_attempts if attempts >= 2
        )

        print(f"📈 Facts attempted this session: {facts_attempted}")
        print(f"✅ Facts answered correctly: {facts_correct}")
        print(f"⚠️  Facts with multiple attempts: {facts_struggled}")

        if facts_struggled > 0:
            print(f"\n💡 {facts_struggled} facts may benefit from additional practice")

        print(f"\n🔄 Performance data updated - next review dates scheduled")
        print("📊 View Analytics for detailed insights on your progress!")
