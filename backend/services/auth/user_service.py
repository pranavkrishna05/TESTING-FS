from datetime import datetime, timedelta
from backend.repositories.auth.user_repository import UserRepository
from backend.repositories.auth.session_repository import SessionRepository
from backend.repositories.auth.password_reset_repository import PasswordResetRepository
from backend.models.user import User
from backend.models.session import Session
from backend.models.password_reset import PasswordReset
import bcrypt
import secrets

class UserService:
    def __init__(self, user_repository: UserRepository, session_repository: SessionRepository, password_reset_repository: PasswordResetRepository):
        self.user_repository = user_repository
        self.session_repository = session_repository
        self.password_reset_repository = password_reset_repository

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

    def create_password_reset(self, email: str) -> Optional[PasswordReset]:
        user = self.user_repository.get_user_by_email(email)
        if not user:
            return None

        token = secrets.token_urlsafe(20)
        expires_at = datetime.utcnow() + timedelta(hours=24)
        password_reset = PasswordReset(user_id=user.id, token=token, expires_at=expires_at)
        return self.password_reset_repository.create_password_reset(password_reset)

    def reset_password(self, token: str, new_password: str) -> bool:
        password_reset = self.password_reset_repository.get_password_reset_by_token(token)
        if not password_reset or password_reset.expires_at < datetime.utcnow() or password_reset.used:
            return False

        user = self.user_repository.get_user_by_email(password_reset.user_id)
        if not user:
            return False

        user.password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        self.user_repository.update_user(user)
        self.password_reset_repository.mark_token_as_used(password_reset)
        return True