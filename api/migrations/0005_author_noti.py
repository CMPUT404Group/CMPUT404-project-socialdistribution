# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_auto_20160320_1811'),
    ]

    operations = [
        migrations.AddField(
            model_name='author',
            name='noti',
            field=models.BooleanField(default=False),
        ),
    ]
