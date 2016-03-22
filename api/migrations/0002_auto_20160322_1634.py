# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='author',
            name='github_name',
        ),
        migrations.AddField(
            model_name='author',
            name='github',
            field=models.CharField(default=b'http://github.com/defunkt', max_length=40, blank=True),
        ),
    ]
