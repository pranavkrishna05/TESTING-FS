from typing import Optional
from backend.models.user import User

class UserRepository:

    def __init__(self, db):
        self.db = db

    def add_user(self, user: User) -> User:
        query = """
        INSERT INTO users (email, password, is_active, created_at, updated_at)
        VALUES (:email, :password, :is_active, :created_at, :updated_at)
        RETURNING id;
        """
        cursor = self.db.cursor()
        cursor.execute(query, user.dict())
        user.id = cursor.fetchone()[0]
        self.db.commit()
        return user

    def get_user_by_email(self, email: str) -> Optional[User]:
        query = "SELECT * FROM users WHERE email = :email;"
        cursor = self.db.cursor()
        cursor.execute(query, {"email": email})
        row = cursor.fetchone()
        if row:
            return User(id=row[0], email=row[1], password=row[2], is_active=row[3], created_at=row[4], updated_at=row[5])
        return None