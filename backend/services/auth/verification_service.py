from itsdangerous import URLSafeTimedSerializer

class VerificationService:
    serializer = URLSafeTimedSerializer('ThisIsASecret!')

    @staticmethod
    def generate_token(email: str) -> str:
        return VerificationService.serializer.dumps(email, salt='email-verification-salt')

    @staticmethod
    def confirm_token(token: str, expiration: int = 86400) -> str:
        try:
            email = VerificationService.serializer.loads(token, salt='email-verification-salt', max_age=expiration)
        except (SignatureExpired, BadSignature):
            return None
        return email