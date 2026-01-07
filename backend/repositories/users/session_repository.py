from flask import session

class SessionRepository:
    @staticmethod
    def save_user_session(user_id: int) -> None:
        session['user_id'] = user_id

    @staticmethod
    def clear_user_session() -> None:
        session.pop('user_id', None)

    @staticmethod
    def get_user_session() -> int:
        return session.get('user_id')