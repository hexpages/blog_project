from django.utils import timezone
import hashlib
from django.conf import settings

class EmailVerificationTokenGenerator:
    def _make_hash_value(self, user, timestamp):
        return f"{user.pk}{timestamp}{user.email.lower()}{user.is_active}{settings.SECRET_KEY[:20]}"

    def make_token(self, user):
        timestamp = int(timezone.now().timestamp())
        hash_input = self._make_hash_value(user, timestamp)
        return f"{timestamp}-{hashlib.sha256(hash_input.encode()).hexdigest()}"

    def check_token(self, user, token, timeout=3600):
        try:
            ts_str, hash_value = token.split('-', 1)
            timestamp = int(ts_str)
            
            if (timezone.now().timestamp() - timestamp) > timeout:
                return False
                
            expected_hash = hashlib.sha256(
                self._make_hash_value(user, timestamp).encode()
            ).hexdigest()
            
            return hash_value == expected_hash
        except (ValueError, TypeError, AttributeError):
            return False

email_verification_token = EmailVerificationTokenGenerator()