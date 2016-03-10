# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Author',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('github_name', models.CharField(max_length=40)),
                ('status', models.CharField(default=b'W', max_length=1, choices=[(b'W', b'Waiting for approve'), (b'P', b'Passed')])),
                ('author', models.OneToOneField(related_name='post_author', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('comment_id', models.AutoField(unique=True, serialize=False, primary_key=True)),
                ('text', models.TextField()),
                ('pub_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('author', models.ForeignKey(to='post.Author')),
            ],
        ),
        migrations.CreateModel(
            name='Following',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('author', models.ForeignKey(related_name='follow_author', to='post.Author')),
                ('following', models.ForeignKey(related_name='follow_following', to='post.Author')),
            ],
        ),
        migrations.CreateModel(
            name='Friending',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('author', models.ForeignKey(to='post.Author')),
                ('friend', models.ForeignKey(related_name='friend', to='post.Author')),
            ],
        ),
        migrations.CreateModel(
            name='Node',
            fields=[
                ('node_name', models.CharField(max_length=40, unique=True, serialize=False, primary_key=True)),
                ('author', models.ForeignKey(to='post.Author')),
            ],
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('post_id', models.AutoField(unique=True, serialize=False, primary_key=True)),
                ('content_type', models.CharField(default=b'TX', max_length=2, choices=[(b'MK', b'Markdown'), (b'TX', b'Plaintext'), (b'MG', b'Image Link'), (b'GT', b'Github Activity')])),
                ('pub_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('privilege', models.CharField(default=b'PB', max_length=2, choices=[(b'ME', b'Me'), (b'AA', b'Another Author'), (b'FR', b'Friends'), (b'FF', b'Friends of Friends'), (b'LF', b'Local Friends'), (b'PB', b'Public')])),
                ('title', models.CharField(max_length=200)),
                ('post_text', models.TextField(blank=True)),
                ('img_url', models.CharField(max_length=200, blank=True)),
                ('author', models.ForeignKey(to='post.Author')),
                ('recipient', models.ForeignKey(related_name='recipient', blank=True, to='post.Author')),
            ],
        ),
        migrations.CreateModel(
            name='Upload',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('pic', models.ImageField(upload_to=b'images/', verbose_name=b'Image')),
                ('upload_date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
