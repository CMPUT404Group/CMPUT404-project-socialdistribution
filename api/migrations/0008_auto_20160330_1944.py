# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_post_source'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='source',
            field=models.CharField(default=b'http://cmput404-team-4b.herokuapp.com/', max_length=100),
        ),
    ]
