from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist

UserModel = get_user_model()

class EmailBackend(ModelBackend):
    def authenticate(self, request, email=None, username=None, password=None, **kwargs):
        email = email or username
        if not email:
            return None
            
        try:
            user = UserModel.objects.get(email__iexact=email)
            if user.check_password(password):
                return user
        except ObjectDoesNotExist:
            return None
        return None

    def get_user(self, user_id):
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None