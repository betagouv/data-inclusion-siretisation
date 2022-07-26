# Generated by Django 4.0.6 on 2022-07-26 16:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("annotation", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="annotation",
            name="closed",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="annotation",
            name="irrelevant",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="annotation",
            name="is_parent",
            field=models.BooleanField(default=False),
        ),
    ]
