# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='friend',
            name='friend',
        ),
        migrations.RemoveField(
            model_name='friend',
            name='user',
        ),
        migrations.DeleteModel(
            name='Friend',
        ),
    ]
