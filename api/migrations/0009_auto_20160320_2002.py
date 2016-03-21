# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_author_previous_follower_num'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='friending',
            unique_together=set([('author', 'friend')]),
        ),
    ]
