# Generated by Django 5.0.3 on 2024-03-13 16:49

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("jobtracker", "0010_frameworkagreement"),
    ]

    operations = [
        migrations.AddField(
            model_name="frameworkagreement",
            name="closed",
            field=models.BooleanField(default=False, verbose_name="Closed"),
        ),
    ]
