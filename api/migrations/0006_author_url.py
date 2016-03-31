# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_auto_20160330_1830'),
    ]

    operations = [
        migrations.AddField(
            model_name='author',
            name='url',
            field=models.CharField(default=b'http://127.0.0.1:8000/', max_length=200),
        ),
    ]
