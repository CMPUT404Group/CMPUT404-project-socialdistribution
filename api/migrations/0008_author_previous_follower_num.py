# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_author_noti'),
    ]

    operations = [
        migrations.AddField(
            model_name='author',
            name='previous_follower_num',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
