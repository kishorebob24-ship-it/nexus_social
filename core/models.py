from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    bio = models.TextField(blank=True, default='')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    avatar_url = models.URLField(blank=True, default='')  # fallback to Unsplash
    cover_url = models.URLField(blank=True, default='')
    location = models.CharField(max_length=100, blank=True, default='')
    website = models.URLField(blank=True, default='')
    interests = models.CharField(max_length=500, blank=True, default='',
                                  help_text='Comma-separated interests for AI recommendations')
    followers = models.ManyToManyField('self', symmetrical=False,
                                        related_name='following', blank=True)

    def follower_count(self):
        return self.followers.count()

    def following_count(self):
        return self.following.count()

    def get_avatar(self):
        if self.avatar:
            return self.avatar.url
        if self.avatar_url:
            return self.avatar_url
        seed = self.username
        return f'https://api.dicebear.com/7.x/personas/svg?seed={seed}'

    def __str__(self):
        return self.username


class Post(models.Model):
    CATEGORY_CHOICES = [
        ('tech', 'Technology'),
        ('art', 'Art & Design'),
        ('science', 'Science'),
        ('travel', 'Travel'),
        ('food', 'Food'),
        ('sports', 'Sports'),
        ('music', 'Music'),
        ('business', 'Business'),
        ('health', 'Health'),
        ('general', 'General'),
    ]

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField()
    image = models.ImageField(upload_to='posts/', blank=True, null=True)
    image_url = models.URLField(blank=True, default='')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='general')
    tags = models.CharField(max_length=300, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)
    bookmarks = models.ManyToManyField(User, related_name='bookmarked_posts', blank=True)
    ai_summary = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['-created_at']

    def like_count(self):
        return self.likes.count()

    def comment_count(self):
        return self.comments.count()

    def get_image(self):
        if self.image:
            return self.image.url
        if self.image_url:
            return self.image_url
        return None

    def get_tags_list(self):
        if self.tags:
            return [t.strip() for t in self.tags.split(',') if t.strip()]
        return []

    def __str__(self):
        return f'{self.author.username}: {self.content[:50]}'


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='liked_comments', blank=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'{self.author.username} on {self.post.id}'


class Notification(models.Model):
    TYPE_CHOICES = [
        ('like', 'Liked your post'),
        ('comment', 'Commented on your post'),
        ('follow', 'Started following you'),
        ('mention', 'Mentioned you'),
    ]
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications')
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
