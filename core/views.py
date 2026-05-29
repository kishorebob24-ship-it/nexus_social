import json
import urllib.request
import urllib.parse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.db.models import Q, Count
from django.conf import settings
from .models import User, Post, Comment, Notification
from .forms import RegisterForm, LoginForm, PostForm, ProfileForm


def get_ai_recommendations(user, all_posts):
    """Call Anthropic API to get personalized post recommendations."""
    api_key = settings.ANTHROPIC_API_KEY
    if not api_key:
        # Fallback: simple interest-based scoring
        return _fallback_recommendations(user, all_posts)

    interests = user.interests or 'general content'
    recent_categories = list(
        Post.objects.filter(likes=user).values_list('category', flat=True)[:10]
    )
    recent_tags = []
    for p in Post.objects.filter(likes=user)[:5]:
        recent_tags.extend(p.get_tags_list())

    posts_data = [
        {
            'id': p.id,
            'category': p.category,
            'tags': p.get_tags_list(),
            'likes': p.like_count(),
            'author': p.author.username,
            'content_preview': p.content[:100],
        }
        for p in all_posts[:50]
    ]

    prompt = f"""You are a recommendation engine for a social media platform.
User interests: {interests}
Categories they've liked: {recent_categories}
Tags they engage with: {recent_tags}

Available posts (JSON): {json.dumps(posts_data)}

Return ONLY a JSON array of post IDs ordered by relevance to this user, most relevant first.
Include all IDs. Example: [42, 17, 3, 8, ...]
Return ONLY the JSON array, no explanation."""

    try:
        payload = json.dumps({
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 500,
            "messages": [{"role": "user", "content": prompt}]
        }).encode('utf-8')

        req = urllib.request.Request(
            'https://api.anthropic.com/v1/messages',
            data=payload,
            headers={
                'Content-Type': 'application/json',
                'x-api-key': api_key,
                'anthropic-version': '2023-06-01',
            }
        )
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read())
            text = data['content'][0]['text'].strip()
            # strip markdown fences if present
            if text.startswith('```'):
                text = text.split('```')[1]
                if text.startswith('json'):
                    text = text[4:]
            ordered_ids = json.loads(text)
            post_map = {p.id: p for p in all_posts}
            return [post_map[pid] for pid in ordered_ids if pid in post_map]
    except Exception:
        return _fallback_recommendations(user, all_posts)


def _fallback_recommendations(user, all_posts):
    """Score posts by interest overlap without AI."""
    interests = set(i.strip().lower() for i in (user.interests or '').split(',') if i.strip())
    liked_cats = set(Post.objects.filter(likes=user).values_list('category', flat=True))

    def score(post):
        s = 0
        if post.category in liked_cats:
            s += 3
        for tag in post.get_tags_list():
            if tag.lower() in interests:
                s += 2
        if post.category.lower() in interests:
            s += 2
        s += min(post.like_count(), 10)
        return s

    return sorted(all_posts, key=score, reverse=True)


def get_ai_caption(content, category):
    """Get AI-generated caption suggestion."""
    api_key = settings.ANTHROPIC_API_KEY
    if not api_key:
        return None
    try:
        prompt = f"Write a short, engaging social media caption (max 2 sentences) for a {category} post about: {content[:200]}. Be concise and compelling."
        payload = json.dumps({
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 150,
            "messages": [{"role": "user", "content": prompt}]
        }).encode('utf-8')
        req = urllib.request.Request(
            'https://api.anthropic.com/v1/messages',
            data=payload,
            headers={
                'Content-Type': 'application/json',
                'x-api-key': api_key,
                'anthropic-version': '2023-06-01',
            }
        )
        with urllib.request.urlopen(req, timeout=6) as resp:
            data = json.loads(resp.read())
            return data['content'][0]['text'].strip()
    except Exception:
        return None


# ── Auth views ──────────────────────────────────────────────────────────────

