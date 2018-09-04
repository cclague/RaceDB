# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2018-07-25 22:59
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0085_auto_20180725_1813'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wavett',
            name='sequence_option',
            field=models.PositiveSmallIntegerField(choices=[('Increasing', ((0, 'Est. Speed - Increasing'), (1, 'Youngest to Oldest'), (2, 'Bib - Increasing'))), ('Decreasing', ((3, 'Oldest to Youngest'), (4, 'Bib - Decreasing'))), ('Series', ((5, 'Series Rank'),))], default=0, help_text=b'Criteria used to order participants in the wave', verbose_name='Sequence Option'),
        ),
        migrations.AlterField(
            model_name='wavett',
            name='series_for_seeding',
            field=models.ForeignKey(blank=True, help_text='Must be specified if Sequence Option is Series', null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.Series', verbose_name='Series for Seeding'),
        ),
    ]