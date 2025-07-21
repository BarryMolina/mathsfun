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


def show_results(correct: int, total: int, duration: float, generator, container=None, user_id=None):
    """Display quiz results with timing and optional historical data"""
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

    # Show historical progress if available
    if container and user_id:
        try:
            progress = container.quiz_svc.get_user_progress(user_id)
            if progress.total_sessions > 1:  # Only show if there's historical data
                print("\n📊 Your Progress Summary:")
                print(f"📈 Total sessions completed: {progress.total_sessions}")
                print(f"🎯 Overall accuracy: {progress.overall_accuracy:.1f}%")
                print(f"🏆 Best session accuracy: {progress.best_accuracy:.1f}%")
                print(f"⚡ Average session time: {format_duration(progress.average_session_time)}")
                
                if progress.recent_sessions:
                    print(f"\n📋 Recent Sessions:")
                    for i, session in enumerate(progress.recent_sessions[:3], 1):
                        session_date = session.start_time.strftime("%m/%d %H:%M")
                        print(f"   {i}. {session_date} - {session.accuracy:.1f}% accuracy, {session.total_problems} problems")
        except Exception as e:
            # Don't fail the results display if progress fetch fails
            print(f"📊 Progress data temporarily unavailable")

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