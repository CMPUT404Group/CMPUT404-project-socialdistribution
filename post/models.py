from django.db import models
from django.utils import timezone

# Create your models here.
class Post(models.Model):
	MARKDOWN = 'MD'
	PLAINTEXT = 'PT'
	STYLE_CHOICES = (
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
	text = models.TextField()
	date = models.DateTimeField(default=timezone.now)
	style = models.CharField(max_length=2, choices=STYLE_CHOICES, default=PLAINTEXT)
	privacy = models.CharField(max_length=2, choices=PRIVACY_SETTING_CHOICES, default=FRIENDS)
	
	def __str__(self):
		return self.title