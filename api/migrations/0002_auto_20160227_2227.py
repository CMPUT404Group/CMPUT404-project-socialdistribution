# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='post',
            old_name='publish_date',
            new_name='published',
        ),
        migrations.RemoveField(
            model_name='post',
            name='content_type',
        ),
        migrations.RemoveField(
            model_name='post',
            name='privilege',
        ),
        migrations.AddField(
            model_name='post',
            name='contentType',
            field=models.CharField(default=b'text/plain', max_length=15, choices=[(b'text/x-markdown', b'Markdown'), (b'text/plain', b'Plaintext')]),
        ),
        migrations.AddField(
            model_name='post',
            name='visibility',
            field=models.CharField(default=b'FRIENDS', max_length=18, choices=[(b'PUBLIC', b'Public'), (b'FOAF', b'Friends of Friends'), (b'FRIENDS', b'Friends'), (b'PRIVATE', b'Only Me'), (b'SERVERONLY', b'Only Server')]),
        ),
    ]
