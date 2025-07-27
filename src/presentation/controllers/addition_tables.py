#!/usr/bin/env python3
import random
import time
from typing import List, Tuple, Optional, TYPE_CHECKING
from ..cli.ui import get_user_input
from .session import show_results, prompt_start_session

if TYPE_CHECKING:
    from src.domain.services.addition_fact_service import AdditionFactService


def get_table_range() -> Tuple[int, int]:
    """Get the table range (low and high numbers, 1-100) from user"""
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


def get_order_preference() -> bool:
    """Get user preference for problem order. Returns True for random, False for sequential"""
    print("\n🔀 Problem Order:")
    print("1. Sequential (1+1, 1+2, 1+3...)")
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


def generate_addition_table_problems(low: int, high: int) -> List[Tuple[str, int]]:
    """Generate all problems for addition table from low to high"""
    problems = []
    for i in range(low, high + 1):
        for j in range(low, high + 1):
            problem = f"{i} + {j}"
            answer = i + j
            problems.append((problem, answer))
    return problems


class AdditionTableGenerator:
    """Manages addition table problems for quiz session"""

    def __init__(self, low: int, high: int, randomize: bool):
        self.low = low
        self.high = high
        self.randomize = randomize
        self.problems = generate_addition_table_problems(low, high)
        if randomize:
            random.shuffle(self.problems)
        self.current_index = 0
        self.total_problems = len(self.problems)
        self.is_unlimited = False
        self.num_problems = self.total_problems

    def get_next_problem(self) -> Tuple[str, int]:
        """Get the next problem from the table"""
        if self.current_index >= len(self.problems):
            raise IndexError("No more problems available")

        problem, answer = self.problems[self.current_index]
        self.current_index += 1
        return problem, answer

    def has_more_problems(self) -> bool:
        """Check if there are more problems available"""
        return self.current_index < len(self.problems)

    def get_total_generated(self) -> int:
        """Get total number of problems generated so far"""
        return self.current_index

    def get_progress_display(self) -> str:
        """Get progress display string"""
        return f"{self.current_index}/{self.total_problems}"


def run_addition_table_quiz(
    generator: AdditionTableGenerator,
    addition_fact_service: Optional["AdditionFactService"] = None,
    user_id: Optional[str] = None,
) -> Tuple[int, int, int, float, List[Tuple[int, int, bool, int]]]:
    """Run the addition table quiz with optional fact tracking"""
    order_text = "random order" if generator.randomize else "sequential order"
    range_text = (
        f"{generator.low} to {generator.high}"
        if generator.low != generator.high
        else str(generator.low)
    )
    print(f"\n🎯 Addition Table for {range_text} ({order_text})")
    print(f"📝 {generator.total_problems} problems to solve")
    print("Commands: 'next' (skip), 'stop' (return to menu), 'exit' (quit app)")
    print("=" * 60)

    input("Press Enter when ready to start...")

    start_time = time.time()
    correct_count = 0
    total_attempted = 0
    skipped_count = 0
    session_attempts: List[Tuple[int, int, bool, int]] = (
        []
    )  # Track attempts for fact performance

    while generator.has_more_problems():
        problem, correct_answer = generator.get_next_problem()
        progress = generator.get_progress_display()
        print(f"\n📝 Problem {progress}: {problem}")

        # Parse operands for fact tracking
        operands = problem.split(" + ")
        operand1, operand2 = int(operands[0]), int(operands[1])

        problem_start_time = time.time()
        problem_answered = False

        while True:
            user_input = input("Your answer: ").strip().lower()

            if user_input == "exit":
                end_time = time.time()
                duration = end_time - start_time
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

                    # Track the attempt for fact performance
                    session_attempts.append(
                        (operand1, operand2, True, response_time_ms)
                    )

                    break
                else:
                    print(f"❌ Not quite right. Try again!")
                    print("You can type 'next' to move on to the next problem.")

                    # Track incorrect attempt
                    session_attempts.append(
                        (operand1, operand2, False, response_time_ms)
                    )

            except ValueError:
                print("❌ Please enter a number, 'next', 'stop', or 'exit'")

    end_time = time.time()
    duration = end_time - start_time
    return correct_count, total_attempted, skipped_count, duration, session_attempts


