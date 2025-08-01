#!/usr/bin/env python3
import random
import time
from datetime import datetime, timezone
from typing import List, Tuple, Optional, TYPE_CHECKING
from ..cli.ui import get_user_input
from .session import show_results, prompt_start_session

if TYPE_CHECKING:
    from src.domain.services.math_fact_service import MathFactService


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
    math_fact_service: Optional["MathFactService"] = None,
    user_id: Optional[str] = None,
) -> Tuple[int, int, int, float, List[Tuple[int, int, bool, int, int]]]:
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
    session_attempts: List[Tuple[int, int, bool, int, int]] = (
        []
    )  # Track attempts for SM-2 fact performance

    while generator.has_more_problems():
        problem, correct_answer = generator.get_next_problem()
        progress = generator.get_progress_display()
        print(f"\n📝 Problem {progress}: {problem}")

        # Parse operands for fact tracking
        operands = problem.split(" + ")
        operand1, operand2 = int(operands[0]), int(operands[1])

        problem_start_time = time.time()
        problem_answered = False
        incorrect_attempts_on_problem = 0

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

    end_time = time.time()
    duration = end_time - start_time
    return correct_count, total_attempted, skipped_count, duration, session_attempts


def get_addition_tables_choice(math_fact_service=None, user_id=None) -> int:
    """Get user's choice for addition tables submenu."""
    print("\n📊 Addition Tables Options:")
    print("1. Practice a specific range")

    # Show review option if user is signed in
    if math_fact_service and user_id:
        # Get count of facts due for review
        facts_due = math_fact_service.get_facts_due_for_review(user_id, limit=100)
        due_count = len(facts_due)
        if due_count > 0:
            print(f"2. Review Due Facts ({due_count} facts ready)")
        else:
            print("2. Review Due Facts (none due)")
    else:
        print("2. Review Due Facts (sign in required)")

    print("3. Return to main menu")

    while True:
        try:
            choice = int(get_user_input("Select option", "1"))
            if choice in [1, 2, 3]:
                return choice
            else:
                print("❌ Please enter 1, 2, or 3")
        except ValueError:
            print("❌ Please enter a valid number")


def practice_specific_range(container=None, user=None):
    """Handle practicing a specific addition table range."""
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
    math_fact_service = None
    user_id = None
    if container and user:
        math_fact_service = container.math_fact_svc
        user_id = user.id

    correct, total, skipped, duration, session_attempts = run_addition_table_quiz(
        generator, math_fact_service, user_id
    )

    # Show enhanced results with fact tracking if available
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


def review_due_facts(container=None, user=None):
    """Handle reviewing facts that are due based on SM-2 scheduling."""
    if not container or not user:
        print("❌ You must be signed in to use Review Due Facts.")
        return

    math_fact_service = container.math_fact_svc
    user_id = user.id

    # Get facts due for review
    facts_due = math_fact_service.get_facts_due_for_review(user_id)

    if not facts_due:
        print("\n🎉 No facts are due for review right now!")
        print("Great job staying on top of your practice!")

        # Show next review info if available
        all_facts = math_fact_service.get_all_user_performances(user_id)
        if all_facts:
            # Find the next fact due for review
            next_due = min(
                all_facts, key=lambda f: f.next_review_date or datetime.now(timezone.utc)
            )
            if next_due.next_review_date:
                time_until = next_due.next_review_date - datetime.now(timezone.utc)
                if time_until.days > 0:
                    print(f"⏰ Next review in {time_until.days} day(s)")
                else:
                    hours = time_until.seconds / 3600
                    print(f"⏰ Next review in {hours:.1f} hour(s)")
        return

    # Convert due facts to problems and randomize
    problems = []
    fact_lookup = {}  # Map problem string to fact key

    for fact in facts_due:
        operand1, operand2 = map(int, fact.fact_key.split("+"))
        problem = f"{operand1} + {operand2}"
        answer = operand1 + operand2
        problems.append((problem, answer))
        fact_lookup[problem] = fact.fact_key

    import random

    random.shuffle(problems)

    print(f"\n🎯 Reviewing {len(problems)} facts due for practice")
    print("These facts are scheduled for review based on your learning progress.")
    print("Commands: 'next' (skip), 'stop' (return to menu), 'exit' (quit app)")
    print("=" * 60)

    input("Press Enter when ready to start...")

    start_time = time.time()
    correct_count = 0
    total_attempted = 0
    skipped_count = 0
    session_attempts: List[Tuple[int, int, bool, int, int]] = []

    for i, (problem, correct_answer) in enumerate(problems):
        print(f"\n📝 Problem {i+1}/{len(problems)}: {problem}")

        # Parse operands for fact tracking
        operands = problem.split(" + ")
        operand1, operand2 = int(operands[0]), int(operands[1])

        problem_start_time = time.time()
        problem_answered = False
        incorrect_attempts_on_problem = 0

        while True:
            user_input = input("Your answer: ").strip().lower()

            if user_input == "exit":
                end_time = time.time()
                duration = end_time - start_time
                show_review_results(
                    correct_count,
                    total_attempted,
                    skipped_count,
                    duration,
                    session_attempts,
                    math_fact_service,
                    user_id,
                    len(problems),
                )
                return
            elif user_input == "stop":
                end_time = time.time()
                duration = end_time - start_time
                show_review_results(
                    correct_count,
                    total_attempted,
                    skipped_count,
                    duration,
                    session_attempts,
                    math_fact_service,
                    user_id,
                    len(problems),
                )
                return
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
    show_review_results(
        correct_count,
        total_attempted,
        skipped_count,
        duration,
        session_attempts,
        math_fact_service,
        user_id,
        len(problems),
    )


