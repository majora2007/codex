"""Generated by Django 3.2.9 on 2021-12-06 00:59."""

import django.db.models.deletion

from django.db import migrations, models


class Migration(migrations.Migration):
    """Make sort_name only descend from BrowserGroup."""

    dependencies = [
        ("codex", "0011_alter_comic_unique_together"),
    ]

    operations = [
        migrations.AddField(
            model_name="failedimport",
            name="parent_folder",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="codex.folder",
            ),
        ),
        migrations.AddField(
            model_name="failedimport",
            name="stat",
            field=models.JSONField(null=True),
        ),
        migrations.AlterField(
            model_name="comic",
            name="sort_name",
            field=models.CharField(db_index=True, default="", max_length=32),
        ),
        migrations.AlterField(
            model_name="folder",
            name="sort_name",
            field=models.CharField(db_index=True, default="", max_length=32),
        ),
        migrations.AlterField(
            model_name="imprint",
            name="sort_name",
            field=models.CharField(db_index=True, default="", max_length=32),
        ),
        migrations.AlterField(
            model_name="publisher",
            name="sort_name",
            field=models.CharField(db_index=True, default="", max_length=32),
        ),
        migrations.AlterField(
            model_name="series",
            name="sort_name",
            field=models.CharField(db_index=True, default="", max_length=32),
        ),
        migrations.AlterField(
            model_name="volume",
            name="sort_name",
            field=models.CharField(db_index=True, default="", max_length=32),
        ),
    ]
