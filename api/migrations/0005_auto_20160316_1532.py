# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_auto_20160315_1636'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='other_author',
            field=models.ForeignKey(related_name='Share_with_user', blank=True, to='api.Author', null=True),
        ),
        migrations.AlterField(
            model_name='post',
            name='visibility',
            field=models.CharField(default=b'FRIENDS', max_length=18, choices=[(b'PUBLIC', b'Public'), (b'FOAF', b'Friends of Friends'), (b'FRIENDS', b'Friends'), (b'PRIVATE', b'Only Me'), (b'SERVERONLY', b'Only Server'), (b'OTHERAUTHOR', b'Other Author')]),
        ),
    ]
