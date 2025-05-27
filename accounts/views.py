from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.core.mail import send_mail
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from .forms import SignupForm, LoginForm, ForgotPasswordForm, ResetPasswordForm
from .tokens import email_verification_token
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.conf import settings

CustomUser = get_user_model()

def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.save()
            
            user.email_verification_token = email_verification_token.make_token(user)
            user.email_verification_token_created_at = timezone.now()
            user.save(update_fields=['email_verification_token', 'email_verification_token_created_at'])
            
            uid = urlsafe_base64_encode(force_bytes(str(user.pk)))
            verification_link = request.build_absolute_uri(
                f"/accounts/verify-email/{uid}/{user.email_verification_token}/"
            )
            
            send_mail(
                'Verify Your Email',
                f'Click the link to verify your email: {verification_link}',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
                html_message=f'''  
                <h2>Email Verification</h2>
                <p>Click below to verify your email:</p>
                <a href="{verification_link}">Verify Email</a>
                <p>Link expires in 1 hour.</p>
                '''
            )
            messages.success(request, 'Verification email sent! Please check your inbox.')
            return redirect('login')
    else:
        form = SignupForm()
    return render(request, 'accounts/signup.html', {'form': form})

def verify_email_view(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
        
        if not user.email_verification_token:
            messages.error(request, 'This link has already been used.')
            return redirect('login')
            
        if email_verification_token.check_token(user, token):
            user.is_email_verified = True
            user.email_verification_token = None
            user.email_verification_token_created_at = None
            user.save()
            messages.success(request, 'Email verified successfully! You may now login.')
            return redirect('login')
            
        messages.error(request, 'Invalid or expired verification link.')
    except (CustomUser.DoesNotExist, ValueError, TypeError):
        messages.error(request, 'Invalid verification link.')
    return redirect('login')

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            
            user = authenticate(
                request,
                email=username,
                username=username,
                password=password
            )
            
            if user is not None:
                if user.is_email_verified:
                    login(request, user)
                    messages.success(request, 'Login successful!')
                    return redirect('home')
                messages.error(request, 'Please verify your email first.')
            else:
                messages.error(request, 'Invalid email or password.')
        else:
            messages.error(request, 'Invalid password!')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})

def forgot_password_view(request):
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = CustomUser.objects.get(email=email)
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(str(user.pk)))
                reset_link = request.build_absolute_uri(
                    f"/accounts/reset-password/{uid}/{token}/"
                )
                
                send_mail(
                    'Password Reset Request',
                    f'Click the link to reset your password: {reset_link}',
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    html_message=f'''
                    <h2>Password Reset</h2>
                    <p>Click below to reset your password:</p>
                    <a href="{reset_link}">Reset Password</a>
                    <p>This link expires in 24 hours.</p>
                    '''
                )
                messages.success(request, 'Password reset link sent to your email.')
            except CustomUser.DoesNotExist:
                messages.error(request, 'No account found with this email.')
            return redirect('login')
    else:
        form = ForgotPasswordForm()
    return render(request, 'accounts/forgot_password.html', {'form': form})

def reset_password_view(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except (CustomUser.DoesNotExist, ValueError, TypeError):
        user = None

    if user is None or not default_token_generator.check_token(user, token):
        messages.error(request, 'Invalid or expired password reset link.')
        return redirect('login')

    if request.method == 'POST':
        form = ResetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Password updated successfully! Please login with your new password.')
            return redirect('login')
    else:
        form = ResetPasswordForm(user)
    
    return render(request, 'accounts/reset_password.html', {
        'form': form,
        'validlink': True
    })

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')