# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_auto_20160330_1408'),
    ]

    operations = [
        migrations.AlterField(
            model_name='author',
            name='host',
            field=models.CharField(default=b'http://127.0.0.1:8000/', max_length=100),
        ),
    ]
