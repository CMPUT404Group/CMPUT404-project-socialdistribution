# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_node'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Upload',
        ),
        migrations.AlterField(
            model_name='author',
            name='host',
            field=models.CharField(default=b'http://127.0.0.1:8000/', max_length=40),
        ),
        migrations.AlterField(
            model_name='author',
            name='picture',
            field=models.ImageField(null=True, upload_to=b'profile_images/', blank=True),
        ),
    ]
