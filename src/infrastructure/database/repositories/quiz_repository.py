"""Quiz repository for MathsFun application."""

from typing import List, Optional
from datetime import datetime
from .base import BaseRepository
from src.domain.models.quiz_session import QuizSession, SessionStatus
from src.domain.models.problem_attempt import ProblemAttempt


class QuizRepository(BaseRepository):
    """Repository for quiz-related database operations."""
    
    def create_session(self, session: QuizSession) -> Optional[QuizSession]:
        """Create a new quiz session."""
        try:
            session_data = session.to_dict()
            session_data.pop('id', None)  # Let database generate ID
            
            response = self.client.table("quiz_sessions").insert(session_data).execute()
            data = self._handle_single_response(response)
            return QuizSession.from_dict(data) if data else None
        except Exception as e:
            print(f"Error creating quiz session: {e}")
            return None
    
    def get_session(self, session_id: str) -> Optional[QuizSession]:
        """Get quiz session by ID."""
        try:
            response = self.client.table("quiz_sessions").select("*").eq("id", session_id).execute()
            data = self._handle_single_response(response)
            return QuizSession.from_dict(data) if data else None
        except Exception as e:
            print(f"Error fetching quiz session: {e}")
            return None
    
    def update_session(self, session: QuizSession) -> Optional[QuizSession]:
        """Update existing quiz session."""
        try:
            response = self.client.table("quiz_sessions").update(session.to_dict()).eq("id", session.id).execute()
            data = self._handle_single_response(response)
            return QuizSession.from_dict(data) if data else None
        except Exception as e:
            print(f"Error updating quiz session: {e}")
            return None
    
    def complete_session(self, session_id: str) -> Optional[QuizSession]:
        """Mark session as completed with end time."""
        try:
            response = self.client.table("quiz_sessions").update({
                "status": SessionStatus.COMPLETED.value,
                "end_time": datetime.now().isoformat()
            }).eq("id", session_id).execute()
            data = self._handle_single_response(response)
            return QuizSession.from_dict(data) if data else None
        except Exception as e:
            print(f"Error completing quiz session: {e}")
            return None
    
    def get_user_sessions(self, user_id: str, limit: int = 50, status: Optional[SessionStatus] = None) -> List[QuizSession]:
        """Get quiz sessions for a user."""
        try:
            query = self.client.table("quiz_sessions").select("*").eq("user_id", user_id)
            
            if status:
                query = query.eq("status", status.value)
            
            response = query.order("start_time", desc=True).limit(limit).execute()
            data = self._handle_response(response)
            
            if data and isinstance(data, list):
                return [QuizSession.from_dict(session) for session in data]
            return []
        except Exception as e:
            print(f"Error fetching user sessions: {e}")
            return []
    
    def save_attempt(self, attempt: ProblemAttempt) -> Optional[ProblemAttempt]:
        """Save a problem attempt."""
        try:
            attempt_data = attempt.to_dict()
            attempt_data.pop('id', None)  # Let database generate ID
            
            response = self.client.table("problem_attempts").insert(attempt_data).execute()
            data = self._handle_single_response(response)
            return ProblemAttempt.from_dict(data) if data else None
        except Exception as e:
            print(f"Error saving problem attempt: {e}")
            return None
    
    def get_session_attempts(self, session_id: str) -> List[ProblemAttempt]:
        """Get all attempts for a quiz session."""
        try:
            response = self.client.table("problem_attempts").select("*").eq("session_id", session_id).order("timestamp").execute()
            data = self._handle_response(response)
            
            if data and isinstance(data, list):
                return [ProblemAttempt.from_dict(attempt) for attempt in data]
            return []
        except Exception as e:
            print(f"Error fetching session attempts: {e}")
            return []
    
    def increment_session_stats(self, session_id: str, is_correct: bool) -> bool:
        """Increment session problem count and correct answers."""
        try:
            # Get current session
            session = self.get_session(session_id)
            if not session:
                return False
            
            # Update counters
            new_total = session.total_problems + 1
            new_correct = session.correct_answers + (1 if is_correct else 0)
            
            response = self.client.table("quiz_sessions").update({
                "total_problems": new_total,
                "correct_answers": new_correct
            }).eq("id", session_id).execute()
            
            return self._handle_response(response) is not None
        except Exception as e:
            print(f"Error incrementing session stats: {e}")
            return False