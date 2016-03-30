from django.contrib.auth.models import User
from django import forms
from api.models import Author

class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ('github', 'picture', 'displayName')
