from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.forms import ModelForm

# Create your models here.
# temporarily put all the model in one place
# we can separate them into different apps later on

# Why having additional Author class instead of Auth.user:
# Auth.user is the model comes with Django, we have to add some fields to make it an author.

'''
class Author(models.Model):
    STATUS_CHOICES = (
        ('W', 'Waiting for approve'),
        ('P', 'Passed')
    )

    author = models.OneToOneField(User, on_delete=models.CASCADE)
    github_name = models.CharField(max_length=40)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='W')

    def __unicode__(self):
        return self.author.username

class Post(models.Model):
    TYPE_CHOICES = (
        ('MK', 'Markdown'),
        ('TX', 'Plaintext'),
        ('MG', 'Image Link'),
        ('GT', 'Github Activity')
    )

    PRIVILEGE_CHOICES = (
        ('ME', 'Me'),
        ('AA', 'Another Author'),
        ('FR', 'Friends'),
        ('FF', 'Friends of Friends'),
        ('LF', 'Local Friends'),
        ('PB', 'Public')
    )

    post_id = models.AutoField(primary_key=True, unique=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    content_type = models.CharField(max_length=2, choices=TYPE_CHOICES, default='TX')
    pub_date = models.DateTimeField(default=timezone.now)
    privilege = models.CharField(max_length=2, choices=PRIVILEGE_CHOICES, default='PB')
    title = models.CharField(max_length=200)
    post_text = models.TextField(blank=True)
    # image url, only available when content_type == img
    img_url = models.CharField(max_length=200, blank=True)
    # another author who are able to see this post
    # only available when privilege == 'AA'
    recipient = models.ForeignKey(Author, related_name='recipient', blank=True, on_delete=models.CASCADE)

    # python2: __unicode__()
    # python3: __str__()
    def __unicode__(self):
        return self.title


# for files like images (hopefully will work for posting images)
class Upload(models.Model):
    pic = models.ImageField("Image", upload_to="images/")    
    upload_date=models.DateTimeField(auto_now_add =True)

class Comment(models.Model):
    comment_id = models.AutoField(primary_key=True, unique=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    text = models.TextField()
    pub_date = models.DateTimeField(default=timezone.now)

class Node(models.Model):
    node_name = models. CharField(max_length=40, primary_key=True, unique=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)

class Friending(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    friend = models.ForeignKey(Author, related_name='friend', on_delete=models.CASCADE)

class Following(models.Model):
    author = models.ForeignKey(Author, related_name='follow_author', on_delete=models.CASCADE)
    following = models.ForeignKey(Author, related_name='follow_following', on_delete=models.CASCADE)
'''
