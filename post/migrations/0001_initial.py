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
            name='Post',
            fields=[
                ('post_id', models.AutoField(unique=True, serialize=False, primary_key=True)),
                ('content_type', models.CharField(default=b'TX', max_length=2, choices=[(b'MK', b'Markdown'), (b'TX', b'Plaintext'), (b'MG', b'Image Link'), (b'GT', b'Github Activity')])),
                ('pub_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('privilege', models.CharField(default=b'PB', max_length=2, choices=[(b'ME', b'Me'), (b'AA', b'Another Author'), (b'FR', b'Friends'), (b'FF', b'Friends of Friends'), (b'LF', b'Local Friends'), (b'PB', b'Public')])),
                ('title', models.CharField(max_length=200)),
                ('post_text', models.TextField(blank=True)),
                ('img_url', models.CharField(max_length=200, blank=True)),
                ('author', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('recipient', models.ForeignKey(related_name='recipient', blank=True, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
