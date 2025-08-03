#!/usr/bin/env python3
"""Interactive analytics controller for math fact performance with SM-2 data."""

import re
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any, Tuple, TYPE_CHECKING
from ..cli.ui import get_user_input

if TYPE_CHECKING:
    from src.domain.services.math_fact_service import MathFactService
    from src.domain.models.math_fact_performance import MathFactPerformance


def view_analytics_mode(container=None, user=None) -> None:
    """Main interactive analytics mode with command processing."""
    if not container or not user:
        print("❌ You must be signed in to view analytics.")
        return

    math_fact_service = container.math_fact_svc
    user_id = user.id

    # Get all user performance data
    all_performances = math_fact_service.get_all_user_performances(user_id)

    if not all_performances:
        print("\n📊 Math Fact Performance Analytics")
        print("=" * 60)
        print("No math facts tracked yet!")
        print("Complete some addition problems to see your analytics here.")
        print("\n💡 Try practicing from the Addition Tables menu first.")
        return

    print("\n📊 Math Fact Performance Analytics (SM-2 Spaced Repetition)")
    print("=" * 60)

    # Initialize analytics state
    analytics_state = AnalyticsState(all_performances, math_fact_service, user_id)

    # Display initial overview and table
    display_analytics_overview(analytics_state)
    display_analytics_table(analytics_state)

    # Interactive command loop
    print(
        "\nCommands: sort <field> [asc/desc] | filter <condition> | clear | refresh | help | back"
    )

    while True:
        try:
            command = get_user_input("Enter command", "back").strip().lower()

            if command == "back":
                break
            elif command == "help":
                show_analytics_help()
            elif command == "clear":
                analytics_state.clear_filters_and_sorting()
                display_analytics_table(analytics_state)
            elif command == "refresh":
                analytics_state.refresh_data()
                display_analytics_overview(analytics_state)
                display_analytics_table(analytics_state)
            elif command.startswith("sort "):
                handle_sort_command(command, analytics_state)
                display_analytics_table(analytics_state)
            elif command.startswith("filter "):
                handle_filter_command(command, analytics_state)
                display_analytics_table(analytics_state)
            else:
                print("❌ Unknown command. Type 'help' for available commands.")

        except KeyboardInterrupt:
            print("\n\nReturning to Addition Tables menu...")
            break
        except Exception as e:
            print(f"❌ Error processing command: {e}")


