from django.contrib import admin

from .models import Post, Tag, Topic


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "slug")


class PostInline(admin.TabularInline):
    model = Post
    extra = 0
    readonly_fields = ("created_at",)


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "created_at", "updated_at")
    list_filter = ("tags", "created_at")
    search_fields = ("title", "description", "author__username")
    filter_horizontal = ("tags",)
    inlines = (PostInline,)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("topic", "author", "created_at")
    list_filter = ("created_at",)
    search_fields = ("content", "topic__title", "author__username")
    readonly_fields = ("created_at",)
