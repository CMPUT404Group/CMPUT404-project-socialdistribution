# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_auto_20160309_0030'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='author',
            name='status',
        ),
    ]
