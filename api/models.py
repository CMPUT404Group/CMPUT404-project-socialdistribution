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
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    github_name = models.CharField(max_length=40, blank=True)
    picture = models.ImageField(upload_to='profile_images/', blank=True)
    host = models.CharField(max_length=40, default="http://127.0.0.1:8080/")

    def __unicode__(self):
        return self.user.username


class Post(models.Model):
    PUBLIC = 'PUBLIC'
    FRIENDS_OF_FRIENDS = 'FOAF'
    FRIENDS = 'FRIENDS'
    ME_ONLY = 'PRIVATE'
    SERVER_ONLY = "SERVERONLY"

    VISIBILITY_SETTING_CHOICES = (
        (PUBLIC, 'Public'),
        (FRIENDS_OF_FRIENDS, 'Friends of Friends'),
        (FRIENDS, 'Friends'),
        (ME_ONLY, 'Only Me'),
        (SERVER_ONLY, "Only Server")
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


class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey('api.Post', related_name='comments')

    author = models.ForeignKey('Author')
    comment = models.TextField()
    contentType = models.CharField(max_length=15, choices=CONTENT_TYPE_CHOICES, default=PLAINTEXT)
    published = models.DateTimeField(default=timezone.now)


# for files like images (hopefully will work for posting images)
class Upload(models.Model):
    pic = models.ImageField("Image", upload_to="images/")
    upload_date = models.DateTimeField(auto_now_add=True)


class Image(models.Model):
    photo = models.ImageField("Image", upload_to="images/")
    upload_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey('Author')
    
class Friending(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    friend = models.ForeignKey(Author, related_name='friend', on_delete=models.CASCADE)

class Following(models.Model):
    author = models.ForeignKey(Author, related_name='follow_author', on_delete=models.CASCADE)
    following = models.ForeignKey(Author, related_name='follow_following', on_delete=models.CASCADE)
