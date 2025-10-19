from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import SignUpForm, UserUpdateForm, ProfileUpdateForm

def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("accounts:profile")
    else:
        form = SignUpForm()
    return render(request, "accounts/signup.html", {"form": form})

@login_required
def profile(request):
    submissions = request.user.profile.get_submissions()
    total_score = request.user.profile.get_total_score()
    return render(request, "accounts/profile.html", {
        "submissions": submissions,
        "total_score": total_score
    })

@login_required
def edit_profile(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('accounts:profile') 
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)

    return render(request, 'accounts/edit_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })
