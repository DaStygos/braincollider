from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import redirect_to_login
from django.db import transaction
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import PostForm, TopicForm
from .models import Post, Tag, Topic


def topic_list(request):
    topics = (
        Topic.objects.select_related("author")
        .prefetch_related("tags")
        .annotate(post_count=Count("posts", distinct=True))
    )
    tag_slug = request.GET.get("tag")
    selected_tag = None
    if tag_slug:
        selected_tag = get_object_or_404(Tag, slug=tag_slug)
        topics = topics.filter(tags=selected_tag)
    return render(
        request,
        "forum/topic_list.html",
        {"topics": topics.distinct(), "tags": Tag.objects.all(), "selected_tag": selected_tag},
    )


def topic_detail(request, topic_id):
    topic = get_object_or_404(
        Topic.objects.select_related("author").prefetch_related("tags", "posts__author"),
        pk=topic_id,
    )
    form = PostForm()
    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.topic = topic
            post.author = request.user
            post.save()
            topic.save(update_fields=["updated_at"])
            messages.success(request, "Votre réponse a été publiée.")
            return redirect("forum:topic_detail", topic_id=topic.pk)
    return render(request, "forum/topic_detail.html", {"topic": topic, "form": form})


@login_required
def topic_create(request):
    form = TopicForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        with transaction.atomic():
            topic = form.save(commit=False)
            topic.author = request.user
            topic.save()
            form.save_m2m()
        messages.success(request, "Votre sujet a été créé.")
        return redirect("forum:topic_detail", topic_id=topic.pk)
    return render(request, "forum/topic_form.html", {"form": form})


@login_required
@require_POST
def post_create(request, topic_id):
    topic = get_object_or_404(Topic, pk=topic_id)
    form = PostForm(request.POST)
    if form.is_valid():
        post = form.save(commit=False)
        post.topic = topic
        post.author = request.user
        post.save()
        topic.save(update_fields=["updated_at"])
        messages.success(request, "Votre réponse a été publiée.")
        return redirect("forum:topic_detail", topic_id=topic.pk)
    return render(
        request,
        "forum/topic_detail.html",
        {"topic": topic, "form": form},
        status=400,
    )