def show_review_results(
    correct: int,
    total: int,
    skipped: int,
    duration: float,
    session_attempts: List[Tuple[int, int, bool, int, int]],
    math_fact_service,
    user_id: str,
    total_facts: int,
):
    """Show results for review due facts session."""
    print("\n" + "=" * 60)
    print("📊 REVIEW SESSION RESULTS")
    print("=" * 60)

    if total > 0:
        accuracy = (correct / total) * 100
        print(f"✅ Correct: {correct}/{total} ({accuracy:.1f}%)")
    else:
        print("✅ No problems attempted")

    if skipped > 0:
        print(f"⏭️  Skipped: {skipped}")

    print(f"⏱️  Time: {duration:.1f} seconds")

    if total > 0:
        avg_time = duration / total
        print(f"📈 Average time per problem: {avg_time:.1f} seconds")

    print(f"📝 Facts reviewed: {total_facts}")

    # Process session with SM-2 if we have attempts
    if session_attempts and math_fact_service:
        try:
            analysis = math_fact_service.analyze_session_performance(
                user_id, session_attempts
            )
            facts_due_count = analysis.get("facts_due_for_review", 0)

            print(f"\n🎯 Facts still due for review: {facts_due_count}")

            if facts_due_count == 0:
                print("🎉 Excellent! All your facts are up to date!")
            elif facts_due_count < total_facts:
                print(
                    f"💪 Progress made! {total_facts - facts_due_count} facts updated"
                )

        except Exception as e:
            print(f"\n⚠️  Could not process SM-2 updates: {e}")


def addition_tables_mode(container=None, user=None):
    """Handle addition tables workflow with submenu."""
    try:
        print("\n📊 Addition Tables Mode Selected!")

        # Get math fact service for checking due facts
        math_fact_service = None
        user_id = None
        if container and user:
            math_fact_service = container.math_fact_svc
            user_id = user.id

        while True:
            choice = get_addition_tables_choice(math_fact_service, user_id)

            if choice == 1:
                practice_specific_range(container, user)
                break
            elif choice == 2:
                review_due_facts(container, user)
                break
            elif choice == 3:
                return  # Return to main menu

    except Exception as e:
        print(f"❌ Error: {e}")
        print("Returning to main menu...")


def show_results_with_fact_insights(
    correct: int,
    total: int,
    duration: float,
    generator: AdditionTableGenerator,
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

        try:
            # Analyze session performance with SM-2
            analysis = math_fact_service.analyze_session_performance(
                user_id, session_attempts
            )

            if "error" not in analysis:
                # Show session analysis
                facts_practiced = len(analysis.get("facts_practiced", []))
                new_facts = len(analysis.get("new_facts_learned", []))
                print(f"📝 Facts practiced this session: {facts_practiced}")
                if new_facts > 0:
                    print(f"🆕 New facts learned: {new_facts}")

                # Show facts due for review
                facts_due_count = analysis.get("facts_due_for_review", 0)
                if facts_due_count > 0:
                    print(f"\n📅 Facts due for review: {facts_due_count}")
                    print("💡 Use 'Review Due Facts' from the addition tables menu!")

                # Show weak facts that need practice
                weak_facts = math_fact_service.get_weak_facts(
                    user_id, (generator.low, generator.high), 5
                )
                if weak_facts:
                    weak_fact_keys = [f.fact_key for f in weak_facts[:3]]  # Show top 3
                    print(f"\n🎯 FOCUS ON: {', '.join(weak_fact_keys)}")

                # Show SM-2 performance summary
                summary = math_fact_service.get_performance_summary(user_id)
                if summary["total_facts"] > 0:
                    avg_ease = summary.get("average_ease_factor", 2.5)
                    print(
                        f"\n📊 Average difficulty: {avg_ease:.1f}/4.0 (higher = easier)"
                    )

                    # Show interval distribution
                    intervals = summary.get("facts_by_interval", {})
                    if intervals:
                        print("🗓️  Review schedule:")
                        for days in sorted(intervals.keys())[
                            :3
                        ]:  # Show top 3 intervals
                            count = intervals[days]
                            if days == 1:
                                print(f"   • {count} facts: Review daily")
                            elif days <= 7:
                                print(f"   • {count} facts: Review every {days} days")
                            else:
                                print(f"   • {count} facts: Review every {days} days")

        except Exception as e:
            print(f"\n⚠️  Could not load SM-2 insights: {e}")

    elif not math_fact_service:
        # Show message about signing in for enhanced features
        print("\n" + "=" * 60)
        print("🔐 SIGN IN FOR PERSONALIZED INSIGHTS")
        print("=" * 60)
        print("Sign in to track your progress with SM-2 spaced repetition!")
        print("• Adaptive review scheduling based on your performance")
        print("• Get facts due for review at optimal intervals")
        print("• Track learning efficiency with ease factors")
        print("• Personalized difficulty adjustment")
