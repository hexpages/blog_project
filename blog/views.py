from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Blog, Category, NewsletterSubscriber
from .forms import NewsletterSubscriptionForm, CommentForm
from django.contrib import messages

def home(request):
    """
    Home page view displaying:
    - Latest featured post
    - Top stories (last 3 featured posts excluding the latest)
    - 4 published posts from each category except first
    """
    # Get the latest featured post
    latest_featured = Blog.objects.filter(
        status='published',
        is_featured=True
    ).order_by('-created_at').first()

    # Get top stories (last 3 featured posts excluding the latest)
    top_stories = Blog.objects.filter(
        status='published',
        is_featured=True
    ).exclude(id=latest_featured.id if latest_featured else None).order_by('-created_at')[:3]

    # Get all categories
    categories = Category.objects.all()
    category_posts = {}
    
    # Get last 4 published posts for each category except latest one
    for category in categories:
        posts = Blog.objects.filter(
            status='published',
            category=category
        ).order_by('-created_at')[1:4]
        if posts.exists():  # Only include categories with posts
            category_posts[category] = posts

    context = {
        'categories': categories,
        'latest_featured': latest_featured,
        'top_stories': top_stories,
        'category_posts': category_posts,
        'form': NewsletterSubscriptionForm(), 
    }
    return render(request, 'blog/homepage.html', context)

def category_posts(request, slug):
    """
    Category page view displaying posts for a specific category with pagination
    """
    # Get the category or return 404
    category = get_object_or_404(Category, slug=slug)
    
    # Get all published posts for the category
    posts = Blog.objects.filter(
        status='published',
        category=category
    ).order_by('-created_at')

    # Pagination
    paginator = Paginator(posts, 6)  # Show 6 posts per page
    page = request.GET.get('page')
    
    try:
        posts_paginated = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page
        posts_paginated = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver last page
        posts_paginated = paginator.page(paginator.num_pages)

    # Get the latest featured post for the category
    latest_featured = posts.filter(is_featured=True).order_by('-created_at').first()

    context = {
        'category': category,
        'latest_featured': latest_featured,
        'posts': posts_paginated,
        'form': NewsletterSubscriptionForm(), 
    }
    return render(request, 'blog/category_posts.html', context)

def blog_post(request, slug):
    """
    Blog post page view displaying a single post
    """
    # Get the post or return 404
    post = get_object_or_404(
        Blog,
        slug=slug,
        status='published'
    )

    # Increment views count
    post.views_count += 1
    post.save(update_fields=['views_count'])

    # Get related posts (same category, excluding current post, up to 3)
    related_posts = Blog.objects.filter(
        status='published',
        category=post.category
    ).exclude(id=post.id).order_by('-created_at')[:3]

    comments = post.comments.filter(approved=True)
    form = CommentForm()

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.blog = post
            comment.user = request.user  # Ensure user is logged in
            comment.save()
            return redirect('blog_post', slug=slug)

    context = {
        'post': post,
        'related_posts': related_posts,
        'comments': comments,
        'comment_form': form,
        'form': NewsletterSubscriptionForm(), 
    }
    return render(request, 'blog/blog_post.html', context)

def subscribe(request):
    if request.method == 'POST':
        form = NewsletterSubscriptionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Thank you for subscribing!")
            return redirect(request.POST.get('next', 'home'))
        else:
            messages.error(request, "Invalid email or already subscribed.")
            return redirect(request.POST.get('next', 'home'))
    return redirect('home')

def unsubscribe(request, subscriber_id):
    subscriber = get_object_or_404(NewsletterSubscriber, id=subscriber_id)
    if request.method == 'POST':
        subscriber.is_active = False
        subscriber.save()
        messages.success(request, "You have been unsubscribed.")
        return redirect('home')
    return render(request, 'blog/unsubscribe.html', {'subscriber': subscriber})

from django.db.models import Q
from django.shortcuts import render
from .models import Blog

def blog_search(request):
    query = request.GET.get('q', '').strip()
    blogs = Blog.objects.filter(status='published')  # Only published blogs

    if query:
        blogs = blogs.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(tags__icontains=query) |
            Q(author__first_name__icontains=query) |
            Q(author__last_name__icontains=query) |
            Q(category__name__icontains=query)
        ).distinct()

    context = {
        'blogs': blogs,
        'query': query,
    }
    return render(request, 'blog/search_results.html', context)