from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordResetForm,
    SetPasswordForm
)
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password

CustomUser = get_user_model()

class SignupForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        strip=False,
    )
    password2 = forms.CharField(
        label="Password Confirmation",
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        strip=False,
    )

    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError("This email is already registered.")
        return email

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if password1:
            validate_password(password1)
        return password1

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"autocomplete": "email"})
    )

class ForgotPasswordForm(PasswordResetForm):
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"autocomplete": "email"})
    )

class ResetPasswordForm(SetPasswordForm):
    pass