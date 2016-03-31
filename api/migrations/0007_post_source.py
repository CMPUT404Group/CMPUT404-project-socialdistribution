# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_author_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='source',
            field=models.CharField(default=b'http://127.0.0.1:8000/', max_length=100),
        ),
    ]
