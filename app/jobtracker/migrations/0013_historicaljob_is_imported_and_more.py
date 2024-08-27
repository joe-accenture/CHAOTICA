# Generated by Django 5.0.6 on 2024-08-27 13:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("jobtracker", "0012_alter_historicalphase_description_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="historicaljob",
            name="is_imported",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="historicalphase",
            name="is_imported",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="job",
            name="is_imported",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="phase",
            name="is_imported",
            field=models.BooleanField(default=False),
        ),
    ]
