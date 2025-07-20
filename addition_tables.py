#!/usr/bin/env python3
import random
import time
from typing import List, Tuple
from ui import get_user_input
from session import show_results, prompt_start_session


def get_table_range() -> Tuple[int, int]:
    """Get the table range (low and high numbers, 1-100) from user"""
    while True:
        try:
            low_input = get_user_input("Enter low number for addition table (1-100)", "1")
            low = int(low_input)
            if low < 1 or low > 100:
                print("❌ Please enter a number between 1 and 100")
                continue
            
            high_input = get_user_input("Enter high number for addition table (1-100)", "10")
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


def run_addition_table_quiz(generator: AdditionTableGenerator) -> Tuple[int, int, float]:
    """Run the addition table quiz"""
    order_text = "random order" if generator.randomize else "sequential order"
    range_text = f"{generator.low} to {generator.high}" if generator.low != generator.high else str(generator.low)
    print(f"\n🎯 Addition Table for {range_text} ({order_text})")
    print(f"📝 {generator.total_problems} problems to solve")
    print("Commands: 'next' (skip), 'stop' (return to menu), 'exit' (quit app)")
    print("=" * 60)
    
    input("Press Enter when ready to start...")
    
    start_time = time.time()
    correct_count = 0
    total_attempted = 0
    
    while generator.has_more_problems():
        problem, correct_answer = generator.get_next_problem()
        progress = generator.get_progress_display()
        print(f"\n📝 Problem {progress}: {problem}")
        
        while True:
            user_input = input("Your answer: ").strip().lower()
            
            if user_input == "exit":
                end_time = time.time()
                duration = end_time - start_time
                return correct_count, total_attempted, duration
            elif user_input == "stop":
                end_time = time.time()
                duration = end_time - start_time
                return correct_count, total_attempted, duration
            elif user_input == "next":
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
                    print(f"❌ Not quite right. Try again!")
                    print("You can type 'next' to move on to the next problem.")
            
            except ValueError:
                print("❌ Please enter a number, 'next', 'stop', or 'exit'")
    
    end_time = time.time()
    duration = end_time - start_time
    return correct_count, total_attempted, duration


def addition_tables_mode():
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
        
        correct, total, duration = run_addition_table_quiz(generator)
        
        show_results(correct, total, duration, generator)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Returning to main menu...")