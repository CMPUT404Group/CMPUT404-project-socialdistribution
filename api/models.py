from django.db import models
from django.utils import timezone

# Create your models here.
MARKDOWN = 'text/x-markdown'
PLAINTEXT = 'text/plain'
CONTENT_TYPE_CHOICES = (
	(MARKDOWN, 'Markdown'),
	(PLAINTEXT, 'Plaintext')
)

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
	title = models.CharField(max_length=200)
	# source - where did you get this post from? - ex http://lastplaceigotthisfrom.com/post/yyyyy
	# origin - where it is actually from - ex http://whereitcamefrom.com/post/zzzzz
	# description - a brief description of the post
	contentType = models.CharField(max_length=15, choices=CONTENT_TYPE_CHOICES, default=PLAINTEXT)
	content = models.TextField()	
	author = models.ForeignKey('auth.User')
	# categories - categories this posts fits into - a list of strings - ex ["web","tutorial"]
	# count - total # of comments for this post
	published = models.DateTimeField(default=timezone.now)
	visibility = models.CharField(max_length=18, choices=VISIBILITY_SETTING_CHOICES, default=FRIENDS)
	# comments = models.ForeignKey('api.Comment', related_name='post')


class Comment(models.Model):
	post = models.ForeignKey('api.Post', related_name='comments')

	author =  models.ForeignKey('auth.User')
	comment = models.TextField()
	contentType = models.CharField(max_length=15, choices=CONTENT_TYPE_CHOICES, default=PLAINTEXT)
	published = models.DateTimeField(default=timezone.now)

# for files like images (hopefully will work for posting images)
class Upload(models.Model):
    pic = models.ImageField("Image", upload_to="images/")    
    upload_date=models.DateTimeField(auto_now_add =True)
