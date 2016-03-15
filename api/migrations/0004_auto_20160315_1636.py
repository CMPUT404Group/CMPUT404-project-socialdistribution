# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_notification'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='following',
            name='author',
        ),
        migrations.RemoveField(
            model_name='following',
            name='following',
        ),
        migrations.RemoveField(
            model_name='notification',
            name='follower',
        ),
        migrations.RemoveField(
            model_name='notification',
            name='notificatee',
        ),
        migrations.DeleteModel(
            name='Following',
        ),
        migrations.DeleteModel(
            name='Notification',
        ),
    ]
