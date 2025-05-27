# forms.py
from django import forms
from .models import NewsletterSubscriber, Comment

class NewsletterSubscriptionForm(forms.ModelForm):
    class Meta:
        model = NewsletterSubscriber
        fields = ['email']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['comment']
