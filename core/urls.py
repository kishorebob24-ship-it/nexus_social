from django.urls import path
from . import views

urlpatterns = [
    path('', views.feed, name='feed'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('explore/', views.explore, name='explore'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('profile/edit/me/', views.edit_profile, name='edit_profile'),
    path('post/create/', views.create_post, name='create_post'),
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('bookmarks/', views.bookmarks_view, name='bookmarks'),
    # AJAX
    path('api/like/<int:pk>/', views.toggle_like, name='toggle_like'),
    path('api/follow/<str:username>/', views.toggle_follow, name='toggle_follow'),
    path('api/bookmark/<int:pk>/', views.toggle_bookmark, name='toggle_bookmark'),
    path('api/comment/<int:pk>/', views.add_comment, name='add_comment'),
    path('api/ai-suggest/', views.ai_suggest, name='ai_suggest'),
]
