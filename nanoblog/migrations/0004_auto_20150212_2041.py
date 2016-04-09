# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nanoblog', '0003_blogger'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blogger',
            name='age',
            field=models.IntegerField(null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='blogger',
            name='bio',
            field=models.CharField(max_length=430, null=True),
            preserve_default=True,
        ),
    ]
