# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=200)),
                ('text', models.TextField()),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('style', models.CharField(default=b'PT', max_length=2, choices=[(b'MD', b'Markdown'), (b'PT', b'Plaintext')])),
                ('privacy', models.CharField(default=b'FR', max_length=2, choices=[(b'ME', b'Me'), (b'FR', b'Friends'), (b'FF', b'Friends of Friends'), (b'PB', b'Public')])),
            ],
        ),
    ]
