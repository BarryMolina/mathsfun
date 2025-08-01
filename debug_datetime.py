#!/usr/bin/env python3
"""Debug script to identify timezone comparison issues."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from datetime import datetime, timezone
from src.config.container import Container
from src.domain.models.math_fact_performance import MathFactPerformance

def test_datetime_comparison():
    """Test datetime comparison to identify the exact issue."""
    print("Testing datetime comparison issues...")
    
    # Initialize container with supabase manager
    from src.infrastructure.database.supabase_manager import SupabaseManager
    supabase_manager = SupabaseManager()
    container = Container(supabase_manager)
    
    # Test user ID (the one from the session)
    user_id = "bazzaboy+000@gmail.com"  # This might not be the actual user ID
    
    try:
        # Get math fact service
        math_fact_service = container.math_fact_svc
        
        print("Getting facts due for review...")
        facts_due = math_fact_service.get_facts_due_for_review(user_id, 5)
        print(f"Found {len(facts_due)} facts due")
        
        if facts_due:
            fact = facts_due[0]
            print(f"First fact: {fact.fact_key}")
            print(f"Next review date: {fact.next_review_date} (type: {type(fact.next_review_date)})")
            print(f"Next review date timezone: {fact.next_review_date.tzinfo if fact.next_review_date else 'None'}")
            
            now_naive = datetime.now()
            now_aware = datetime.now(timezone.utc)
            print(f"datetime.now(): {now_naive} (type: {type(now_naive)}, tz: {now_naive.tzinfo})")
            print(f"datetime.now(timezone.utc): {now_aware} (type: {type(now_aware)}, tz: {now_aware.tzinfo})")
            
            # Test the is_due_for_review property
            print("Testing is_due_for_review property...")
            try:
                is_due = fact.is_due_for_review
                print(f"is_due_for_review: {is_due}")
            except Exception as e:
                print(f"ERROR in is_due_for_review: {e}")
        
        # Test get_weak_facts which triggers the error
        print("\nTesting get_weak_facts...")
        try:
            weak_facts = math_fact_service.get_weak_facts(user_id, (1, 2), 3)
            print(f"get_weak_facts succeeded: {len(weak_facts)} facts")
        except Exception as e:
            print(f"ERROR in get_weak_facts: {e}")
    
    except Exception as e:
        print(f"Overall error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_datetime_comparison()