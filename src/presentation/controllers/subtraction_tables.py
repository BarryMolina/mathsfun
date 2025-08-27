#!/usr/bin/env python3
"""Subtraction tables functionality with dual-range input system to ensure non-negative results."""

from typing import List, Tuple, Optional, TYPE_CHECKING
from ..cli.ui import get_user_input
from .math_tables_base import (
    MathTableGenerator,
    QuizSessionConfig,
    _run_quiz_session,
    get_order_preference,
    tables_mode_workflow,
    show_results_with_fact_insights,
)
from .session import show_results, prompt_start_session
from .analytics import view_analytics_mode
from src.domain.models.math_fact_performance import calculate_sm2_grade
from datetime import datetime, timezone

if TYPE_CHECKING:
    from src.domain.services.math_fact_service import MathFactService


def get_subtraction_table_ranges() -> Tuple[int, int, int, int]:
    """Get dual-range input for subtraction tables to ensure non-negative results.

    Returns:
        Tuple of (subtrahend_low, subtrahend_high, offset_low, offset_high)
    """
    print("\n📊 Subtraction Table Configuration")
    print("To ensure all answers are non-negative, subtraction tables use two ranges:")
    print("1. Subtrahend range (numbers being subtracted)")
    print("2. Minuend offset range (added to subtrahend to create minuend)")
    print("\nExample: Subtrahend 1-10, Offset 0-9 → Problems like 10-1, 11-2, 19-9")

    # Get subtrahend range
    while True:
        try:
            print("\n🔢 Subtrahend Range (numbers being subtracted):")
            subtrahend_low_input = get_user_input("Enter low subtrahend (1-100)", "1")
            subtrahend_low = int(subtrahend_low_input)
            if subtrahend_low < 1 or subtrahend_low > 100:
                print("❌ Please enter a number between 1 and 100")
                continue

            subtrahend_high_input = get_user_input(
                "Enter high subtrahend (1-100)", "10"
            )
            subtrahend_high = int(subtrahend_high_input)
            if subtrahend_high < 1 or subtrahend_high > 100:
                print("❌ Please enter a number between 1 and 100")
                continue

            if subtrahend_low > subtrahend_high:
                print("❌ Low number must be less than or equal to high number")
                continue

            break
        except ValueError:
            print("❌ Please enter valid numbers")

    # Get minuend offset range
    while True:
        try:
            print("\n➕ Minuend Offset Range (added to subtrahend to create minuend):")
            offset_low_input = get_user_input("Enter low offset (0-100)", "0")
            offset_low = int(offset_low_input)
            if offset_low < 0 or offset_low > 100:
                print("❌ Please enter a number between 0 and 100")
                continue

            offset_high_input = get_user_input("Enter high offset (0-100)", "9")
            offset_high = int(offset_high_input)
            if offset_high < 0 or offset_high > 100:
                print("❌ Please enter a number between 0 and 100")
                continue

            if offset_low > offset_high:
                print("❌ Low offset must be less than or equal to high offset")
                continue

            break
        except ValueError:
            print("❌ Please enter valid numbers")

    # Validate total range doesn't exceed reasonable limits
    total_problems = (subtrahend_high - subtrahend_low + 1) * (
        offset_high - offset_low + 1
    )
    if total_problems > 10000:
        print(f"⚠️  This configuration would create {total_problems} problems.")
        print("Consider using smaller ranges for better practice sessions.")
        confirm = get_user_input("Continue anyway? (y/n)", "n")
        if confirm.lower() not in ["y", "yes"]:
            return get_subtraction_table_ranges()  # Recursively ask again

    return subtrahend_low, subtrahend_high, offset_low, offset_high


