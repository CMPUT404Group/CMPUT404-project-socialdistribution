from django.db import models
from django.utils import timezone

# Create your models here.
class Post(models.Model):
	MARKDOWN = 'MD'
	PLAINTEXT = 'PT'
	CONTENT_TYPE_CHOICES = (
		(MARKDOWN, 'Markdown'),
		(PLAINTEXT, 'Plaintext')
	)

	ONLY_ME = 'ME'
	FRIENDS = 'FR'
	FRIENDS_OF_FRIENDS = 'FF'
	PUBLIC = 'PB'
	# some more missing here

	PRIVACY_SETTING_CHOICES = (
		(ONLY_ME, 'Me'),
		(FRIENDS, 'Friends'),
		(FRIENDS_OF_FRIENDS, 'Friends of Friends'),
		(PUBLIC, 'Public')
		# some more missing here
	)
	author = models.ForeignKey('auth.User')
	title = models.CharField(max_length=200)
	content = models.TextField()
	date = models.DateTimeField(default=timezone.now)
	content_type = models.CharField(max_length=2, choices=CONTENT_TYPE_CHOICES, default=PLAINTEXT)
	privilege = models.CharField(max_length=2, choices=PRIVACY_SETTING_CHOICES, default=FRIENDS)
	