#!/usr/bin/env python3
"""Addition tables functionality using base classes for DRY code reuse."""

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


def get_addition_table_range() -> Tuple[int, int]:
    """Get the table range (low and high numbers, 1-100) from user for addition tables."""
    while True:
        try:
            low_input = get_user_input(
                "Enter low number for addition table (1-100)", "1"
            )
            low = int(low_input)
            if low < 1 or low > 100:
                print("❌ Please enter a number between 1 and 100")
                continue

            high_input = get_user_input(
                "Enter high number for addition table (1-100)", "10"
            )
            high = int(high_input)
            if high < 1 or high > 100:
                print("❌ Please enter a number between 1 and 100")
                continue

            if low > high:
                print("❌ Low number must be less than or equal to high number")
                continue

            return low, high
        except ValueError:
            print("❌ Please enter a valid number")


class AdditionTableGenerator(MathTableGenerator):
    """Addition table problem generator using base class."""

    def __init__(self, low: int, high: int, randomize: bool):
        super().__init__(randomize)
        self.low = low
        self.high = high
        self.initialize_problems()

    def get_operation_symbol(self) -> str:
        """Get the addition operation symbol."""
        return "+"

    def calculate_result(self, operand1: int, operand2: int) -> int:
        """Calculate addition result."""
        return operand1 + operand2

    def generate_problems(self) -> List[Tuple[str, int]]:
        """Generate all addition problems for the specified range."""
        problems = []
        for i in range(self.low, self.high + 1):
            for j in range(self.low, self.high + 1):
                problem = f"{i} + {j}"
                answer = self.calculate_result(i, j)
                problems.append((problem, answer))
        return problems

    def get_range_input_prompt(self) -> List[str]:
        """Get prompts for addition table range input."""
        return [
            "Enter low number for addition table (1-100)",
            "Enter high number for addition table (1-100)",
        ]


def run_addition_table_quiz(
    generator: AdditionTableGenerator,
    math_fact_service: Optional["MathFactService"] = None,
    user_id: Optional[str] = None,
) -> Tuple[int, int, int, float, List[Tuple[int, int, bool, int, int]]]:
    """Run the addition table quiz with optional fact tracking."""
    order_text = "random order" if generator.randomize else "sequential order"
    range_text = (
        f"{generator.low} to {generator.high}"
        if generator.low != generator.high
        else str(generator.low)
    )

    # Generate all problems for the quiz engine
    problems = []
    while generator.has_more_problems():
        problem_str, correct_answer = generator.get_next_problem()
        problems.append((problem_str, correct_answer))

    # Create config for the quiz session
    config = QuizSessionConfig(
        header_lines=[
            f"🎯 Addition Table for {range_text} ({order_text})",
            f"📝 {len(problems)} problems to solve",
        ],
        math_fact_service=math_fact_service,
        user_id=user_id,
        total_facts=len(problems),
        progress_format="Problem {current}/{total}",
        operation_symbol="+",
    )

    return _run_quiz_session(problems, config)


def practice_addition_specific_range(container=None, user=None):
    """Handle practicing a specific addition table range."""
    low, high = get_addition_table_range()
    randomize = get_order_preference()

    range_text = f"{low} to {high}" if low != high else str(low)
    total_problems = (high - low + 1) * (high - low + 1)

    print(f"\n📋 Settings:")
    print(f"   Range: Addition table for {range_text}")
    print(f"   Order: {'Random' if randomize else 'Sequential'}")
    print(f"   Total problems: {total_problems}")

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

    generator = AdditionTableGenerator(low, high, randomize)

    print(f"\n🏁 Starting addition table practice...")
    correct, total, skipped, duration, session_attempts = run_addition_table_quiz(
        generator, math_fact_service, user_id
    )

    # Track session performance with SM-2 if available
    if math_fact_service and user_id and session_attempts:
        math_fact_service.analyze_session_performance(user_id, session_attempts, "+")

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
    """Get addition facts that need remedial review based on poor performance."""
    all_performances = math_fact_service.get_all_user_performances(user_id)
    remedial_facts = []

    for performance in all_performances:
        # Only include addition facts
        if "+" not in performance.fact_key:
            continue

        # Check if fact needs remedial review (low ease factor or recent failures)
        if performance.easiness_factor < 1.8 or (
            performance.accuracy < 0.7 and performance.total_attempts >= 3
        ):
            try:
                # Parse fact key to get operands
                operands = performance.fact_key.split("+")
                if len(operands) == 2:
                    operand1, operand2 = int(operands[0]), int(operands[1])
                    remedial_facts.append((operand1, operand2))
            except (ValueError, IndexError):
                continue

    return remedial_facts


