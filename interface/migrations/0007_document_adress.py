# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-09-25 19:29
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('interface', '0006_auto_20170908_1814'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='adress',
            field=models.UUIDField(default=uuid.uuid4, editable=False),
        ),
    ]