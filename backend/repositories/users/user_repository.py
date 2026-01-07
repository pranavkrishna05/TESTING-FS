from backend.models.users.user import User
from backend import db

class UserRepository:
    @staticmethod
    def find_by_email(email: str) -> User:
        return User.query.filter_by(email=email).first()

    @staticmethod
    def save(user: User) -> None:
        db.session.add(user)
        db.session.commit()