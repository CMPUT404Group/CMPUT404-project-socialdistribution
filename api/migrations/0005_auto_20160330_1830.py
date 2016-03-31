# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_auto_20160330_1708'),
    ]

    operations = [
        migrations.RenameField(
            model_name='post',
            old_name='image_url',
            new_name='image',
        ),
    ]
