# Nexus Social — AI-Powered Social Media App

A professional social media platform built with Django + HTML/CSS/JS, featuring AI-powered content recommendations via Claude.

## Features

- **AI Feed Recommendations** — Claude analyzes your interests and activity to rank posts
- **AI Caption Assistant** — Get AI-suggested captions when creating posts
- **Follow System** — Follow users, see their posts in your feed
- **Likes, Comments, Bookmarks** — Full post interaction suite
- **Explore Page** — Search posts by keyword, tag, or category
- **Notifications** — Real-time-style notifications for likes, follows, comments
- **Rich Profiles** — Avatars, cover photos, bios, interests, stats
- **9 Post Categories** — Tech, Art, Travel, Science, Food, Sports, Music, Business, Health

## Quick Start

```bash
# 1. Clone and enter
cd nexus_social

# 2. Run setup (installs deps, migrates DB, seeds demo data)
bash setup.sh

# 3. Optional: add your Anthropic API key for AI features
export ANTHROPIC_API_KEY=sk-ant-your-key-here

# 4. Start the server
python manage.py runserver
```

Open http://127.0.0.1:8000 — log in with `alice_chen` / `demo1234`

## Demo Accounts

| Username      | Password   | Focus              |
|---------------|------------|--------------------|
| alice_chen    | demo1234   | Design & UX        |
| dev_marcus    | demo1234   | Engineering        |
| travel_sofia  | demo1234   | Travel             |
| james_photo   | demo1234   | Photography        |
| admin         | admin123   | Admin panel        |

Admin panel: http://127.0.0.1:8000/admin/

## AI Features

### Feed Recommendations
Without an API key: posts are scored by interest/category overlap.
With API key: Claude ranks posts by semantic relevance to your interests.

### Caption Assistant
On the Create Post page, write a draft and click "Suggest Caption" for an AI-polished version. Falls back gracefully when no API key is set.

## Project Structure

```
nexus_social/
├── core/
│   ├── models.py          # User, Post, Comment, Notification
│   ├── views.py           # All views + AI recommendation logic
│   ├── forms.py           # Register, Login, Post, Profile forms
│   ├── urls.py            # URL routing
│   ├── admin.py           # Admin registration
│   ├── templates/core/    # All HTML templates
│   └── management/commands/seed_demo.py
├── nexus_social/
│   ├── settings.py
│   └── urls.py
├── manage.py
├── requirements.txt
└── setup.sh
```

## Tech Stack

- **Backend**: Django 4.2, SQLite (easily swappable to Postgres)
- **Frontend**: Vanilla HTML/CSS/JS — no frameworks, no npm
- **AI**: Anthropic Claude API (claude-sonnet-4)
- **Images**: Unsplash URLs + local upload support via Pillow
- **Fonts**: Playfair Display + DM Sans (Google Fonts)
