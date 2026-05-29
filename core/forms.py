from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import User, Post


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    interests = forms.CharField(
        required=False,
        help_text='e.g. technology, art, travel',
        widget=forms.TextInput(attrs={'placeholder': 'technology, design, travel...'})
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'interests', 'password1', 'password2')


class LoginForm(AuthenticationForm):
    pass


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('content', 'image', 'image_url', 'category', 'tags')
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4, 'placeholder': 'What\'s on your mind?'}),
            'image_url': forms.URLInput(attrs={'placeholder': 'https://...'}),
            'tags': forms.TextInput(attrs={'placeholder': 'design, tech, inspiration'}),
        }
        labels = {
            'image_url': 'Image URL (optional)',
            'tags': 'Tags (comma-separated)',
        }


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'bio', 'avatar', 'avatar_url',
                  'cover_url', 'location', 'website', 'interests')
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3}),
            'interests': forms.TextInput(attrs={'placeholder': 'technology, art, travel'}),
        }
