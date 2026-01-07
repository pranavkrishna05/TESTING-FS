from backend.repositories.users.user_repository import UserRepository
from backend.models.users.user import User

class UserService:
    @staticmethod
    def register_user(email: str, password: str) -> User:
        if UserRepository.find_by_email(email):
            raise ValueError('Email already exists')

        if len(password) < 8:
            raise ValueError('Password must be at least 8 characters long')

        new_user = User(email=email)
        new_user.set_password(password)
        UserRepository.save(new_user)
        return new_user