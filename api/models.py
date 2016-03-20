from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import uuid

# Create your models here.
MARKDOWN = 'text/x-markdown'
PLAINTEXT = 'text/plain'
CONTENT_TYPE_CHOICES = (
    (MARKDOWN, 'Markdown'),
    (PLAINTEXT, 'Plaintext')
)

# Why having additional Authors class instead of auth.user:
# auth.user is the model comes with Django, we need more attributes for Authors.
# create Author model with a one-to-one association with the the `User` model
class Author(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
    github_name = models.CharField(max_length=40, blank=True)
    picture = models.ImageField(upload_to='profile_images/', blank=True)
    host = models.CharField(max_length=40, default="http://127.0.0.1:8080/")
    displayname = models.CharField(max_length=40, default="defaultUsername")

    def __unicode__(self):
        # return self.user.username
        return self.displayname

class Node(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    hostname = models.CharField(max_length=40)
    url = models.CharField(max_length=200)

    def __unicode__(self):
        return self.hostname

class Post(models.Model):
    PUBLIC = 'PUBLIC'
    FRIENDS_OF_FRIENDS = 'FOAF'
    FRIENDS = 'FRIENDS'
    ME_ONLY = 'PRIVATE'
    SERVER_ONLY = 'SERVERONLY'
    OTHER_AUTHOR = 'OTHERAUTHOR'

    VISIBILITY_SETTING_CHOICES = (
        (PUBLIC, 'Public'),
        (FRIENDS_OF_FRIENDS, 'Friends of Friends'),
        (FRIENDS, 'Friends'),
        (ME_ONLY, 'Only Me'),
        (SERVER_ONLY, 'Only Server'),
        (OTHER_AUTHOR, 'Other Author')
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    # source - where did you get this post from? - ex http://lastplaceigotthisfrom.com/post/yyyyy
    # origin - where it is actually from - ex http://whereitcamefrom.com/post/zzzzz
    # description - a brief description of the post
    contentType = models.CharField(max_length=15, choices=CONTENT_TYPE_CHOICES, default=PLAINTEXT)
    content = models.TextField()
    author = models.ForeignKey('Author')
    # categories - categories this posts fits into - a list of strings - ex ["web","tutorial"]
    # count - total # of comments for this post
    published = models.DateTimeField(default=timezone.now)
    visibility = models.CharField(max_length=18, choices=VISIBILITY_SETTING_CHOICES, default=FRIENDS)
    # comments = models.ForeignKey('api.Comment', related_name='post')
    image_url = models.CharField(max_length=200, blank=True, null=True)
    other_author = models.CharField(max_length=30,blank=True,null=True)


class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey('Post', related_name='comments', on_delete=models.CASCADE)

    author = models.ForeignKey('Author')
    comment = models.TextField()
    contentType = models.CharField(max_length=15, choices=CONTENT_TYPE_CHOICES, default=PLAINTEXT)
    published = models.DateTimeField(default=timezone.now)

class Image(models.Model):
    photo = models.ImageField("Image", upload_to="images/")
    upload_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey('Author')

# we are only using friending model
# when you friend someone, you follow him
# when he follows back, you guys become friends
# A friends B: A follows B
# B friends A: B follows A
# A and B mutually followed each other, they are considered and friends.  
class Friending(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    friend = models.ForeignKey(Author, related_name='friend', on_delete=models.CASCADE)
