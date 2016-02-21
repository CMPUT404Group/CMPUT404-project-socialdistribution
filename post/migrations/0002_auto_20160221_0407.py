# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('post', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Author',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('github_name', models.CharField(max_length=40)),
                ('status', models.CharField(default=b'W', max_length=1, choices=[(b'W', b'Waiting for approve'), (b'P', b'Passed')])),
                ('author', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
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
            name='Commenting',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('comment', models.ForeignKey(to='post.Comment')),
            ],
        ),
        migrations.CreateModel(
            name='Follwing',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('author', models.ForeignKey(to='post.Author')),
                ('following', models.ForeignKey(related_name='following', to='post.Author')),
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
        migrations.AlterField(
            model_name='post',
            name='author',
            field=models.ForeignKey(to='post.Author'),
        ),
        migrations.AlterField(
            model_name='post',
            name='recipient',
            field=models.ForeignKey(related_name='recipient', blank=True, to='post.Author'),
        ),
        migrations.AddField(
            model_name='commenting',
            name='post',
            field=models.ForeignKey(to='post.Post'),
        ),
    ]
