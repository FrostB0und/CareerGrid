from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

from .models import Post, Profile
from django.db.models import Q

def home(request):
    if request.user.is_authenticated:
        following_ids = Follow.objects.filter(
            follower=request.user
        ).values_list('following_id', flat=True)

        posts = Post.objects.filter(
            user__in=list(following_ids) + [request.user.id]
        ).order_by('-created_at')

        # Suggest users not already followed (excluding yourself), max 3
        suggestions = User.objects.exclude(
            id__in=list(following_ids) + [request.user.id]
        )[:3]
    else:
        posts = Post.objects.all().order_by('-created_at')
        suggestions = []

    return render(request, 'home.html', {'posts': posts, 'suggestions': suggestions})

# ---------------- HOME ----------------
def home(request):
    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'home.html', {'posts': posts})


# ---------------- PROFILE PAGE ----------------
def profile(request, username):
    user_obj = get_object_or_404(User, username=username)

    profile, created = Profile.objects.get_or_create(user=user_obj)

    posts = Post.objects.filter(user=user_obj).order_by('-created_at')

    return render(request, 'profile.html', {
        'profile_user': user_obj,
        'profile': profile,
        'posts': posts
    })


# ---------------- CREATE POST ----------------
@login_required
def create_post(request):
    if request.method == "POST":
        content = request.POST.get("content", "")

        Post.objects.create(
            user=request.user,
            content=content
        )

        return redirect('/')

    return render(request, "create_post.html")


# ---------------- REGISTER ----------------
def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/')
    else:
        form = UserCreationForm()

    return render(request, 'register.html', {'form': form})


# ---------------- EDIT PROFILE ----------------
@login_required
def edit_profile(request):
    user = request.user
    profile, created = Profile.objects.get_or_create(user=user)

    if request.method == "POST":

        # User fields
        user.first_name = request.POST.get("first_name", "")
        user.last_name = request.POST.get("last_name", "")
        user.email = request.POST.get("email", "")
        user.save()

        # Profile fields
        profile.bio = request.POST.get("bio", "")
        profile.location = request.POST.get("location", "")
        profile.website = request.POST.get("website", "")
        profile.phone = request.POST.get("phone", "")
        profile.save()

        return redirect("profile", username=user.username)

    return render(request, "edit_profile.html", {
        "profile": profile,
        "user": user
    })