# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('post', '0002_upload'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='author',
            name='author',
        ),
        migrations.RemoveField(
            model_name='comment',
            name='author',
        ),
        migrations.RemoveField(
            model_name='commenting',
            name='comment',
        ),
        migrations.RemoveField(
            model_name='commenting',
            name='post',
        ),
        migrations.RemoveField(
            model_name='follwing',
            name='author',
        ),
        migrations.RemoveField(
            model_name='follwing',
            name='following',
        ),
        migrations.RemoveField(
            model_name='friending',
            name='author',
        ),
        migrations.RemoveField(
            model_name='friending',
            name='friend',
        ),
        migrations.RemoveField(
            model_name='node',
            name='author',
        ),
        migrations.RemoveField(
            model_name='post',
            name='author',
        ),
        migrations.RemoveField(
            model_name='post',
            name='recipient',
        ),
        migrations.DeleteModel(
            name='Upload',
        ),
        migrations.DeleteModel(
            name='Author',
        ),
        migrations.DeleteModel(
            name='Comment',
        ),
        migrations.DeleteModel(
            name='Commenting',
        ),
        migrations.DeleteModel(
            name='Follwing',
        ),
        migrations.DeleteModel(
            name='Friending',
        ),
        migrations.DeleteModel(
            name='Node',
        ),
        migrations.DeleteModel(
            name='Post',
        ),
    ]
