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
            name='Comment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('comment', models.TextField()),
                ('contentType', models.CharField(default=b'text/plain', max_length=15, choices=[(b'text/x-markdown', b'Markdown'), (b'text/plain', b'Plaintext')])),
                ('published', models.DateTimeField(default=django.utils.timezone.now)),
                ('author', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=200)),
                ('contentType', models.CharField(default=b'text/plain', max_length=15, choices=[(b'text/x-markdown', b'Markdown'), (b'text/plain', b'Plaintext')])),
                ('content', models.TextField()),
                ('published', models.DateTimeField(default=django.utils.timezone.now)),
                ('visibility', models.CharField(default=b'FRIENDS', max_length=18, choices=[(b'PUBLIC', b'Public'), (b'FOAF', b'Friends of Friends'), (b'FRIENDS', b'Friends'), (b'PRIVATE', b'Only Me'), (b'SERVERONLY', b'Only Server')])),
                ('author', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='comment',
            name='post',
            field=models.ForeignKey(related_name='comments', to='api.Post'),
        ),
    ]
