# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_remove_author_noti'),
    ]

    operations = [
        migrations.AddField(
            model_name='author',
            name='noti',
            field=models.BooleanField(default=False),
        ),
    ]
