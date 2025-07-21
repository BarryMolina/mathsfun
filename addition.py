#!/usr/bin/env python3
import random
import time
from typing import Tuple, Optional
from ui import get_user_input
from session import show_results, prompt_start_session

DIFFICULTY_DESCRIPTIONS = {
    1: "Two single-digit numbers",
    2: "Two two-digit numbers, no carrying",
    3: "Two two-digit numbers with carrying",
    4: "Two three-digit numbers, no carrying",
    5: "Two three-digit numbers with carrying",
}


def display_difficulty_options():
    """Display difficulty level options with descriptions"""
    print("\n🎚️  Difficulty Levels:")
    for level, description in DIFFICULTY_DESCRIPTIONS.items():
        print(f"{level}. {description}")
    print()


def get_difficulty_range() -> Tuple[int, int]:
    """Get low and high difficulty levels from user"""
    display_difficulty_options()

    while True:
        try:
            low = int(get_user_input("Enter lowest difficulty level", "1"))
            if low not in range(1, 6):
                print("❌ Please enter a number between 1 and 5")
                continue
            break
        except ValueError:
            print("❌ Please enter a valid number")

    while True:
        try:
            high = int(get_user_input("Enter highest difficulty level", "5"))
            if high not in range(1, 6):
                print("❌ Please enter a number between 1 and 5")
                continue
            if high < low:
                print("❌ High difficulty must be >= low difficulty")
                continue
            break
        except ValueError:
            print("❌ Please enter a valid number")

    return low, high


def get_num_problems() -> int:
    """Get number of problems from user (0 = unlimited)"""
    while True:
        try:
            user_input = get_user_input("Number of problems (0 for unlimited)", "0")
            num = int(user_input)
            if num < 0:
                print("❌ Please enter 0 for unlimited or a positive number")
                continue
            return num
        except ValueError:
            print("❌ Please enter a valid number")


def generate_single_digit_numbers() -> Tuple[int, int]:
    """Generate two single-digit numbers (0-9)"""
    return random.randint(0, 9), random.randint(0, 9)


def generate_two_digit_no_carrying() -> Tuple[int, int]:
    """Generate two two-digit numbers with no carrying required"""
    # Ensure ones digits sum <= 9 and tens digits sum <= 9
    while True:
        num1 = random.randint(10, 99)
        num2 = random.randint(10, 99)

        ones1, tens1 = num1 % 10, num1 // 10
        ones2, tens2 = num2 % 10, num2 // 10

        if ones1 + ones2 <= 9 and tens1 + tens2 <= 9:
            return num1, num2


def generate_two_digit_with_carrying() -> Tuple[int, int]:
    """Generate two two-digit numbers with carrying required"""
    # Ensure ones digits sum > 9
    while True:
        num1 = random.randint(10, 99)
        num2 = random.randint(10, 99)

        ones1, ones2 = num1 % 10, num2 % 10

        if ones1 + ones2 > 9:
            return num1, num2


