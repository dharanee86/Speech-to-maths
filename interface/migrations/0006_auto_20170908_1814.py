# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-09-08 16:14
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('interface', '0005_auto_20170908_1749'),
    ]

    operations = [
        migrations.RenameField(
            model_name='document',
            old_name='auteur',
            new_name='author',
        ),
        migrations.RenameField(
            model_name='document',
            old_name='contenu',
            new_name='content',
        ),
        migrations.RenameField(
            model_name='document',
            old_name='date_creation',
            new_name='creation_date',
        ),
        migrations.RenameField(
            model_name='document',
            old_name='date_derniere_modification',
            new_name='last_modification_date',
        ),
        migrations.RenameField(
            model_name='document',
            old_name='titre',
            new_name='title',
        ),
    ]