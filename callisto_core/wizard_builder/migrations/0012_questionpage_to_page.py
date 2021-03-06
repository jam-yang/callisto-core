# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-02 22:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("sites", "0002_alter_domain_unique"),
        ("wizard_builder", "0011_rename_questionpage_attrs"),
    ]

    operations = [
        migrations.CreateModel(
            name="Page",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "position",
                    models.PositiveSmallIntegerField(
                        default=0, verbose_name="position"
                    ),
                ),
                (
                    "section",
                    models.IntegerField(
                        choices=[(1, "When"), (2, "Where"), (3, "What"), (4, "Who")],
                        default=1,
                    ),
                ),
                (
                    "infobox",
                    models.TextField(
                        blank=True,
                        verbose_name="why is this asked? wrap additional titles in [[double brackets]]",
                    ),
                ),
                ("sites", models.ManyToManyField(to="sites.Site")),
            ],
            options={"ordering": ["position"]},
        )
    ]
