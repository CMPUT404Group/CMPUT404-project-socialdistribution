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
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=200)),
                ('content', models.TextField()),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('content_type', models.CharField(default=b'PT', max_length=2, choices=[(b'MD', b'Markdown'), (b'PT', b'Plaintext')])),
                ('privilege', models.CharField(default=b'FR', max_length=2, choices=[(b'ME', b'Me'), (b'FR', b'Friends'), (b'FF', b'Friends of Friends'), (b'PB', b'Public')])),
                ('author', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
