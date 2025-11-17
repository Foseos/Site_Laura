"""
User authentication and profile views.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import RegisterForm, ProfileForm


def register(request):
    """User registration."""
    if request.user.is_authenticated:
        return redirect('forum:index')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Auto login after registration
            login(request, user)
            messages.success(request, f"Bienvenue {user.username}! Votre compte a été créé.")
            return redirect('forum:index')
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """User login."""
    if request.user.is_authenticated:
        return redirect('forum:index')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'forum:index')
            return redirect(next_url)
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")

    return render(request, 'accounts/login.html')


@login_required
def logout_view(request):
    """User logout."""
    logout(request)
    messages.success(request, "Vous avez été déconnecté.")
    return redirect('forum:index')


@login_required
def profile(request, username):
    """View user profile."""
    user = get_object_or_404(User, username=username)
    topics = user.topics.select_related('forum').order_by('-created_at')[:10]
    posts = user.posts.select_related('topic__forum').order_by('-created_at')[:20]

    context = {
        'profile_user': user,
        'topics': topics,
        'posts': posts,
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def edit_profile(request):
    """Edit user profile."""
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Votre profil a été mis à jour!")
            return redirect('accounts:profile', username=request.user.username)
    else:
        form = ProfileForm(instance=request.user.profile)

    return render(request, 'accounts/edit_profile.html', {'form': form})
