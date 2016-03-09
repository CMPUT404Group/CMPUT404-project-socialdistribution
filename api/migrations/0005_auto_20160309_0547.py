# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_auto_20160309_0030'),
    ]

    operations = [
        migrations.AlterField(
            model_name='author',
            name='status',
            field=models.CharField(default=b'W', max_length=1, choices=[(b'W', b'Waiting for approval'), (b'P', b'Passed')]),
        ),
    ]
