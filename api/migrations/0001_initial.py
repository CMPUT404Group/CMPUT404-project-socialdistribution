# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Author',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('github_name', models.CharField(max_length=40, blank=True)),
                ('picture', models.ImageField(null=True, upload_to=b'profile_images/', blank=True)),
                ('host', models.CharField(default=b'http://127.0.0.1:8000/', max_length=40)),
                ('displayname', models.CharField(default=b'defaultUsername', max_length=40)),
                ('previous_follower_num', models.PositiveIntegerField(default=0)),
                ('noti', models.BooleanField(default=False)),
                ('user', models.OneToOneField(null=True, blank=True, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('comment', models.TextField()),
                ('contentType', models.CharField(default=b'text/plain', max_length=15, choices=[(b'text/x-markdown', b'Markdown'), (b'text/plain', b'Plaintext')])),
                ('published', models.DateTimeField(default=django.utils.timezone.now)),
                ('author', models.ForeignKey(to='api.Author')),
            ],
        ),
        migrations.CreateModel(
            name='Friending',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('author', models.ForeignKey(to='api.Author')),
                ('friend', models.ForeignKey(related_name='friend', to='api.Author')),
            ],
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('photo', models.ImageField(upload_to=b'images/', verbose_name=b'Image')),
                ('upload_date', models.DateTimeField(auto_now_add=True)),
                ('author', models.ForeignKey(to='api.Author')),
            ],
        ),
        migrations.CreateModel(
            name='Node',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('hostname', models.CharField(max_length=40)),
                ('url', models.CharField(max_length=200)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('title', models.CharField(max_length=200)),
                ('contentType', models.CharField(default=b'text/plain', max_length=15, choices=[(b'text/x-markdown', b'Markdown'), (b'text/plain', b'Plaintext')])),
                ('content', models.TextField()),
                ('published', models.DateTimeField(default=django.utils.timezone.now)),
                ('visibility', models.CharField(default=b'FRIENDS', max_length=18, choices=[(b'PUBLIC', b'Public'), (b'FOAF', b'Friends of Friends'), (b'FRIENDS', b'Friends'), (b'PRIVATE', b'Only Me'), (b'SERVERONLY', b'Only Server'), (b'OTHERAUTHOR', b'Other Author')])),
                ('image_url', models.CharField(max_length=200, null=True, blank=True)),
                ('other_author', models.CharField(max_length=30, null=True, blank=True)),
                ('author', models.ForeignKey(to='api.Author')),
            ],
        ),
        migrations.AddField(
            model_name='comment',
            name='post',
            field=models.ForeignKey(related_name='comments', to='api.Post'),
        ),
    ]
