"""
Forum views following Django MVC pattern.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Max, Q
from django.core.paginator import Paginator
from django.utils import timezone
from .models import Category, Forum, Topic, Post
from .forms import TopicForm, PostForm


def index(request):
    """Homepage showing all categories and forums."""
    categories = Category.objects.prefetch_related('forums').all()

    # Get forum statistics
    stats = {
        'total_topics': Topic.objects.count(),
        'total_posts': Post.objects.count(),
        'total_users': User.objects.count(),
        'latest_member': User.objects.order_by('-date_joined').first(),
    }

    context = {
        'categories': categories,
        'stats': stats,
    }
    return render(request, 'forum/index.html', context)


def category_detail(request, slug):
    """Show all forums in a category."""
    category = get_object_or_404(Category, slug=slug)
    forums = category.forums.annotate(
        topic_count=Count('topics'),
        post_count=Count('topics__posts')
    ).all()

    context = {
        'category': category,
        'forums': forums,
    }
    return render(request, 'forum/category_detail.html', context)


def forum_detail(request, category_slug, forum_slug):
    """Show all topics in a forum."""
    forum = get_object_or_404(
        Forum.objects.select_related('category'),
        category__slug=category_slug,
        slug=forum_slug
    )

    topics_list = forum.topics.select_related('author', 'forum').annotate(
        post_count=Count('posts')
    ).all()

    # Pagination
    paginator = Paginator(topics_list, 20)
    page_number = request.GET.get('page')
    topics = paginator.get_page(page_number)

    context = {
        'forum': forum,
        'topics': topics,
    }
    return render(request, 'forum/forum_detail.html', context)


def topic_detail(request, category_slug, forum_slug, topic_slug, pk):
    """Show all posts in a topic."""
    topic = get_object_or_404(
        Topic.objects.select_related('forum__category', 'author'),
        pk=pk,
        slug=topic_slug
    )

    # Increment view count
    topic.increment_views()

    posts_list = topic.posts.select_related('author', 'author__profile').all()

    # Pagination
    paginator = Paginator(posts_list, 15)
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)

    # Reply form
    form = PostForm() if request.user.is_authenticated else None

    context = {
        'topic': topic,
        'posts': posts,
        'form': form,
    }
    return render(request, 'forum/topic_detail.html', context)


@login_required
def create_topic(request, category_slug, forum_slug):
    """Create a new topic in a forum."""
    forum = get_object_or_404(
        Forum.objects.select_related('category'),
        category__slug=category_slug,
        slug=forum_slug
    )

    if forum.is_locked:
        messages.error(request, "Ce forum est verrouillé.")
        return redirect(forum.get_absolute_url())

    if request.method == 'POST':
        topic_form = TopicForm(request.POST)
        post_form = PostForm(request.POST)

        if topic_form.is_valid() and post_form.is_valid():
            # Create topic
            topic = topic_form.save(commit=False)
            topic.forum = forum
            topic.author = request.user
            topic.save()

            # Create first post
            post = post_form.save(commit=False)
            post.topic = topic
            post.author = request.user
            post.save()

            # Update user profile post count
            if hasattr(request.user, 'profile'):
                request.user.profile.update_post_count()

            messages.success(request, "Votre sujet a été créé avec succès!")
            return redirect(topic.get_absolute_url())
    else:
        topic_form = TopicForm()
        post_form = PostForm()

    context = {
        'forum': forum,
        'topic_form': topic_form,
        'post_form': post_form,
    }
    return render(request, 'forum/create_topic.html', context)


@login_required
def create_post(request, category_slug, forum_slug, topic_slug, pk):
    """Reply to a topic."""
    topic = get_object_or_404(Topic, pk=pk, slug=topic_slug)

    if topic.is_locked:
        messages.error(request, "Ce sujet est verrouillé.")
        return redirect(topic.get_absolute_url())

    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.topic = topic
            post.author = request.user
            post.save()

            # Update topic's updated_at
            topic.save(update_fields=['updated_at'])

            # Update user profile post count
            if hasattr(request.user, 'profile'):
                request.user.profile.update_post_count()

            messages.success(request, "Votre réponse a été ajoutée!")
            return redirect(post.get_absolute_url())
    else:
        return redirect(topic.get_absolute_url())


@login_required
def edit_post(request, pk):
    """Edit a post."""
    post = get_object_or_404(Post, pk=pk)

    if request.user != post.author and not request.user.is_staff:
        messages.error(request, "Vous ne pouvez pas modifier ce message.")
        return redirect(post.topic.get_absolute_url())

    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.is_edited = True
            post.edited_at = timezone.now()
            post.save()

            messages.success(request, "Votre message a été modifié!")
            return redirect(post.get_absolute_url())
    else:
        form = PostForm(instance=post)

    context = {
        'form': form,
        'post': post,
    }
    return render(request, 'forum/edit_post.html', context)


@login_required
def delete_post(request, pk):
    """Delete a post."""
    post = get_object_or_404(Post, pk=pk)

    if request.user != post.author and not request.user.is_staff:
        messages.error(request, "Vous ne pouvez pas supprimer ce message.")
        return redirect(post.topic.get_absolute_url())

    # Can't delete first post (delete topic instead)
    if post.is_first_post():
        messages.error(request, "Impossible de supprimer le premier message. Supprimez le sujet entier.")
        return redirect(post.topic.get_absolute_url())

    if request.method == 'POST':
        topic_url = post.topic.get_absolute_url()
        post.delete()

        # Update user profile post count
        if hasattr(request.user, 'profile'):
            request.user.profile.update_post_count()

        messages.success(request, "Votre message a été supprimé!")
        return redirect(topic_url)

    context = {'post': post}
    return render(request, 'forum/delete_post.html', context)


def search(request):
    """Search topics and posts."""
    query = request.GET.get('q', '')
    results = []

    if query:
        topics = Topic.objects.filter(
            Q(title__icontains=query) | Q(posts__content__icontains=query)
        ).distinct().select_related('forum', 'author')[:50]

        results = topics

    context = {
        'query': query,
        'results': results,
    }
    return render(request, 'forum/search.html', context)


# Import User model
from django.contrib.auth.models import User
