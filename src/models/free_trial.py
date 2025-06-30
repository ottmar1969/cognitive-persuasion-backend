from datetime import datetime, timedelta
from src.models.user_simple import db

class FreeTrialManager:
    """
    Manages free trial functionality for new users
    """
    
    # Trial configuration
    TRIAL_DURATION_MINUTES = 3
    TRIAL_SESSIONS_LIMIT = 1
    TRIAL_BUSINESSES_LIMIT = 1
    TRIAL_AUDIENCES_LIMIT = 2
    
    @staticmethod
    def is_trial_eligible(user):
        """Check if user is eligible for free trial"""
        # New users who haven't used trial yet
        return (user.trial_used == False and 
                user.credits == 0 and
                user.created_at is not None)
    
    @staticmethod
    def is_trial_active(user):
        """Check if user's trial is currently active"""
        if not user.trial_started or user.trial_used:
            return False
            
        # Check time limit
        trial_end = user.trial_started + timedelta(minutes=FreeTrialManager.TRIAL_DURATION_MINUTES)
        current_time = datetime.utcnow()
        
        # Check session limit
        sessions_remaining = FreeTrialManager.TRIAL_SESSIONS_LIMIT - user.trial_sessions_used
        
        return (current_time < trial_end and sessions_remaining > 0)
    
    @staticmethod
    def start_trial(user):
        """Start free trial for user"""
        if not FreeTrialManager.is_trial_eligible(user):
            return False
            
        user.trial_started = datetime.utcnow()
        user.trial_sessions_used = 0
        db.session.commit()
        return True
    
    @staticmethod
    def use_trial_session(user):
        """Use one trial session"""
        if not FreeTrialManager.is_trial_active(user):
            return False
            
        user.trial_sessions_used += 1
        
        # Mark trial as used if no sessions remaining
        if user.trial_sessions_used >= FreeTrialManager.TRIAL_SESSIONS_LIMIT:
            user.trial_used = True
            
        db.session.commit()
        return True
    
    @staticmethod
    def get_trial_status(user):
        """Get detailed trial status for user"""
        if not user.trial_started:
            return {
                'eligible': FreeTrialManager.is_trial_eligible(user),
                'active': False,
                'used': user.trial_used,
                'sessions_remaining': 0,
                'time_remaining_seconds': 0,
                'can_start': FreeTrialManager.is_trial_eligible(user)
            }
        
        trial_end = user.trial_started + timedelta(minutes=FreeTrialManager.TRIAL_DURATION_MINUTES)
        current_time = datetime.utcnow()
        time_remaining = max(0, (trial_end - current_time).total_seconds())
        sessions_remaining = max(0, FreeTrialManager.TRIAL_SESSIONS_LIMIT - user.trial_sessions_used)
        
        return {
            'eligible': False,
            'active': FreeTrialManager.is_trial_active(user),
            'used': user.trial_used,
            'sessions_remaining': sessions_remaining,
            'time_remaining_seconds': int(time_remaining),
            'time_remaining_formatted': FreeTrialManager._format_time_remaining(time_remaining),
            'trial_started': user.trial_started.isoformat() if user.trial_started else None,
            'sessions_used': user.trial_sessions_used,
            'can_start': False
        }
    
    @staticmethod
    def _format_time_remaining(seconds):
        """Format remaining time in human-readable format"""
        if seconds <= 0:
            return "0:00"
        
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes}:{seconds:02d}"
    
    @staticmethod
    def extend_trial(user, additional_minutes=0, additional_sessions=0):
        """Extend trial (for promotions, referrals, etc.)"""
        if not user.trial_started:
            return False
        
        # Extend time if trial is still active
        if FreeTrialManager.is_trial_active(user):
            # This would require storing trial_end_time separately
            # For now, we'll just add sessions
            pass
        
        # Add additional sessions
        if additional_sessions > 0:
            # Reduce sessions used (effectively adding more)
            user.trial_sessions_used = max(0, user.trial_sessions_used - additional_sessions)
            if user.trial_sessions_used < FreeTrialManager.TRIAL_SESSIONS_LIMIT:
                user.trial_used = False
            db.session.commit()
            return True
        
        return False

# Add trial fields to User model (these should be added to user_simple.py)
"""
Add these fields to the User class in user_simple.py:

trial_started = db.Column(db.DateTime, nullable=True)
trial_used = db.Column(db.Boolean, default=False)
trial_sessions_used = db.Column(db.Integer, default=0)
"""

