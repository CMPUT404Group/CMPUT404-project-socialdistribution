# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0009_auto_20160320_2002'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='friending',
            unique_together=set([]),
        ),
    ]
