from django.contrib.auth.models import User
from django import forms
from api.models import Author


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ('github_name', 'picture')
