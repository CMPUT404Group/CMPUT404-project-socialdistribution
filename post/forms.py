from django import forms
from api.models import Post, Comment, Upload
from django.contrib.auth.models import User

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'content', 
                  'published', 'author', 'other_author', 
                  'visibility', 'contentType', 'image_url')
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

# FileUpload form class.
class UploadFileForm(forms.ModelForm):
    class Meta:
        model = Upload
        fields = "__all__"