def conduct_remedial_review(
    remedial_facts: List[Tuple[int, int]], container=None, user=None
) -> None:
    """Conduct focused practice on facts needing remedial review."""
    if not remedial_facts:
        print("🎉 Great! No addition facts need remedial review at this time.")
        return

    print(f"\n🎯 Remedial Review: {len(remedial_facts)} addition facts need practice")
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
        problem_str = f"{operand1} + {operand2}"
        answer = operand1 + operand2
        problems.append((problem_str, answer))

    # Create quiz config
    config = QuizSessionConfig(
        header_lines=[
            "🎯 Remedial Review - Addition Facts",
            f"📝 {len(problems)} facts need extra practice",
            "🔄 Focus on accuracy to improve your mastery",
        ],
        show_results_on_exit=True,
        math_fact_service=math_fact_service,
        user_id=user_id,
        total_facts=len(problems),
        operation_symbol="+",
    )

    correct, total, skipped, duration, session_attempts = _run_quiz_session(
        problems, config
    )

    # Track session performance
    if math_fact_service and user_id and session_attempts:
        math_fact_service.analyze_session_performance(user_id, session_attempts, "+")


def review_due_facts(container=None, user=None):
    """Handle reviewing due addition facts with SM-2 integration."""
    if not container or not user:
        print("❌ Please sign in to access spaced repetition review")
        return

    math_fact_service = container.math_fact_svc
    user_id = user.id

    # Get scheduled facts due for review
    scheduled_facts = math_fact_service.get_facts_due_for_review(user_id, limit=100)

    # Get facts needing remedial review
    remedial_facts = get_facts_needing_remedial_review(math_fact_service, user_id)

    # Filter to addition facts only
    addition_scheduled = [f for f in scheduled_facts if "+" in f.fact_key]

    if not addition_scheduled and not remedial_facts:
        print("🎉 Excellent! No addition facts are due for review right now.")
        print("💡 Practice specific ranges to learn new facts or come back later!")
        return

    total_due = len(addition_scheduled) + len(remedial_facts)
    print(f"\n📚 Facts Due for Review: {total_due} addition facts")
    print(f"   📅 Scheduled review: {len(addition_scheduled)} facts")
    print(f"   🎯 Remedial review: {len(remedial_facts)} facts")

    # Combine scheduled and remedial facts
    all_problems = []

    # Add scheduled review problems
    for performance in addition_scheduled:
        try:
            operands = performance.fact_key.split("+")
            if len(operands) == 2:
                operand1, operand2 = int(operands[0]), int(operands[1])
                problem_str = f"{operand1} + {operand2}"
                answer = operand1 + operand2
                all_problems.append((problem_str, answer))
        except (ValueError, IndexError):
            continue

    # Add remedial review problems
    for operand1, operand2 in remedial_facts:
        problem_str = f"{operand1} + {operand2}"
        answer = operand1 + operand2
        all_problems.append((problem_str, answer))

    print(f"\n✅ Ready to start! Press Enter to begin...")
    try:
        input()
    except (EOFError, KeyboardInterrupt):
        return

    # Create quiz config
    config = QuizSessionConfig(
        header_lines=[
            "📚 Review Due Facts - Addition",
            f"📝 {len(all_problems)} facts ready for review",
            "🧠 Based on spaced repetition scheduling",
        ],
        show_results_on_exit=True,
        math_fact_service=math_fact_service,
        user_id=user_id,
        total_facts=len(all_problems),
        operation_symbol="+",
    )

    correct, total, skipped, duration, session_attempts = _run_quiz_session(
        all_problems, config
    )

    # Track session performance
    if session_attempts:
        math_fact_service.analyze_session_performance(user_id, session_attempts, "+")


def addition_tables_mode(container=None, user=None):
    """Addition tables mode using shared workflow."""
    return tables_mode_workflow(
        "Addition", practice_addition_specific_range, review_due_facts, container, user
    )


# Export the main function for backward compatibility
def get_addition_tables_choice(math_fact_service=None, user_id=None) -> int:
    """Get user's choice for addition tables submenu - DEPRECATED."""
    from .math_tables_base import get_tables_choice

    return get_tables_choice("Addition", math_fact_service, user_id)


def practice_specific_range(container=None, user=None):
    """Practice specific range - DEPRECATED, use practice_addition_specific_range."""
    return practice_addition_specific_range(container, user)


# Keep the old functions for any existing imports
from .math_tables_base import show_review_results
