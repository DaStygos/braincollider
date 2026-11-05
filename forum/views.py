from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Count
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_GET, require_POST

from core.rate_limits import rate_limit

from .forms import PostForm, TopicForm
from .models import Post, Tag, Topic


TOPICS_PER_PAGE = 25
POSTS_PER_PAGE = 50


def _topic_detail_context(request, topic, form):
    post_paginator = Paginator(
        topic.posts.select_related("author"), POSTS_PER_PAGE
    )
    post_page_number = request.GET.get("posts")
    if post_page_number == "last":
        post_page = post_paginator.page(post_paginator.num_pages)
    else:
        post_page = post_paginator.get_page(post_page_number)
    return {
        "topic": topic,
        "form": form,
        "posts": post_page.object_list,
        "post_page": post_page,
        "post_count": post_paginator.count,
    }


def topic_list(request):
    topics = (
        Topic.objects.select_related("author")
        .prefetch_related("tags")
        .annotate(post_count=Count("posts", distinct=True))
    )
    tag_slug = request.GET.get("tag")
    selected_sort = request.GET.get("sort", "activity")
    sort_orders = {
        "activity": ("-updated_at", "-pk"),
        "newest": ("-created_at", "-pk"),
        "oldest": ("created_at", "pk"),
    }
    if selected_sort not in sort_orders:
        selected_sort = "activity"
    selected_tag = None
    if tag_slug:
        selected_tag = get_object_or_404(Tag, slug=tag_slug)
        topics = topics.filter(tags=selected_tag)
    topics = topics.order_by(*sort_orders[selected_sort])
    topics = topics.distinct()
    paginator = Paginator(topics, TOPICS_PER_PAGE)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(
        request,
        "forum/topic_list.html",
        {
            "topics": page_obj.object_list,
            "page_obj": page_obj,
            "topic_count": paginator.count,
            "tags": Tag.objects.all(),
            "selected_tag": selected_tag,
            "selected_sort": selected_sort,
        },
    )


@require_GET
def topic_detail(request, topic_id):
    topic = get_object_or_404(
        Topic.objects.select_related("author").prefetch_related("tags"),
        pk=topic_id,
    )
    form = PostForm()
    return render(
        request,
        "forum/topic_detail.html",
        _topic_detail_context(request, topic, form),
    )


@login_required
@rate_limit("forum-topic-create", limit=5, period=60 * 60, methods={"POST"})
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
@rate_limit("forum-reply", limit=30, period=60 * 60, methods={"POST"})
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
        return redirect(f"{reverse('forum:topic_detail', args=[topic.pk])}?posts=last")
    return render(
        request,
        "forum/topic_detail.html",
        _topic_detail_context(request, topic, form),
        status=400,
    )
