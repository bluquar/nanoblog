# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('nanoblog', '0005_auto_20150213_2049'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.CharField(max_length=160)),
                ('datetime', models.DateTimeField(auto_now_add=True)),
                ('post', models.ForeignKey(to='nanoblog.BlogPost')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterField(
            model_name='blogger',
            name='age',
            field=models.PositiveIntegerField(null=True),
            preserve_default=True,
        ),
    ]