class SubtractionTableGenerator(MathTableGenerator):
    """Subtraction table problem generator with dual-range system."""

    def __init__(
        self,
        subtrahend_low: int,
        subtrahend_high: int,
        offset_low: int,
        offset_high: int,
        randomize: bool,
    ):
        super().__init__(randomize)
        self.subtrahend_low = subtrahend_low
        self.subtrahend_high = subtrahend_high
        self.offset_low = offset_low
        self.offset_high = offset_high
        self.initialize_problems()

    def get_operation_symbol(self) -> str:
        """Get the subtraction operation symbol."""
        return "-"

    def calculate_result(self, operand1: int, operand2: int) -> int:
        """Calculate subtraction result (minuend - subtrahend)."""
        return operand1 - operand2

    def generate_problems(self) -> List[Tuple[str, int]]:
        """Generate all subtraction problems using dual-range system.

        For each subtrahend, create problems with all offset values:
        minuend = subtrahend + offset, ensuring all results ≥ 0
        """
        problems = []
        for subtrahend in range(self.subtrahend_low, self.subtrahend_high + 1):
            for offset in range(self.offset_low, self.offset_high + 1):
                minuend = subtrahend + offset
                problem = f"{minuend} - {subtrahend}"
                answer = self.calculate_result(minuend, subtrahend)
                # Verify answer is non-negative (should always be true with this system)
                assert answer >= 0, f"Negative result: {problem} = {answer}"
                problems.append((problem, answer))
        return problems

    def get_range_input_prompt(self) -> List[str]:
        """Get prompts for subtraction table range input."""
        return [
            "Subtrahend range (numbers being subtracted)",
            "Minuend offset range (added to create minuend)",
        ]

    def get_configuration_summary(self) -> str:
        """Get a summary of the current configuration."""
        subtrahend_range = (
            f"{self.subtrahend_low}-{self.subtrahend_high}"
            if self.subtrahend_low != self.subtrahend_high
            else str(self.subtrahend_low)
        )
        offset_range = (
            f"{self.offset_low}-{self.offset_high}"
            if self.offset_low != self.offset_high
            else str(self.offset_low)
        )
        return f"Subtrahend: {subtrahend_range}, Offset: {offset_range}"


def run_subtraction_table_quiz(
    generator: SubtractionTableGenerator,
    math_fact_service: Optional["MathFactService"] = None,
    user_id: Optional[str] = None,
) -> Tuple[int, int, int, float, List[Tuple[int, int, bool, int, int]]]:
    """Run the subtraction table quiz with optional fact tracking."""
    order_text = "random order" if generator.randomize else "sequential order"
    config_summary = generator.get_configuration_summary()

    # Generate all problems for the quiz engine
    problems = []
    while generator.has_more_problems():
        problem_str, correct_answer = generator.get_next_problem()
        problems.append((problem_str, correct_answer))

    # Create config for the quiz session
    config = QuizSessionConfig(
        header_lines=[
            f"🎯 Subtraction Table ({config_summary}) - {order_text}",
            f"📝 {len(problems)} problems to solve",
            "✅ All answers will be non-negative",
        ],
        math_fact_service=math_fact_service,
        user_id=user_id,
        total_facts=len(problems),
        progress_format="Problem {current}/{total}",
        operation_symbol="-",
    )

    return _run_quiz_session(problems, config)


def practice_subtraction_specific_range(container=None, user=None):
    """Handle practicing a specific subtraction table range."""
    subtrahend_low, subtrahend_high, offset_low, offset_high = (
        get_subtraction_table_ranges()
    )
    randomize = get_order_preference()

    # Calculate problem count
    subtrahend_count = subtrahend_high - subtrahend_low + 1
    offset_count = offset_high - offset_low + 1
    total_problems = subtrahend_count * offset_count

    print(f"\n📋 Settings:")
    print(
        f"   Subtrahend range: {subtrahend_low} to {subtrahend_high} ({subtrahend_count} numbers)"
    )
    print(f"   Offset range: {offset_low} to {offset_high} ({offset_count} offsets)")
    print(f"   Order: {'Random' if randomize else 'Sequential'}")
    print(f"   Total problems: {total_problems}")
    print(
        f"   Result range: {offset_low} to {subtrahend_high + offset_high - subtrahend_low}"
    )

    # Get services if available
    math_fact_service = None
    user_id = None
    if container and user:
        math_fact_service = container.math_fact_svc
        user_id = user.id

    print(f"\n✅ Ready to start! Press Enter to begin...")
    try:
        input()
    except (EOFError, KeyboardInterrupt):
        return

    generator = SubtractionTableGenerator(
        subtrahend_low, subtrahend_high, offset_low, offset_high, randomize
    )

    print(f"\n🏁 Starting subtraction table practice...")
    correct, total, skipped, duration, session_attempts = run_subtraction_table_quiz(
        generator, math_fact_service, user_id
    )

    # Track session performance with SM-2 if available
    if math_fact_service and user_id and session_attempts:
        math_fact_service.analyze_session_performance(user_id, session_attempts, "-")

    # Show results with fact insights
    show_results_with_fact_insights(
        correct,
        total,
        duration,
        generator,
        skipped,
        session_attempts,
        math_fact_service,
        user_id,
    )


def get_facts_needing_remedial_review(
    math_fact_service: "MathFactService", user_id: str
) -> List[Tuple[int, int]]:
    """Get subtraction facts that need remedial review based on poor performance."""
    all_performances = math_fact_service.get_all_user_performances(user_id)
    remedial_facts = []

    for performance in all_performances:
        # Only include subtraction facts
        if "-" not in performance.fact_key:
            continue

        # Check if fact needs remedial review (low ease factor or recent failures)
        if performance.easiness_factor < 1.8 or (
            performance.accuracy < 0.7 and performance.total_attempts >= 3
        ):
            try:
                # Parse fact key to get operands
                operands = performance.fact_key.split("-")
                if len(operands) == 2:
                    operand1, operand2 = int(operands[0]), int(operands[1])
                    remedial_facts.append((operand1, operand2))
            except (ValueError, IndexError):
                continue

    return remedial_facts


