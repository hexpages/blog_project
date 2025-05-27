# admin.py
from django.contrib import admin
from .models import Category, Blog, NewsletterSubscriber, Comment

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at', 'updated_at']
    list_filter = ['created_at']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}  # Auto-populate base slug from name

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    readonly_fields = ['author'] 

    def save_model(self, request, obj, form, change):
        if not change or not obj.author:  # If it's a new post (not being edited), set the author
            obj.author = request.user
        super().save_model(request, obj, form, change)

    list_display = ['title', 'slug', 'author', 'category', 'status', 'created_at']
    list_filter = ['status', 'category', 'created_at']
    search_fields = ['title', 'slug', 'content']
    prepopulated_fields = {'slug': ('title',)}  # Auto-populate base slug from title
    list_per_page = 20

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'blog', 'comment', 'created_at', 'approved')
    list_filter = ('approved', 'created_at')
    search_fields = ['comment']

@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ['email', 'is_active', 'subscribed_at']
    list_filter = ['is_active', 'subscribed_at']
    search_fields = ['email']