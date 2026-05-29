"""
Management command to seed demo users and posts.
Run: python manage.py seed_demo
"""
from django.core.management.base import BaseCommand
from core.models import User, Post


DEMO_USERS = [
    {
        'username': 'alice_chen', 'email': 'alice@demo.com',
        'first_name': 'Alice', 'last_name': 'Chen',
        'bio': 'Product designer & visual storyteller. Based in SF.',
        'interests': 'design, art, technology, ux',
        'avatar_url': 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=150&auto=format&fit=crop',
        'cover_url': 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=900&auto=format&fit=crop',
        'location': 'San Francisco, CA',
    },
    {
        'username': 'dev_marcus', 'email': 'marcus@demo.com',
        'first_name': 'Marcus', 'last_name': 'Rivera',
        'bio': 'Full-stack engineer. Building things that matter.',
        'interests': 'technology, programming, open source, science',
        'avatar_url': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&auto=format&fit=crop',
        'cover_url': 'https://images.unsplash.com/photo-1518770660439-4636190af475?w=900&auto=format&fit=crop',
        'location': 'Austin, TX',
    },
    {
        'username': 'travel_sofia', 'email': 'sofia@demo.com',
        'first_name': 'Sofia', 'last_name': 'Andersen',
        'bio': 'Explorer of 60+ countries. Photographer.',
        'interests': 'travel, photography, food, culture',
        'avatar_url': 'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=150&auto=format&fit=crop',
        'cover_url': 'https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?w=900&auto=format&fit=crop',
        'location': 'Copenhagen, DK',
    },
    {
        'username': 'james_photo', 'email': 'james@demo.com',
        'first_name': 'James', 'last_name': 'Okafor',
        'bio': 'Photographer & visual artist. Capturing light.',
        'interests': 'photography, art, design, travel',
        'avatar_url': 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150&auto=format&fit=crop',
        'cover_url': 'https://images.unsplash.com/photo-1497366216548-37526070297c?w=900&auto=format&fit=crop',
        'location': 'Lagos, NG',
    },
]

DEMO_POSTS = [
    {
        'author': 'alice_chen',
        'content': 'Just shipped our new design system. Three months of work distilled into reusable components that will accelerate every future product build. The hardest part? Getting agreement on spacing tokens.',
        'category': 'tech',
        'tags': 'design, ux, product',
        'image_url': 'https://images.unsplash.com/photo-1561070791-2526d30994b5?w=700&auto=format&fit=crop',
    },
    {
        'author': 'dev_marcus',
        'content': 'Hot take: the biggest productivity killer in engineering teams isn\'t context switching — it\'s poorly written Jira tickets. "Fix bug" is not a user story. Invest 10 minutes in a good description and save hours of back-and-forth.',
        'category': 'tech',
        'tags': 'engineering, productivity, agile',
        'image_url': '',
    },
    {
        'author': 'travel_sofia',
        'content': 'Woke up at 4am to catch the sunrise over the rice terraces in Bali. The fog rolling through the valleys while the golden light hit the water — some views are worth every early alarm.',
        'category': 'travel',
        'tags': 'travel, bali, nature, photography',
        'image_url': 'https://images.unsplash.com/photo-1537996194471-e657df975ab4?w=700&auto=format&fit=crop',
    },
    {
        'author': 'james_photo',
        'content': 'Golden hour portraits — there\'s genuinely nothing like it. Shot this series entirely on natural light, no reflectors. The way soft backlight wraps around a face creates a depth that no studio light can replicate.',
        'category': 'art',
        'tags': 'photography, portrait, light, art',
        'image_url': 'https://images.unsplash.com/photo-1531746020798-e6953c6e8e04?w=700&auto=format&fit=crop',
    },
    {
        'author': 'alice_chen',
        'content': 'Accessible design isn\'t a feature — it\'s a quality metric. If your product doesn\'t work for someone with a visual impairment or motor difficulty, it\'s not done. Accessibility should be in the definition of "shipped".',
        'category': 'tech',
        'tags': 'accessibility, design, inclusion',
        'image_url': '',
    },
    {
        'author': 'dev_marcus',
        'content': 'Two years ago I rebuilt our entire auth system. Today it handled 10M requests with zero incidents. The boring infrastructure work that nobody wants to talk about is often what makes everything else possible.',
        'category': 'tech',
        'tags': 'engineering, infrastructure, backend',
        'image_url': 'https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=700&auto=format&fit=crop',
    },
    {
        'author': 'travel_sofia',
        'content': 'Tokyo at 2am is a completely different city. The vending machines, the empty streets, the izakayas still buzzing. If you visit Japan and only see it in daylight, you\'re only seeing half of it.',
        'category': 'travel',
        'tags': 'japan, tokyo, travel, nightlife',
        'image_url': 'https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=700&auto=format&fit=crop',
    },
    {
        'author': 'james_photo',
        'content': 'Architectural photography teaches you to see the world in geometry. Every building is a composition of lines, shadows, and negative space. Once you start noticing it, you can\'t unsee it.',
        'category': 'art',
        'tags': 'architecture, photography, composition',
        'image_url': 'https://images.unsplash.com/photo-1486325212027-8081e485255e?w=700&auto=format&fit=crop',
    },
    {
        'author': 'alice_chen',
        'content': 'The best feedback I ever got from a user test: "I didn\'t think about it at all — I just did it." That unconscious flow state is the goal. If your users are thinking about your UI, you\'ve already failed.',
        'category': 'tech',
        'tags': 'ux, usability, design',
        'image_url': '',
    },
    {
        'author': 'dev_marcus',
        'content': 'Finished reading "A Philosophy of Software Design" for the second time. Still the most dense, practical guide to managing complexity in large codebases. Deep modules > shallow modules every time.',
        'category': 'tech',
        'tags': 'books, software, architecture',
        'image_url': 'https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=700&auto=format&fit=crop',
    },
]


class Command(BaseCommand):
    help = 'Seeds the database with demo users and posts'

    def handle(self, *args, **options):
        self.stdout.write('Creating demo users...')
        user_objects = {}
        for ud in DEMO_USERS:
            user, created = User.objects.get_or_create(username=ud['username'])
            for k, v in ud.items():
                if k != 'username':
                    setattr(user, k, v)
            user.set_password('demo1234')
            user.save()
            user_objects[ud['username']] = user
            status = 'created' if created else 'updated'
            self.stdout.write(f'  {ud["username"]} — {status}')

        # Add follow relationships
        users = list(user_objects.values())
        for i, user in enumerate(users):
            for j, other in enumerate(users):
                if i != j:
                    user.following.add(other)

        self.stdout.write('Creating demo posts...')
        for pd in DEMO_POSTS:
            author = user_objects.get(pd['author'])
            if author:
                post, created = Post.objects.get_or_create(
                    author=author,
                    content=pd['content'],
                    defaults={
                        'category': pd['category'],
                        'tags': pd['tags'],
                        'image_url': pd['image_url'],
                    }
                )
                if created:
                    # Add some likes
                    for u in users:
                        if u != author:
                            import random
                            if random.random() > 0.4:
                                post.likes.add(u)
                    self.stdout.write(f'  Post by {author.username}')

        self.stdout.write(self.style.SUCCESS('\nDemo data created! Login: alice_chen / demo1234'))
