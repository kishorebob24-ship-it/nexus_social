from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Post, Comment, Notification

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'interests', 'date_joined')
    fieldsets = UserAdmin.fieldsets + (
        ('Profile', {'fields': ('bio', 'avatar', 'avatar_url', 'cover_url', 'location', 'website', 'interests')}),
    )

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('author', 'category', 'created_at', 'updated_at', 'like_count')
    list_filter = ('category',)
    search_fields = ('content', 'author__username', 'tags')
    ordering = ('-updated_at', '-created_at')
    list_select_related = ('author',)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'post', 'created_at')
    search_fields = ('content', 'author__username')
    list_select_related = ('author', 'post')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'sender', 'notification_type', 'post', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read')
    search_fields = ('recipient__username', 'sender__username')
