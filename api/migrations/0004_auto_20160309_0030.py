# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_auto_20160308_1838'),
    ]

    operations = [
        migrations.AddField(
            model_name='author',
            name='picture',
            field=models.ImageField(upload_to=b'profile_images', blank=True),
        ),
        migrations.AlterField(
            model_name='author',
            name='github_name',
            field=models.CharField(max_length=40, blank=True),
        ),
    ]
