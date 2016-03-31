from django import forms
from api.models import Post, Comment
from django.contrib.auth.models import User

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'content', 
                  'published', 'author', 'other_author', 
                  'visibility', 'contentType', 'image')
        exclude = ['published', 'author']
        widgets = {
            'visibility': forms.RadioSelect,
            'contentType': forms.RadioSelect,
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('comment', 'contentType', 'published', 'author')
        exclude = ['published', 'author']
        widgets = {
            'contentType': forms.RadioSelect,
        }