def conduct_remedial_review(
    remedial_facts: List[Tuple[int, int]], container=None, user=None
) -> None:
    """Conduct focused practice on subtraction facts needing remedial review."""
    if not remedial_facts:
        print("🎉 Great! No subtraction facts need remedial review at this time.")
        return

    print(
        f"\n🎯 Remedial Review: {len(remedial_facts)} subtraction facts need practice"
    )
    print("These are facts you've struggled with recently.")

    # Get services
    math_fact_service = None
    user_id = None
    if container and user:
        math_fact_service = container.math_fact_svc
        user_id = user.id

    print(f"\n✅ Ready to start! Press Enter to begin...")
    try:
        input()
    except (EOFError, KeyboardInterrupt):
        return

    # Create problems from remedial facts
    problems = []
    for operand1, operand2 in remedial_facts:
        problem_str = f"{operand1} - {operand2}"
        answer = operand1 - operand2
        problems.append((problem_str, answer))

    # Create quiz config
    config = QuizSessionConfig(
        header_lines=[
            "🎯 Remedial Review - Subtraction Facts",
            f"📝 {len(problems)} facts need extra practice",
            "🔄 Focus on accuracy to improve your mastery",
        ],
        show_results_on_exit=True,
        math_fact_service=math_fact_service,
        user_id=user_id,
        total_facts=len(problems),
        operation_symbol="-",
    )

    correct, total, skipped, duration, session_attempts = _run_quiz_session(
        problems, config
    )

    # Track session performance
    if math_fact_service and user_id and session_attempts:
        math_fact_service.analyze_session_performance(user_id, session_attempts, "-")


def review_due_facts(container=None, user=None):
    """Handle reviewing due subtraction facts with SM-2 integration."""
    if not container or not user:
        print("❌ Please sign in to access spaced repetition review")
        return

    math_fact_service = container.math_fact_svc
    user_id = user.id

    # Get scheduled facts due for review
    scheduled_facts = math_fact_service.get_facts_due_for_review(user_id, limit=100)

    # Get facts needing remedial review
    remedial_facts = get_facts_needing_remedial_review(math_fact_service, user_id)

    # Filter to subtraction facts only
    subtraction_scheduled = [f for f in scheduled_facts if "-" in f.fact_key]

    if not subtraction_scheduled and not remedial_facts:
        print("🎉 Excellent! No subtraction facts are due for review right now.")
        print("💡 Practice specific ranges to learn new facts or come back later!")
        return

    total_due = len(subtraction_scheduled) + len(remedial_facts)
    print(f"\n📚 Facts Due for Review: {total_due} subtraction facts")
    print(f"   📅 Scheduled review: {len(subtraction_scheduled)} facts")
    print(f"   🎯 Remedial review: {len(remedial_facts)} facts")

    # Combine scheduled and remedial facts
    all_problems = []

    # Add scheduled review problems
    for performance in subtraction_scheduled:
        try:
            operands = performance.fact_key.split("-")
            if len(operands) == 2:
                operand1, operand2 = int(operands[0]), int(operands[1])
                problem_str = f"{operand1} - {operand2}"
                answer = operand1 - operand2
                all_problems.append((problem_str, answer))
        except (ValueError, IndexError):
            continue

    # Add remedial review problems
    for operand1, operand2 in remedial_facts:
        problem_str = f"{operand1} - {operand2}"
        answer = operand1 - operand2
        all_problems.append((problem_str, answer))

    print(f"\n✅ Ready to start! Press Enter to begin...")
    try:
        input()
    except (EOFError, KeyboardInterrupt):
        return

    # Create quiz config
    config = QuizSessionConfig(
        header_lines=[
            "📚 Review Due Facts - Subtraction",
            f"📝 {len(all_problems)} facts ready for review",
            "🧠 Based on spaced repetition scheduling",
        ],
        show_results_on_exit=True,
        math_fact_service=math_fact_service,
        user_id=user_id,
        total_facts=len(all_problems),
        operation_symbol="-",
    )

    correct, total, skipped, duration, session_attempts = _run_quiz_session(
        all_problems, config
    )

    # Track session performance
    if session_attempts:
        math_fact_service.analyze_session_performance(user_id, session_attempts, "-")


def subtraction_tables_mode(container=None, user=None):
    """Subtraction tables mode using shared workflow."""
    return tables_mode_workflow(
        "Subtraction",
        practice_subtraction_specific_range,
        review_due_facts,
        container,
        user,
    )