class AnalyticsState:
    """Maintains state for the interactive analytics interface."""

    def __init__(
        self,
        all_performances: List["MathFactPerformance"],
        math_fact_service: "MathFactService",
        user_id: str,
    ):
        self.math_fact_service = math_fact_service
        self.user_id = user_id
        self.original_performances = all_performances
        self.filtered_performances = all_performances.copy()
        self.sort_field: Optional[str] = None
        self.sort_descending = True
        self.active_filters: List[str] = []

    def clear_filters_and_sorting(self):
        """Reset all filters and sorting."""
        self.filtered_performances = self.original_performances.copy()
        self.sort_field = None
        self.sort_descending = True
        self.active_filters = []
        print("✅ Filters and sorting cleared")

    def refresh_data(self):
        """Reload data from the database."""
        self.original_performances = self.math_fact_service.get_all_user_performances(
            self.user_id
        )
        self.filtered_performances = self.original_performances.copy()
        self.active_filters = []
        print("✅ Data refreshed")

    def apply_sort(self, field: str, descending: bool = True):
        """Apply sorting to the filtered performances."""
        self.sort_field = field
        self.sort_descending = descending

        try:
            if field == "fact":
                self.filtered_performances.sort(
                    key=lambda p: p.fact_key, reverse=descending
                )
            elif field == "attempts":
                self.filtered_performances.sort(
                    key=lambda p: p.total_attempts, reverse=descending
                )
            elif field == "accuracy":
                self.filtered_performances.sort(
                    key=lambda p: p.accuracy, reverse=descending
                )
            elif field == "time":
                self.filtered_performances.sort(
                    key=lambda p: p.average_response_time_seconds, reverse=descending
                )
            elif field == "ease":
                self.filtered_performances.sort(
                    key=lambda p: float(p.easiness_factor), reverse=descending
                )
            elif field == "interval":
                self.filtered_performances.sort(
                    key=lambda p: p.interval_days, reverse=descending
                )
            elif field == "repetitions":
                self.filtered_performances.sort(
                    key=lambda p: p.repetition_number, reverse=descending
                )
            elif field == "grade":
                self.filtered_performances.sort(
                    key=lambda p: p.last_sm2_grade or -1, reverse=descending
                )
            elif field == "fastest":
                self.filtered_performances.sort(
                    key=lambda p: p.fastest_response_ms or 99999, reverse=descending
                )
            elif field == "slowest":
                self.filtered_performances.sort(
                    key=lambda p: p.slowest_response_ms or 0, reverse=descending
                )
            else:
                print(f"❌ Unknown sort field: {field}")
                return False

            direction = "descending" if descending else "ascending"
            print(f"✅ Sorted by {field} ({direction})")
            return True
        except Exception as e:
            print(f"❌ Error sorting by {field}: {e}")
            return False

    def apply_filter(self, condition: str):
        """Apply a filter condition to the performances."""
        try:
            # Parse different filter types
            if condition == "due":
                filtered = [
                    p for p in self.filtered_performances if p.is_due_for_review
                ]
                filter_desc = "facts due for review"
            elif condition == "overdue":
                now = datetime.now(timezone.utc)
                filtered = [
                    p
                    for p in self.filtered_performances
                    if p.next_review_date and p.next_review_date < now
                ]
                filter_desc = "overdue facts"
            elif condition == "easy":
                filtered = [
                    p
                    for p in self.filtered_performances
                    if float(p.easiness_factor) > 2.5
                ]
                filter_desc = "easy facts (ease factor > 2.5)"
            elif condition == "difficult":
                filtered = [
                    p
                    for p in self.filtered_performances
                    if float(p.easiness_factor) < 2.0
                ]
                filter_desc = "difficult facts (ease factor < 2.0)"
            elif condition == "daily":
                filtered = [
                    p for p in self.filtered_performances if p.interval_days == 1
                ]
                filter_desc = "facts on daily review"
            elif condition == "new":
                filtered = [
                    p for p in self.filtered_performances if p.repetition_number < 3
                ]
                filter_desc = "new facts (repetitions < 3)"
            elif condition == "established":
                filtered = [
                    p for p in self.filtered_performances if p.repetition_number >= 6
                ]
                filter_desc = "established facts (repetitions ≥ 6)"
            else:
                # Parse numeric filters like "accuracy <80" or "ease >2.5"
                result = self._parse_numeric_filter(condition)
                if result[0] is None or result[1] is None:
                    print(f"❌ Unknown filter condition: {condition}")
                    return False
                
                filtered, filter_desc = result[0], result[1]
                assert filtered is not None and filter_desc is not None

            self.filtered_performances = filtered
            self.active_filters.append(filter_desc)
            print(f"✅ Applied filter: {filter_desc} ({len(filtered)} facts shown)")
            return True

        except Exception as e:
            print(f"❌ Error applying filter '{condition}': {e}")
            return False

    def _parse_numeric_filter(
        self, condition: str
    ) -> Tuple[Optional[List["MathFactPerformance"]], Optional[str]]:
        """Parse numeric filter conditions like 'accuracy <80' or 'ease >2.5'."""
        # Pattern for field operator value
        match = re.match(r"(\w+)\s*([<>=]+)\s*([0-9.]+)", condition)
        if not match:
            return None, None

        field, operator, value_str = match.groups()
        try:
            value = float(value_str)
        except ValueError:
            return None, None

        filtered = []

        for p in self.filtered_performances:
            field_value = None

            if field == "accuracy":
                field_value = p.accuracy
            elif field == "attempts":
                field_value = p.total_attempts
            elif field == "time":
                field_value = p.average_response_time_seconds
            elif field == "ease":
                field_value = float(p.easiness_factor)
            elif field == "interval":
                field_value = p.interval_days
            elif field == "repetitions":
                field_value = p.repetition_number
            elif field == "grade":
                field_value = p.last_sm2_grade
            else:
                return None, None

            # Apply operator (skip null values for grade field)
            if field_value is None and field == "grade":
                continue
            elif operator == "<" and field_value is not None and field_value < value:
                filtered.append(p)
            elif operator == "<=" and field_value is not None and field_value <= value:
                filtered.append(p)
            elif operator == ">" and field_value is not None and field_value > value:
                filtered.append(p)
            elif operator == ">=" and field_value is not None and field_value >= value:
                filtered.append(p)
            elif operator == "=" and field_value is not None and field_value == value:
                filtered.append(p)

        filter_desc = f"{field} {operator} {value}"
        return filtered, filter_desc


def display_analytics_overview(state: AnalyticsState) -> None:
    """Display overview statistics."""
    performances = state.filtered_performances

    if not performances:
        print("No facts match the current filters.")
        return

    total_facts = len(performances)
    facts_due = sum(1 for p in performances if p.is_due_for_review)
    avg_ease = sum(float(p.easiness_factor) for p in performances) / total_facts
    total_accuracy = sum(p.accuracy for p in performances) / total_facts

    # Get overall summary for additional context
    summary = state.math_fact_service.get_performance_summary(state.user_id)

    print(
        f"Total facts tracked: {total_facts} | Due for review: {facts_due} | Average ease factor: {avg_ease:.1f} | Overall accuracy: {total_accuracy:.1f}%"
    )

    if state.active_filters:
        print(f"Active filters: {', '.join(state.active_filters)}")

    print()


