# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Author',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('github_name', models.CharField(max_length=40)),
                ('status', models.CharField(default=b'W', max_length=1, choices=[(b'W', b'Waiting for approve'), (b'P', b'Passed')])),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterField(
            model_name='comment',
            name='author',
            field=models.ForeignKey(to='api.Author'),
        ),
        migrations.AlterField(
            model_name='post',
            name='author',
            field=models.ForeignKey(to='api.Author'),
        ),
    ]
