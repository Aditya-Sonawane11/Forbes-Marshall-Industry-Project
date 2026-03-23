"""
Session Manager
Handles user session management with timeout and re-authentication
"""
import time
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class SessionManager:
    """Manage user sessions with timeout and validation"""

    # Session timeout in seconds (default: 30 minutes)
    SESSION_TIMEOUT = 1800  # 30 minutes

    # Warning before timeout (default: 5 minutes before expiry)
    WARNING_BEFORE_TIMEOUT = 300  # 5 minutes

    def __init__(self):
        self._session: Optional[Dict[str, Any]] = None
        self._last_activity: Optional[float] = None
        self._session_start: Optional[float] = None
        logger.info("SessionManager initialized")

    def create_session(self, user_id: int, username: str, role: str) -> bool:
        """
        Create a new session for the user

        Args:
            user_id: User ID from database
            username: Username
            role: User role (Admin, Manager, Tester)

        Returns:
            bool: Success status
        """
        try:
            current_time = time.time()
            self._session = {
                'user_id': user_id,
                'username': username,
                'role': role,
                'created_at': current_time
            }
            self._last_activity = current_time
            self._session_start = current_time

            logger.info(f"Session created for user: {username} (ID: {user_id}, Role: {role})")
            return True
        except Exception as e:
            logger.error(f"Failed to create session: {e}")
            return False

    def is_session_valid(self) -> bool:
        """
        Check if the current session is valid (exists and not expired)

        Returns:
            bool: True if session is valid, False otherwise
        """
        if not self._session or self._last_activity is None:
            logger.warning("No active session")
            return False

        current_time = time.time()
        elapsed = current_time - self._last_activity

        if elapsed > self.SESSION_TIMEOUT:
            logger.warning(f"Session expired for user: {self._session.get('username')} (idle for {elapsed:.0f}s)")
            self.destroy_session()
            return False

        return True

    def update_activity(self) -> None:
        """Update the last activity timestamp"""
        if self._session:
            self._last_activity = time.time()
            logger.debug(f"Activity updated for user: {self._session.get('username')}")

    def get_session_info(self) -> Optional[Dict[str, Any]]:
        """
        Get current session information

        Returns:
            dict: Session information including user details and timing
        """
        if not self.is_session_valid():
            return None

        current_time = time.time()
        time_remaining = int(self.SESSION_TIMEOUT - (current_time - self._last_activity))
        session_duration = int(current_time - self._session_start)

        return {
            'user_id': self._session['user_id'],
            'username': self._session['username'],
            'role': self._session['role'],
            'time_remaining_seconds': time_remaining,
            'session_duration_seconds': session_duration,
            'created_at': datetime.fromtimestamp(self._session['created_at']).isoformat(),
            'last_activity': datetime.fromtimestamp(self._last_activity).isoformat()
        }

    def get_user_id(self) -> Optional[int]:
        """Get the current user ID"""
        if self.is_session_valid():
            return self._session.get('user_id')
        return None

    def get_username(self) -> Optional[str]:
        """Get the current username"""
        if self.is_session_valid():
            return self._session.get('username')
        return None

    def get_role(self) -> Optional[str]:
        """Get the current user role"""
        if self.is_session_valid():
            return self._session.get('role')
        return None

    def should_show_warning(self) -> bool:
        """
        Check if we should show a timeout warning

        Returns:
            bool: True if session will expire soon
        """
        if not self._session or self._last_activity is None:
            return False

        current_time = time.time()
        elapsed = current_time - self._last_activity
        time_remaining = self.SESSION_TIMEOUT - elapsed

        return 0 < time_remaining <= self.WARNING_BEFORE_TIMEOUT

    def get_time_until_expiry(self) -> int:
        """
        Get the time until session expires in seconds

        Returns:
            int: Seconds until expiry, or 0 if no session
        """
        if not self._session or self._last_activity is None:
            return 0

        current_time = time.time()
        elapsed = current_time - self._last_activity
        time_remaining = self.SESSION_TIMEOUT - elapsed

        return max(0, int(time_remaining))

    def extend_session(self) -> bool:
        """
        Extend the current session (reset timeout)

        Returns:
            bool: Success status
        """
        if self.is_session_valid():
            self._last_activity = time.time()
            logger.info(f"Session extended for user: {self._session.get('username')}")
            return True
        return False

    def destroy_session(self) -> None:
        """Destroy the current session"""
        if self._session:
            username = self._session.get('username', 'Unknown')
            logger.info(f"Session destroyed for user: {username}")

        self._session = None
        self._last_activity = None
        self._session_start = None

    def set_timeout(self, timeout_seconds: int) -> None:
        """
        Set custom session timeout

        Args:
            timeout_seconds: Timeout duration in seconds
        """
        if timeout_seconds > 0:
            self.SESSION_TIMEOUT = timeout_seconds
            logger.info(f"Session timeout set to {timeout_seconds} seconds")

    def get_session_duration(self) -> int:
        """
        Get total session duration in seconds

        Returns:
            int: Session duration in seconds, or 0 if no session
        """
        if not self._session or self._session_start is None:
            return 0

        return int(time.time() - self._session_start)
