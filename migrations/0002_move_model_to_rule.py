# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('rules_engine', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='condition',
            name='model',
        ),
        migrations.AddField(
            model_name='rule',
            name='model',
            field=models.ForeignKey(related_name='rule_conditions', default=27, to='contenttypes.ContentType'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='condition',
            name='operator',
            field=models.CharField(default=b'==', max_length=12, choices=[(b'>', b'GREATER THAN'), (b'<', b'LESSER THAN'), (b'==', b'EQUALS')]),
        ),
    ]
