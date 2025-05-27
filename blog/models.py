from django.db import models
from django.utils.text import slugify
import uuid
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django_ckeditor_5.fields import CKEditor5Field

class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=60, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Blog(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='blog_posts'
    )
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='blogs'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    excerpt = models.CharField(max_length=300, blank=True)
    content = CKEditor5Field()  # Updated to CKEditor 5 field
    featured_image = models.ImageField(
        upload_to='blog_images/%Y/%m/',
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_featured = models.BooleanField(default=False)
    meta_description = models.CharField(max_length=160, blank=True)
    tags = models.CharField(max_length=200, blank=True)
    views_count = models.PositiveIntegerField(default=0, editable=False)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['status']),
            models.Index(fields=['-created_at']),
        ]

    def save(self, *args, **kwargs):
        is_new_post = self._state.adding
        if is_new_post:
            super().save(*args, **kwargs)
        if not self.slug or self.slug.strip() == '':
            base_slug = slugify(self.title)
            self.slug = f"{base_slug}-{str(self.id)}"
        super().save(*args, **kwargs)
        if is_new_post and self.status == 'published':
            self._send_newsletter()

    def _send_newsletter(self):
        """Send email notification to subscribers and admin for new blog post."""
        subscribers = NewsletterSubscriber.objects.filter(is_active=True)
        admin_email = 'your-email@example.com'  # Replace with your email
        subject = f"New Blog Post: {self.title}"
        post_url = f"{settings.SITE_URL}{reverse('blog_post', args=[self.slug])}"

        # Prepare email content
        for recipient in list(subscribers) + [{'email': admin_email}]:
            unsubscribe_url = (
                f"{settings.SITE_URL}/newsletter/unsubscribe/{recipient.id}/"
                if isinstance(recipient, NewsletterSubscriber)
                else ''
            )
            html_message = render_to_string(
                'emails/new_post_notification.html',
                {
                    'post': self,
                    'subscriber': recipient,
                    'unsubscribe_url': unsubscribe_url,
                    'post_url': post_url,
                }
            )
            try:
                send_mail(
                    subject=subject,
                    message='',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[recipient.email],
                    html_message=html_message,
                    fail_silently=False,
                )
            except Exception:
                continue  # Skip failed emails, continue with others

    def __str__(self):
        return self.title
    
class Comment(models.Model):
    blog = models.ForeignKey('Blog', on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=True)  # Optional: for moderation

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Comment by {self.user} on {self.blog}'    

class NewsletterSubscriber(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    
    class Meta:
        ordering = ['-subscribed_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['is_active']),
        ]

    def __str__(self):
        return self.email