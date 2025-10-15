from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import SignUpForm, ProfilePictureForm
from problems.models import Submission

def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # connecte automatiquement après inscription
            return redirect("accounts:profile")
    else:
        form = SignUpForm()
    return render(request, "accounts/signup.html", {"form": form})

@login_required
def profile(request):
    if request.method == "POST":
        form = ProfilePictureForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            return redirect("accounts:profile")
    else:
        form = ProfilePictureForm(instance=request.user.profile)
    
    submissions = Submission.objects.filter(user=request.user)
    total_score = sum(sub.problem.get_score() for sub in submissions if sub.is_correct)
    return render(request, "accounts/profile.html", {
        "submissions": submissions,
        "total_score": total_score,
        "form": form
    })