def register_view(request):
    if request.user.is_authenticated:
        return redirect('feed')
    form = RegisterForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        login(request, user)
        return redirect('feed')
    return render(request, 'core/auth.html', {'form': form, 'mode': 'register'})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('feed')
    form = LoginForm(request, request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        return redirect(request.GET.get('next', 'feed'))
    return render(request, 'core/auth.html', {'form': form, 'mode': 'login'})


def logout_view(request):
    logout(request)
    return redirect('login')


# ── Main views ───────────────────────────────────────────────────────────────

@login_required
def feed(request):
    following_users = request.user.following.all()
    following_posts = Post.objects.filter(
        author__in=following_users
    ).select_related('author').prefetch_related('likes', 'comments')

    all_posts = Post.objects.exclude(
        author=request.user
    ).select_related('author').prefetch_related('likes', 'comments')

    recommended = get_ai_recommendations(request.user, list(all_posts))

    # Merge: following first, then recommended (deduped)
    seen_ids = set(p.id for p in following_posts)
    final_feed = list(following_posts)
    for p in recommended:
        if p.id not in seen_ids:
            final_feed.append(p)
            seen_ids.add(p.id)

    # Suggested users to follow
    suggested = User.objects.exclude(
        id=request.user.id
    ).exclude(
        id__in=following_users
    ).annotate(
        follower_count=Count('followers')
    ).order_by('-follower_count')[:5]

    unread_notif = request.user.notifications.filter(is_read=False).count()

    return render(request, 'core/feed.html', {
        'posts': final_feed[:30],
        'suggested_users': suggested,
        'unread_notif': unread_notif,
    })


@login_required
def explore(request):
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')

    posts = Post.objects.select_related('author').prefetch_related('likes')

    if query:
        posts = posts.filter(
            Q(content__icontains=query) |
            Q(tags__icontains=query) |
            Q(author__username__icontains=query)
        )
    if category:
        posts = posts.filter(category=category)

    posts = posts.annotate(like_count=Count('likes')).order_by('-like_count', '-created_at')[:40]

    trending_tags = []
    all_tags = Post.objects.exclude(tags='').values_list('tags', flat=True)
    tag_freq = {}
    for tag_str in all_tags:
        for t in tag_str.split(','):
            t = t.strip()
            if t:
                tag_freq[t] = tag_freq.get(t, 0) + 1
    trending_tags = sorted(tag_freq.items(), key=lambda x: -x[1])[:12]

    categories = Post.CATEGORY_CHOICES
    return render(request, 'core/explore.html', {
        'posts': posts,
        'query': query,
        'selected_category': category,
        'trending_tags': trending_tags,
        'categories': categories,
    })


@login_required
def profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    posts = profile_user.posts.prefetch_related('likes', 'comments').all()
    is_following = request.user.following.filter(id=profile_user.id).exists()
    is_own = request.user == profile_user
    return render(request, 'core/profile.html', {
        'profile_user': profile_user,
        'posts': posts,
        'is_following': is_following,
        'is_own': is_own,
    })


@login_required
def edit_profile(request):
    form = ProfileForm(request.POST or None, request.FILES or None, instance=request.user)
    if form.is_valid():
        form.save()
        return redirect('profile', username=request.user.username)
    return render(request, 'core/edit_profile.html', {'form': form})


@login_required
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    comments = post.comments.select_related('author').all()
    return render(request, 'core/post_detail.html', {
        'post': post,
        'comments': comments,
    })


@login_required
def create_post(request):
    form = PostForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('feed')
    return render(request, 'core/create_post.html', {'form': form})

@login_required
def notifications_view(request):
    # Get all notifications first
    notifs = request.user.notifications.select_related(
        'sender', 'post'
    ).all()

    # Mark unread notifications as read
    notifs.filter(is_read=False).update(is_read=True)

    # Limit to latest 50 after update
    notifs = notifs.order_by('-created_at')[:50]

    return render(request, 'core/notifications.html', {
        'notifications': notifs
    })


# ── AJAX endpoints ────────────────────────────────────────────────────────────

@login_required
@require_POST
def toggle_like(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.user in post.likes.all():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True
        if post.author != request.user:
            Notification.objects.create(
                recipient=post.author,
                sender=request.user,
                notification_type='like',
                post=post
            )
    return JsonResponse({'liked': liked, 'count': post.like_count()})


@login_required
@require_POST
def toggle_follow(request, username):
    target = get_object_or_404(User, username=username)
    if target == request.user:
        return JsonResponse({'error': 'Cannot follow yourself'}, status=400)
    if request.user.following.filter(id=target.id).exists():
        request.user.following.remove(target)
        following = False
    else:
        request.user.following.add(target)
        following = True
        Notification.objects.create(
            recipient=target,
            sender=request.user,
            notification_type='follow'
        )
    return JsonResponse({'following': following, 'count': target.follower_count()})


@login_required
@require_POST
def toggle_bookmark(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.user in post.bookmarks.all():
        post.bookmarks.remove(request.user)
        bookmarked = False
    else:
        post.bookmarks.add(request.user)
        bookmarked = True
    return JsonResponse({'bookmarked': bookmarked})


@login_required
@require_POST
def add_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)
    content = request.POST.get('content', '').strip()
    if not content:
        return JsonResponse({'error': 'Empty comment'}, status=400)
    comment = Comment.objects.create(post=post, author=request.user, content=content)
    if post.author != request.user:
        Notification.objects.create(
            recipient=post.author,
            sender=request.user,
            notification_type='comment',
            post=post
        )
    return JsonResponse({
        'id': comment.id,
        'content': comment.content,
        'author': request.user.username,
        'avatar': request.user.get_avatar(),
        'created_at': comment.created_at.strftime('%b %d, %Y'),
    })


@login_required
def ai_suggest(request):
    """Return AI caption suggestion via AJAX."""
    content = request.GET.get('content', '')
    category = request.GET.get('category', 'general')
    suggestion = get_ai_caption(content, category)
    return JsonResponse({'suggestion': suggestion or ''})


@login_required
def bookmarks_view(request):
    posts = request.user.bookmarked_posts.select_related('author').prefetch_related('likes').all()
    return render(request, 'core/bookmarks.html', {'posts': posts})
