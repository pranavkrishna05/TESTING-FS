from datetime import datetime, timedelta
from backend.repositories.auth.user_repository import UserRepository
from backend.repositories.auth.session_repository import SessionRepository
from backend.models.user import User
from backend.models.session import Session
import bcrypt

class UserService:
    def __init__(self, user_repository: UserRepository, session_repository: SessionRepository):
        self.user_repository = user_repository
        self.session_repository = session_repository

    def register_user(self, email: str, password: str) -> User:
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        new_user = User(email=email, password=hashed_password)
        return self.user_repository.add_user(new_user)

    def validate_user(self, email: str, password: str) -> Optional[Session]:
        user = self.user_repository.get_user_by_email(email)
        if not user or not bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            return None
        if user.is_locked:
            return None

        # Create session
        session = Session(user_id=user.id, expires_at=datetime.utcnow() + timedelta(hours=1))
        return self.session_repository.create_session(session)

    def handle_failed_login(self, user: User):
        user.login_attempts += 1
        if user.login_attempts >= 5:
            user.is_locked = True
        self.user_repository.update_user(user)