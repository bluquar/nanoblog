# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nanoblog', '0006_auto_20150218_0007'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='blogger',
            name='content_type',
        ),
        migrations.RemoveField(
            model_name='blogger',
            name='profile_picture',
        ),
        migrations.AddField(
            model_name='blogger',
            name='profile_picture_url',
            field=models.CharField(max_length=256, null=True),
            preserve_default=True,
        ),
    ]
