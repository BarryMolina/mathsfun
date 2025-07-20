#!/usr/bin/env python3
import random
import time
from typing import List, Tuple
from ui import get_user_input
from session import show_results, prompt_start_session


def get_table_number() -> int:
    """Get the table number (1-100) from user"""
    while True:
        try:
            user_input = get_user_input("Enter number for addition table (1-100)", "10")
            num = int(user_input)
            if num < 1 or num > 100:
                print("❌ Please enter a number between 1 and 100")
                continue
            return num
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


def generate_addition_table_problems(n: int) -> List[Tuple[str, int]]:
    """Generate all problems for addition table up to n"""
    problems = []
    for i in range(1, n + 1):
        for j in range(1, n + 1):
            problem = f"{i} + {j}"
            answer = i + j
            problems.append((problem, answer))
    return problems


class AdditionTableGenerator:
    """Manages addition table problems for quiz session"""
    
    def __init__(self, n: int, randomize: bool):
        self.n = n
        self.randomize = randomize
        self.problems = generate_addition_table_problems(n)
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
    print(f"\n🎯 Addition Table for {generator.n} ({order_text})")
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
        
        table_number = get_table_number()
        randomize = get_order_preference()
        
        print(f"\n📋 Settings:")
        print(f"   Table: Addition up to {table_number}")
        print(f"   Order: {'Random' if randomize else 'Sequential'}")
        print(f"   Total problems: {table_number * table_number}")
        
        generator = AdditionTableGenerator(table_number, randomize)
        
        correct, total, duration = run_addition_table_quiz(generator)
        
        show_results(correct, total, duration, generator)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Returning to main menu...")