from django import forms
from api.models import Post
from django.contrib.auth.models import User

class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ('title', 'content', 'date', 'author', 'privilege', 'content_type')
        exclude = ['author']

    # def __init__(self, *args, **kwargs):
    # 	self.author = kwargs.pop('author', '')
    # 	super(PostForm, self).__init__(*args, **kwargs)