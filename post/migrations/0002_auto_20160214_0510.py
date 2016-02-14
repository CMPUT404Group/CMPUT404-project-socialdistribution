# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='privacy',
            field=models.CharField(default=(b'FR',), max_length=2, choices=[((b'ME',), b'Me'), ((b'FR',), b'Friends'), ((b'FF',), b'Friends of Friends'), ((b'PB',), b'Public')]),
        ),
        migrations.AddField(
            model_name='post',
            name='style',
            field=models.CharField(default=b'PT', max_length=2, choices=[(b'MD', b'Markdown'), (b'PT', b'Plaintext')]),
        ),
    ]
