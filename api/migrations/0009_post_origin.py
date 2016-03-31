# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_auto_20160330_1944'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='origin',
            field=models.CharField(default=b'http://cmput404-team-4b.herokuapp.com/', max_length=100),
        ),
    ]