def generate_three_digit_no_carrying() -> Tuple[int, int]:
    """Generate two three-digit numbers with no carrying required"""
    # Ensure all digit pairs sum <= 9
    while True:
        num1 = random.randint(100, 999)
        num2 = random.randint(100, 999)

        ones1, tens1, hundreds1 = num1 % 10, (num1 // 10) % 10, num1 // 100
        ones2, tens2, hundreds2 = num2 % 10, (num2 // 10) % 10, num2 // 100

        if ones1 + ones2 <= 9 and tens1 + tens2 <= 9 and hundreds1 + hundreds2 <= 9:
            return num1, num2


def generate_three_digit_with_carrying() -> Tuple[int, int]:
    """Generate two three-digit numbers with carrying required"""
    # Ensure at least ones digits sum > 9
    while True:
        num1 = random.randint(100, 999)
        num2 = random.randint(100, 999)

        ones1, ones2 = num1 % 10, num2 % 10

        if ones1 + ones2 > 9:
            return num1, num2


def generate_problem_by_difficulty(difficulty: int) -> Tuple[str, int]:
    """Generate a single math problem based on difficulty level"""
    if difficulty == 1:
        num1, num2 = generate_single_digit_numbers()
    elif difficulty == 2:
        num1, num2 = generate_two_digit_no_carrying()
    elif difficulty == 3:
        num1, num2 = generate_two_digit_with_carrying()
    elif difficulty == 4:
        num1, num2 = generate_three_digit_no_carrying()
    elif difficulty == 5:
        num1, num2 = generate_three_digit_with_carrying()
    else:
        raise ValueError(f"Invalid difficulty level: {difficulty}")

    problem = f"{num1} + {num2}"
    answer = num1 + num2
    return problem, answer


class ProblemGenerator:
    """Generates problems on-demand with random difficulty selection"""

    def __init__(
        self, low_difficulty: int, high_difficulty: int, num_problems: int = 0
    ):
        self.low_difficulty = low_difficulty
        self.high_difficulty = high_difficulty
        self.difficulty_range = list(range(low_difficulty, high_difficulty + 1))
        self.num_problems = num_problems  # 0 means unlimited
        self.problems_generated = 0
        self.is_unlimited = num_problems == 0

    def get_next_problem(self) -> Tuple[str, int]:
        """Generate a random problem within the difficulty range"""
        # Randomly select a difficulty level from the range
        difficulty = random.choice(self.difficulty_range)
        problem, answer = generate_problem_by_difficulty(difficulty)
        self.problems_generated += 1

        return problem, answer

    def has_more_problems(self) -> bool:
        """Check if there are more problems available"""
        if self.is_unlimited:
            return True
        return self.problems_generated < self.num_problems

    def get_total_generated(self) -> int:
        """Get the total number of problems generated so far"""
        return self.problems_generated

    def get_progress_display(self) -> str:
        """Get a string showing current progress"""
        if self.is_unlimited:
            return f"#{self.problems_generated}"
        else:
            return f"{self.problems_generated}/{self.num_problems}"


def run_addition_quiz(generator: ProblemGenerator, container=None, user_id: Optional[str] = None) -> Tuple[int, int, float]:
    """Run the interactive addition quiz with problem generation"""
    prompt_start_session(generator)

    # Start a quiz session if container and user_id are provided
    quiz_session = None
    if container and user_id:
        quiz_session = container.quiz_svc.start_quiz_session(
            user_id, 
            "addition", 
            generator.high_difficulty
        )

    if generator.is_unlimited:
        print(f"\n🎯 Timer started! Solve problems until you're ready to stop.")
    else:
        print(
            f"\n🎯 Timer started! You have {generator.num_problems} problems to solve."
        )
    print("Commands: 'next' (skip), 'stop' (return to menu), 'exit' (quit app)")
    print("=" * 60)

    start_time = time.time()
    correct_count = 0
    total_attempted = 0

    while generator.has_more_problems():
        # Generate problem on-demand
        problem, correct_answer = generator.get_next_problem()
        progress = generator.get_progress_display()
        print(f"\n📝 Problem {progress}: {problem}")

        problem_start_time = time.time()
        attempts_on_problem = 0

        while True:
            user_input = input("Your answer: ").strip().lower()

            if user_input == "exit":
                # Complete session if active
                if quiz_session and container:
                    container.quiz_svc.complete_session(quiz_session.id)
                end_time = time.time()
                duration = end_time - start_time
                return correct_count, total_attempted, duration
            elif user_input == "stop":
                # Complete session if active
                if quiz_session and container:
                    container.quiz_svc.complete_session(quiz_session.id)
                end_time = time.time()
                duration = end_time - start_time
                return correct_count, total_attempted, duration
            elif user_input == "next":
                # Record skipped attempt if first attempt on this problem
                if attempts_on_problem == 0 and quiz_session and container:
                    response_time_ms = int((time.time() - problem_start_time) * 1000)
                    container.quiz_svc.record_answer(
                        quiz_session.id, problem, None, correct_answer, response_time_ms
                    )
                print(f"⏭️  Skipped! The answer was {correct_answer}")
                break

            try:
                user_answer = int(user_input)
                attempts_on_problem += 1
                total_attempted += 1
                response_time_ms = int((time.time() - problem_start_time) * 1000)

                # Record the attempt if session is active
                if quiz_session and container:
                    container.quiz_svc.record_answer(
                        quiz_session.id, problem, user_answer, correct_answer, response_time_ms
                    )

                if user_answer == correct_answer:
                    print("✅ Correct! Great job!")
                    correct_count += 1
                    break
                else:
                    print(f"❌ Not quite right. Try again!")
                    print("You can type 'next' to move on to the next problem.")

            except ValueError:
                print("❌ Please enter a number, 'next', 'stop', or 'exit'")

    # If we reach here, all problems in limited mode are completed
    # Complete session if active
    if quiz_session and container:
        container.quiz_svc.complete_session(quiz_session.id)
    
    end_time = time.time()
    duration = end_time - start_time
    return correct_count, total_attempted, duration


def addition_mode(container=None, user_id: Optional[str] = None):
    """Handle addition problems workflow"""
    try:
        print("\n🔢 Addition Mode Selected!")

        # Get user preferences
        low, high = get_difficulty_range()
        num_problems = get_num_problems()

        print(f"\n📋 Settings:")
        print(f"   Difficulty: {low} to {high}")
        if num_problems == 0:
            print(f"   Mode: Unlimited (stop when ready)")
        else:
            print(f"   Problems: {num_problems}")

        # Create problem generator
        generator = ProblemGenerator(low, high, num_problems)

        # Run the quiz
        correct, total, duration = run_addition_quiz(generator, container, user_id)

        # Show results
        show_results(correct, total, duration, generator, container, user_id)

    except Exception as e:
        print(f"❌ Error: {e}")
        print("Returning to main menu...")