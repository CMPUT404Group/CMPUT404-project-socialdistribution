from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.forms import ModelForm
from api.models import Author

# Create your models here.
class Notification(models.Model):
    notificatee = models.ForeignKey(Author, related_name='noti_author', on_delete=models.CASCADE)
    follower = models.ForeignKey(Author, related_name='noti_follower', on_delete=models.CASCADE)

