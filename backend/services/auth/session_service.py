from flask import session
from datetime import datetime, timedelta

class SessionService:
    MAX_ATTEMPTS = 5
    LOCKOUT_PERIOD = timedelta(minutes=15)

    def __init__(self):
        self.attempts = 0
        self.last_attempt = datetime.min

    def validate_attempt(self):
        if self.attempts >= self.MAX_ATTEMPTS and datetime.now() - self.last_attempt < self.LOCKOUT_PERIOD:
            return False
        return True

    def record_attempt(self, success: bool):
        self.attempts = 0 if success else self.attempts + 1
        self.last_attempt = datetime.now()

    @staticmethod
    def reset():
        session.clear()

    @staticmethod
    def get_user_id() -> int:
        return session.get('user_id')

    @staticmethod
    def is_logged_in() -> bool:
        return 'user_id' in session