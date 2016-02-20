from django import forms
from api.models import Post
from django.contrib.auth.models import User

class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ('title', 'content', 'publish_date', 'author', 'privilege', 'content_type')
        exclude = ['publish_date', 'author']
        widgets = {
        	'privilege': forms.RadioSelect,
        	'content_type': forms.RadioSelect,
        }