def addition_tables_mode(container=None, user=None):
    """Handle addition tables workflow"""
    try:
        print("\n📊 Addition Tables Mode Selected!")

        low, high = get_table_range()
        randomize = get_order_preference()

        range_text = f"{low} to {high}" if low != high else str(low)
        total_problems = (high - low + 1) * (high - low + 1)

        print(f"\n📋 Settings:")
        print(f"   Range: Addition table for {range_text}")
        print(f"   Order: {'Random' if randomize else 'Sequential'}")
        print(f"   Total problems: {total_problems}")

        generator = AdditionTableGenerator(low, high, randomize)

        # Get services for fact tracking if available
        addition_fact_service = None
        user_id = None
        if container and user:
            addition_fact_service = container.addition_fact_svc
            user_id = user.id

        correct, total, skipped, duration, session_attempts = run_addition_table_quiz(
            generator, addition_fact_service, user_id
        )

        # Show enhanced results with fact tracking if available
        show_results_with_fact_insights(
            correct,
            total,
            duration,
            generator,
            skipped,
            session_attempts,
            addition_fact_service,
            user_id,
        )

    except Exception as e:
        print(f"❌ Error: {e}")
        print("Returning to main menu...")


def show_results_with_fact_insights(
    correct: int,
    total: int,
    duration: float,
    generator: AdditionTableGenerator,
    skipped: int,
    session_attempts: List[Tuple[int, int, bool, int]],
    addition_fact_service: Optional["AdditionFactService"] = None,
    user_id: Optional[str] = None,
) -> None:
    """Show results with fact-specific insights if fact tracking is available."""

    # Show standard results first
    show_results(correct, total, duration, generator, skipped_count=skipped)

    # Show fact insights if tracking is available
    if addition_fact_service and user_id and session_attempts:
        print("\n" + "=" * 60)
        print("📊 ADDITION FACT INSIGHTS")
        print("=" * 60)

        try:
            # Analyze session performance
            analysis = addition_fact_service.analyze_session_performance(
                user_id, session_attempts
            )

            if "error" not in analysis:
                # Show session analysis
                facts_practiced = analysis.get("facts_practiced", 0)
                print(f"📝 Facts practiced this session: {facts_practiced}")

                # Show mastery improvements
                mastery_improvements = analysis.get("mastery_improvements", [])
                if mastery_improvements:
                    print(f"\n🎉 MASTERED: {', '.join(mastery_improvements)}")

                # Show facts needing practice
                facts_needing_practice = analysis.get("facts_needing_practice", [])
                if facts_needing_practice:
                    print(f"\n💪 NEED PRACTICE: {', '.join(facts_needing_practice)}")

                # Get practice recommendations for this range
                session_range = (generator.low, generator.high)
                recommendations = addition_fact_service.get_practice_recommendations(
                    user_id, session_range
                )

                if recommendations.get("recommendation"):
                    print(f"\n🎯 RECOMMENDATION: {recommendations['recommendation']}")

                # Show range-specific performance summary
                weak_facts = recommendations.get("weak_facts", [])
                mastered_count = recommendations.get("mastered_facts_count", 0)
                total_possible = recommendations.get("total_possible_facts", 0)

                if total_possible > 0:
                    mastery_percentage = (mastered_count / total_possible) * 100
                    print(
                        f"\n📈 RANGE PROGRESS: {mastered_count}/{total_possible} facts mastered ({mastery_percentage:.1f}%)"
                    )

                if weak_facts:
                    weak_fact_keys = [f.fact_key for f in weak_facts]
                    print(f"🎯 FOCUS ON: {', '.join(weak_fact_keys)}")

        except Exception as e:
            print(f"\n⚠️  Could not load fact insights: {e}")

    elif not addition_fact_service:
        # Show message about signing in for enhanced features
        print("\n" + "=" * 60)
        print("🔐 SIGN IN FOR PERSONALIZED INSIGHTS")
        print("=" * 60)
        print("Sign in to track your progress on individual addition facts!")
        print("• See which facts you've mastered")
        print("• Get personalized practice recommendations")
        print("• Track improvement over time")
        print("• Identify facts that need more work")
