from django import forms
from api.models import Post
from django.contrib.auth.models import User

class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ('title', 'content', 'published', 'author', 'visibility', 'contentType')
        exclude = ['published', 'author']
        widgets = {
        	'visibility': forms.RadioSelect,
        	'contentType': forms.RadioSelect,
        }