#!/usr/bin/env python3
import random
import time
from typing import List, Tuple, Optional

DIFFICULTY_DESCRIPTIONS = {
    1: "Two single-digit numbers",
    2: "Two two-digit numbers, no carrying",
    3: "Two two-digit numbers with carrying", 
    4: "Two three-digit numbers, no carrying",
    5: "Two three-digit numbers with carrying"
}

def print_welcome():
    """Display a fun welcome message for MathsFun"""
    print("\n" + "="*50)
    print("🎯 Welcome to MathsFun! 🎯")
    print("Let's make math practice fun and interactive!")
    print("="*50 + "\n")

def print_main_menu():
    """Display the main menu options"""
    print("📚 Main Menu:")
    print("1. Addition")
    print("\nType 'exit' to quit the application")
    print("-" * 30)

def get_user_input(prompt: str, default: Optional[str] = None) -> str:
    """Get user input with optional default value"""
    if default:
        user_input = input(f"{prompt} (default: {default}): ").strip()
        return user_input if user_input else default
    return input(f"{prompt}: ").strip()

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
    """Get number of problems from user (max 10)"""
    while True:
        try:
            num = int(get_user_input("Number of problems", "5"))
            if num < 1:
                print("❌ Please enter at least 1 problem")
                continue
            if num > 10:
                print("❌ Maximum 10 problems allowed")
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
        
        if (ones1 + ones2 <= 9 and 
            tens1 + tens2 <= 9 and 
            hundreds1 + hundreds2 <= 9):
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

def distribute_problems(low_difficulty: int, high_difficulty: int, num_problems: int) -> List[int]:
    """Distribute problems evenly across difficulty levels"""
    difficulty_range = list(range(low_difficulty, high_difficulty + 1))
    num_levels = len(difficulty_range)
    
    # Base problems per level
    base_problems = num_problems // num_levels
    extra_problems = num_problems % num_levels
    
    distribution = []
    for i, difficulty in enumerate(difficulty_range):
        # Add extra problems to first few levels if needed
        problems_for_level = base_problems + (1 if i < extra_problems else 0)
        distribution.extend([difficulty] * problems_for_level)
    
    # Shuffle to randomize order
    random.shuffle(distribution)
    return distribution

def generate_problems(low_difficulty: int, high_difficulty: int, num_problems: int) -> Tuple[List[str], List[int]]:
    """Generate math problems using random number generation"""
    print("\n🎲 Generating your math problems...")
    
    # Get distribution of difficulties
    difficulty_distribution = distribute_problems(low_difficulty, high_difficulty, num_problems)
    
    problems = []
    answers = []
    
    for difficulty in difficulty_distribution:
        problem, answer = generate_problem_by_difficulty(difficulty)
        problems.append(problem)
        answers.append(answer)
    
    return problems, answers

def prompt_start_session(num_problems: int):
    """Prompt user to start the quiz session"""
    print(f"\n✅ {num_problems} problems ready!")
    print("Press Enter when you're ready to start the timer and begin...")
    input()

def run_quiz(problems: List[str], answers: List[int]) -> Tuple[int, int, float]:
    """Run the interactive math quiz with timing"""
    prompt_start_session(len(problems))
    
    print(f"\n🎯 Timer started! You have {len(problems)} problems to solve.")
    print("Commands: 'next' (skip), 'stop' (return to menu), 'exit' (quit app)")
    print("=" * 50)
    
    start_time = time.time()
    correct_count = 0
    total_attempted = 0
    
    for i, (problem, correct_answer) in enumerate(zip(problems, answers), 1):
        print(f"\n📝 Problem {i}/{len(problems)}: {problem}")
        
        while True:
            user_input = input("Your answer: ").strip().lower()
            
            if user_input == 'exit':
                end_time = time.time()
                duration = end_time - start_time
                return correct_count, total_attempted, duration
            elif user_input == 'stop':
                end_time = time.time()
                duration = end_time - start_time
                return correct_count, total_attempted, duration
            elif user_input == 'next':
                print(f"⏭️  Skipped! The answer was {correct_answer}")
                break
            
            try:
                user_answer = int(user_input)
                total_attempted += 1
                
                if user_answer == correct_answer:
                    print("✅ Correct! Great job!")
                    correct_count += 1
                    break
                else:
                    print(f"❌ Not quite right. Try again! (The answer was {correct_answer})")
                    print("You can type 'next' to move on to the next problem.")
                    
            except ValueError:
                print("❌ Please enter a number, 'next', 'stop', or 'exit'")
    
    end_time = time.time()
    duration = end_time - start_time
    return correct_count, total_attempted, duration

def format_duration(duration: float) -> str:
    """Format duration in seconds to a readable string"""
    if duration < 60:
        return f"{duration:.1f} seconds"
    elif duration < 3600:
        minutes = int(duration // 60)
        seconds = duration % 60
        return f"{minutes}m {seconds:.1f}s"
    else:
        hours = int(duration // 3600)
        minutes = int((duration % 3600) // 60)
        seconds = duration % 60
        return f"{hours}h {minutes}m {seconds:.1f}s"

def show_results(correct: int, total: int, duration: float):
    """Display quiz results with timing"""
    print("\n" + "="*50)
    print("🎉 Quiz Complete! 🎉")
    print(f"✅ Correct answers: {correct}")
    print(f"📊 Total attempted: {total}")
    print(f"⏱️  Time taken: {format_duration(duration)}")
    
    if total > 0:
        accuracy = (correct / total) * 100
        print(f"🎯 Accuracy: {accuracy:.1f}%")
        
        # Calculate average time per problem
        avg_time = duration / total
        print(f"📈 Average time per problem: {format_duration(avg_time)}")
        
        if accuracy >= 90:
            print("🌟 Outstanding! You're a math superstar!")
        elif accuracy >= 80:
            print("🎊 Excellent work! Keep it up!")
        elif accuracy >= 70:
            print("👍 Good job! Practice makes perfect!")
        else:
            print("💪 Keep practicing! You'll get better!")
    else:
        print("🤔 No problems attempted this time.")
    
    print("="*50 + "\n")

def addition_mode():
    """Handle addition problems workflow"""
    try:
        print("\n🔢 Addition Mode Selected!")
        
        # Get user preferences
        low, high = get_difficulty_range()
        num_problems = get_num_problems()
        
        print(f"\n📋 Settings:")
        print(f"   Difficulty: {low} to {high}")
        print(f"   Problems: {num_problems}")
        
        # Generate problems
        problems, answers = generate_problems(low, high, num_problems)
        
        # Run the quiz
        correct, total, duration = run_quiz(problems, answers)
        
        # Show results
        show_results(correct, total, duration)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Returning to main menu...")

def main():
    """Main application loop"""
    print_welcome()
    
    while True:
        print_main_menu()
        choice = input("Select an option: ").strip().lower()
        
        if choice == 'exit':
            print("\n👋 Thanks for using MathsFun! Keep practicing!")
            break
        elif choice == '1':
            result = addition_mode()
            if result == 'exit':
                break
        else:
            print("❌ Invalid option. Please try again.\n")

if __name__ == "__main__":
    main()