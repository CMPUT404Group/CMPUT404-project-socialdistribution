# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_auto_20160322_1634'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='author',
            name='displayname',
        ),
        migrations.AddField(
            model_name='author',
            name='displayName',
            field=models.CharField(default=b'defaultDisplayName', max_length=40),
        ),
        migrations.AlterField(
            model_name='author',
            name='github',
            field=models.CharField(default=b'http://github.com/default', max_length=40, blank=True),
        ),
    ]
