# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nanoblog', '0004_auto_20150212_2041'),
    ]

    operations = [
        migrations.AddField(
            model_name='blogger',
            name='content_type',
            field=models.CharField(default='jpeg', max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='blogger',
            name='profile_picture',
            field=models.FileField(upload_to=b'pictures', blank=True),
            preserve_default=True,
        ),
    ]
