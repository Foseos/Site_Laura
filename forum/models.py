"""
Forum models following Django MVC pattern.
"""
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils.text import slugify
from markdownx.models import MarkdownxField


class Category(models.Model):
    """Forum category - top level organization."""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='📁', help_text="Emoji or icon class")
    color = models.CharField(max_length=7, default='#315620', help_text="Hex color code")
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['order', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('forum:category_detail', kwargs={'slug': self.slug})

    def get_topics_count(self):
        return Topic.objects.filter(forum__category=self).count()

    def get_posts_count(self):
        return Post.objects.filter(topic__forum__category=self).count()


class Forum(models.Model):
    """Sub-forum within a category."""
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='forums')
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=150, blank=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='💬', help_text="Emoji or icon class")
    order = models.IntegerField(default=0)
    is_locked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'name']
        unique_together = ['category', 'slug']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.category.name} - {self.name}"

    def get_absolute_url(self):
        return reverse('forum:forum_detail', kwargs={'category_slug': self.category.slug, 'forum_slug': self.slug})

    def get_topics_count(self):
        return self.topics.count()

    def get_posts_count(self):
        return Post.objects.filter(topic__forum=self).count()

    def get_last_post(self):
        return Post.objects.filter(topic__forum=self).select_related('author', 'topic').order_by('-created_at').first()


class Topic(models.Model):
    """Discussion topic within a forum."""
    forum = models.ForeignKey(Forum, on_delete=models.CASCADE, related_name='topics')
    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='topics')
    is_pinned = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=False)
    is_announced = models.BooleanField(default=False)
    views = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-is_pinned', '-is_announced', '-updated_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('forum:topic_detail', kwargs={
            'category_slug': self.forum.category.slug,
            'forum_slug': self.forum.slug,
            'topic_slug': self.slug,
            'pk': self.pk
        })

    def get_posts_count(self):
        return self.posts.count()

    def get_last_post(self):
        return self.posts.select_related('author').order_by('-created_at').first()

    def increment_views(self):
        self.views += 1
        self.save(update_fields=['views'])


class Post(models.Model):
    """Individual post within a topic."""
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='posts')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    content = MarkdownxField()
    is_edited = models.BooleanField(default=False)
    edited_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Post by {self.author.username} in {self.topic.title}"

    def get_absolute_url(self):
        return f"{self.topic.get_absolute_url()}#post-{self.pk}"

    def is_first_post(self):
        return self.topic.posts.first() == self


class UserProfile(models.Model):
    """Extended user profile for forum members."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)
    signature = models.CharField(max_length=250, blank=True)
    post_count = models.IntegerField(default=0)
    joined_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Profile of {self.user.username}"

    def get_avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return '/static/images/default-avatar.png'

    def update_post_count(self):
        self.post_count = self.user.posts.count()
        self.save(update_fields=['post_count'])
