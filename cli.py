#!/usr/bin/env python3
import os
import re
import time
from typing import List, Tuple, Optional
from dotenv import load_dotenv
from chatter import chatter
from jinja_helper import process_template

load_dotenv()

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

def generate_problems(low_difficulty: int, high_difficulty: int, num_problems: int) -> Tuple[List[str], List[int]]:
    """Generate math problems using AI and parse the response"""
    print("\n🤖 Generating your math problems...")
    
    api_key = os.getenv("OPENAI_KEY")
    if not api_key:
        raise ValueError("No API key found. Please set your OPENAI_KEY in the .env file.")
    
    chat_fn = chatter(api_key)
    
    data = {
        "LOW_DIFFICULTY": low_difficulty,
        "HIGH_DIFFICULTY": high_difficulty,
        "NUM_PROBLEMS": num_problems,
    }
    
    prompt = process_template("prompts/addition.jinja", data)
    response = chat_fn(prompt)
    
    # Parse problems and answers from response
    problems = parse_problems(response)
    answers = parse_answers(response)
    
    if len(problems) != len(answers):
        raise ValueError("Mismatch between number of problems and answers")
    
    return problems, answers

def parse_problems(response: str) -> List[str]:
    """Extract problems from AI response"""
    problems_match = re.search(r'<problems>(.*?)</problems>', response, re.DOTALL)
    if not problems_match:
        raise ValueError("Could not find problems in response")
    
    problems_text = problems_match.group(1).strip()
    problems = []
    
    for line in problems_text.split('\n'):
        line = line.strip()
        if line and '. ' in line:
            # Extract just the math expression (e.g., "4 + 5")
            problem = line.split('. ', 1)[1].strip()
            problems.append(problem)
    
    return problems

def parse_answers(response: str) -> List[int]:
    """Extract answers from AI response"""
    answers_match = re.search(r'<answers>(.*?)</answers>', response, re.DOTALL)
    if not answers_match:
        raise ValueError("Could not find answers in response")
    
    answers_text = answers_match.group(1).strip()
    answers = []
    
    for line in answers_text.split('\n'):
        line = line.strip()
        if line and '. ' in line:
            # Extract the number after the period
            answer_str = line.split('. ', 1)[1].strip()
            try:
                answers.append(int(answer_str))
            except ValueError:
                raise ValueError(f"Invalid answer format: {answer_str}")
    
    return answers

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