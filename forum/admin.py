"""
Admin configuration for forum models.
"""
from django.contrib import admin
from .models import Category, Forum, Topic, Post, UserProfile


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'order', 'created_at']
    list_editable = ['order']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'description']


@admin.register(Forum)
class ForumAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'order', 'is_locked', 'created_at']
    list_filter = ['category', 'is_locked']
    list_editable = ['order', 'is_locked']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'description']


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ['title', 'forum', 'author', 'is_pinned', 'is_locked', 'views', 'created_at']
    list_filter = ['forum__category', 'forum', 'is_pinned', 'is_locked', 'created_at']
    list_editable = ['is_pinned', 'is_locked']
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ['title', 'author__username']
    date_hierarchy = 'created_at'


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['topic', 'author', 'created_at', 'is_edited']
    list_filter = ['topic__forum__category', 'topic__forum', 'created_at', 'is_edited']
    search_fields = ['content', 'author__username', 'topic__title']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'edited_at']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'post_count', 'location', 'joined_date']
    search_fields = ['user__username', 'bio', 'location']
    readonly_fields = ['joined_date', 'post_count']
