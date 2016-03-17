# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_auto_20160316_1532'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='other_author',
            field=models.CharField(max_length=30, null=True, blank=True),
        ),
    ]
