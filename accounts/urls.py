from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('verify-email/<uidb64>/<token>/', views.verify_email_view, name='verify_email'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('reset-password/<uidb64>/<token>/', views.reset_password_view, name='reset_password'),
]