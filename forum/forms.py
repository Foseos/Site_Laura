"""
Forum forms.
"""
from django import forms
from .models import Topic, Post


class TopicForm(forms.ModelForm):
    """Form for creating a new topic."""
    class Meta:
        model = Topic
        fields = ['title']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-4 focus:ring-green-200 focus:border-green-500 transition-all duration-300 font-medium',
                'placeholder': 'Titre du sujet'
            })
        }


class PostForm(forms.ModelForm):
    """Form for creating a new post."""
    class Meta:
        model = Post
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:ring-4 focus:ring-green-200 focus:border-green-500 transition-all duration-300 font-medium',
                'placeholder': 'Votre message (Markdown supporté)',
                'rows': 8
            })
        }
        labels = {
            'content': 'Message'
        }
