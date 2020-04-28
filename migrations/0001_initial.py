# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import concurrency.fields
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Condition',
            fields=[
                ('version', concurrency.fields.IntegerVersionField(default=1, help_text='record revision number')),
                ('id', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True, db_index=True)),
                ('type', models.CharField(default=b'And', max_length=12, choices=[(b'And', b'AND'), (b'Or', b'OR')])),
                ('field', models.CharField(max_length=64)),
                ('value', models.CharField(max_length=128)),
                ('content_type', models.CharField(default=b'String', max_length=32, choices=[(b'String', b'String'), (b'Number', b'Number'), (b'Boolean', b'Boolean'), (b'Date', b'Date')])),
                ('operator', models.CharField(default=b'==', max_length=12, choices=[(b'>', b'AND'), (b'<', b'AND'), (b'==', b'OR')])),
                ('model', models.ForeignKey(related_name='rule_conditions', to='contenttypes.ContentType')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Rule',
            fields=[
                ('version', concurrency.fields.IntegerVersionField(default=1, help_text='record revision number')),
                ('id', models.UUIDField(default=uuid.uuid4, serialize=False, editable=False, primary_key=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True, db_index=True)),
                ('name', models.CharField(max_length=64)),
                ('tag', models.CharField(max_length=64, null=True, blank=True)),
                ('halt', models.BooleanField(default=False, verbose_name=b'Stop Further Rules')),
                ('is_active', models.BooleanField(default=True)),
                ('priority', models.IntegerField(default=1)),
                ('expiration', models.DateField(null=True, blank=True)),
                ('action', models.CharField(max_length=64, null=True, blank=True)),
                ('action_args', models.CharField(max_length=128, null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='condition',
            name='rule',
            field=models.ForeignKey(related_name='conditions', to='rules_engine.Rule'),
        ),
    ]
