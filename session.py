#!/usr/bin/env python3


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


def show_results(correct: int, total: int, duration: float, generator):
    """Display quiz results with timing"""
    print("\n" + "=" * 60)

    if generator.is_unlimited:
        print("🎉 Session Complete! 🎉")
        completion_text = "Session ended by user"
    else:
        if generator.get_total_generated() >= generator.num_problems:
            print("🎉 Quiz Complete! 🎉")
            completion_text = "All problems completed"
        else:
            print("🎉 Session Complete! 🎉")
            completion_text = "Session ended by user"

    print(f"📊 Problems presented: {generator.get_total_generated()}")
    print(f"✅ Correct answers: {correct}")
    print(f"📝 Total attempted: {total}")
    print(f"⏭️  Skipped: {generator.get_total_generated() - total}")
    print(f"⏱️  Time taken: {format_duration(duration)}")
    print(f"ℹ️  {completion_text}")

    if total > 0:
        accuracy = (correct / total) * 100
        print(f"🎯 Accuracy: {accuracy:.1f}%")

        # Calculate average time per problem attempted
        avg_time = duration / total
        print(f"📈 Average time per attempted problem: {format_duration(avg_time)}")

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

    print("=" * 60 + "\n")


def prompt_start_session(generator):
    """Prompt user to start the quiz session"""
    if generator.is_unlimited:
        print(f"\n✅ Ready to start unlimited session!")
        print("Solve problems until you're ready to stop.")
    else:
        print(f"\n✅ Ready to start! {generator.num_problems} problems prepared.")
    print("Press Enter when you're ready to start the timer and begin...")
    input()