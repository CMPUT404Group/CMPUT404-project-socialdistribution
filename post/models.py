from django.db import models
from django.utils import timezone

# Create your models here.
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
    author = models.ForeignKey('auth.User')
    content_type = models.CharField(max_length=2, choices=TYPE_CHOICES, default='TX')
    pub_date = models.DateTimeField(default=timezone.now)
    privilege = models.CharField(max_length=2, choices=PRIVILEGE_CHOICES, default='PB')
    title = models.CharField(max_length=200)
    post_text = models.TextField(blank=True)
    # image url, only available when content_type == img
    img_url = models.CharField(max_length=200, blank=True)
    # another author who are able to see this post
    # only available when privilege == 'AA'
    recipient = models.ForeignKey('auth.User', related_name='recipient', blank=True)

    # python2: __unicode__()
    # python3: __str__()
    def __unicode__(self):
        return self.title
