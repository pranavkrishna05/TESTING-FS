from typing import Optional
from backend.models.password_reset import PasswordReset

class PasswordResetRepository:

    def __init__(self, db):
        self.db = db

    def create_password_reset(self, password_reset: PasswordReset) -> PasswordReset:
        query = """
        INSERT INTO password_resets (user_id, token, expires_at, used)
        VALUES (:user_id, :token, :expires_at, :used)
        RETURNING id;
        """
        cursor = self.db.cursor()
        cursor.execute(query, password_reset.dict())
        password_reset.id = cursor.fetchone()[0]
        self.db.commit()
        return password_reset

    def get_password_reset_by_token(self, token: str) -> Optional[PasswordReset]:
        query = "SELECT * FROM password_resets WHERE token = :token;"
        cursor = self.db.cursor()
        cursor.execute(query, {"token": token})
        row = cursor.fetchone()
        if row:
            return PasswordReset(id=row[0], user_id=row[1], token=row[2], expires_at=row[3], used=row[4])
        return None

    def mark_token_as_used(self, password_reset: PasswordReset) -> None:
        query = """
        UPDATE password_resets SET used = :used
        WHERE id = :id;
        """
        cursor = self.db.cursor()
        cursor.execute(query, {"used": True, "id": password_reset.id})
        self.db.commit()