def display_analytics_table(state: AnalyticsState) -> None:
    """Display the comprehensive analytics table."""
    performances = state.filtered_performances

    if not performances:
        print("No facts to display.")
        return

    # Table header
    print(
        "Fact | Attempts | Accuracy | Avg Time | Ease Factor | Interval | Next Review | Repetitions | Last Grade | Fastest | Slowest"
    )
    print("-" * 110)

    # Display each fact
    for p in performances:
        fact = p.fact_key.ljust(4)
        attempts = str(p.total_attempts).rjust(8)
        accuracy = f"{p.accuracy:.1f}%".rjust(8)
        avg_time = f"{p.average_response_time_seconds:.1f}s".rjust(8)
        ease_factor = f"{float(p.easiness_factor):.1f}".rjust(11)

        # Format interval
        if p.interval_days == 1:
            interval = "daily".rjust(8)
        elif p.interval_days < 7:
            interval = f"{p.interval_days}d".rjust(8)
        else:
            interval = f"{p.interval_days}d".rjust(8)

        # Format next review
        if p.next_review_date:
            now = datetime.now(timezone.utc)
            diff = p.next_review_date - now
            if diff.days < 0:
                next_review = "Overdue".ljust(11)
            elif diff.days == 0:
                next_review = "Today".ljust(11)
            elif diff.days == 1:
                next_review = "Tomorrow".ljust(11)
            else:
                next_review = f"In {diff.days}d".ljust(11)
        else:
            next_review = "Unknown".ljust(11)

        repetitions = str(p.repetition_number).rjust(11)

        # Format last SM2 grade
        last_grade = (
            str(p.last_sm2_grade).rjust(10)
            if p.last_sm2_grade is not None
            else "N/A".rjust(10)
        )

        # Format response times
        fastest = (
            f"{(p.fastest_response_ms or 0) / 1000:.1f}s".rjust(7)
            if p.fastest_response_ms
            else "N/A".rjust(7)
        )
        slowest = (
            f"{(p.slowest_response_ms or 0) / 1000:.1f}s".rjust(7)
            if p.slowest_response_ms
            else "N/A".rjust(7)
        )

        print(
            f"{fact} | {attempts} | {accuracy} | {avg_time} | {ease_factor} | {interval} | {next_review} | {repetitions} | {last_grade} | {fastest} | {slowest}"
        )


def handle_sort_command(command: str, state: AnalyticsState) -> None:
    """Handle sort commands like 'sort accuracy desc'."""
    parts = command.split()
    if len(parts) < 2:
        print("❌ Usage: sort <field> [asc/desc]")
        return

    field = parts[1]
    direction = parts[2] if len(parts) > 2 else "desc"
    descending = direction.lower() in ["desc", "descending"]

    state.apply_sort(field, descending)


def handle_filter_command(command: str, state: AnalyticsState) -> None:
    """Handle filter commands like 'filter accuracy <80'."""
    # Remove 'filter ' prefix and get the condition
    condition = command[7:].strip()
    if not condition:
        print("❌ Usage: filter <condition>")
        return

    state.apply_filter(condition)


def show_analytics_help() -> None:
    """Show help for analytics commands."""
    print("\n📋 Analytics Commands Help")
    print("=" * 50)
    print("\n🔍 Sorting:")
    print("  sort <field> [asc/desc]")
    print(
        "  Fields: fact, attempts, accuracy, time, ease, interval, repetitions, grade, fastest, slowest"
    )
    print("  Examples: 'sort accuracy desc', 'sort grade desc', 'sort time asc'")

    print("\n🎯 Filtering:")
    print("  Basic filters:")
    print("    filter due          - Facts due for review today")
    print("    filter overdue      - Overdue facts")
    print("    filter easy         - Facts with ease factor > 2.5")
    print("    filter difficult    - Facts with ease factor < 2.0")
    print("    filter daily        - Facts on daily review (interval = 1)")
    print("    filter new          - Facts with repetitions < 3")
    print("    filter established  - Facts with repetitions ≥ 6")

    print("\n  Numeric filters:")
    print("    filter <field> <operator> <value>")
    print(
        "    Examples: 'filter accuracy <80', 'filter ease >2.5', 'filter attempts >=10'"
    )

    print("\n🛠️  Utility:")
    print("  clear    - Remove all filters and sorting")
    print("  refresh  - Reload data from database")
    print("  help     - Show this help")
    print("  back     - Return to Addition Tables menu")
    print()
