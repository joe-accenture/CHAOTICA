# Generated by Django 5.0.3 on 2024-03-22 22:27

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("jobtracker", "0027_organisationalunitrole_bs_colour_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="organisationalunitrole",
            options={"ordering": ["name"]},
        ),
        migrations.AddField(
            model_name="historicalorganisationalunitrole",
            name="default_role",
            field=models.BooleanField(default=False, verbose_name="Default Role"),
        ),
        migrations.AddField(
            model_name="historicalorganisationalunitrole",
            name="manage_role",
            field=models.BooleanField(default=False, verbose_name="Manager Role"),
        ),
        migrations.AddField(
            model_name="organisationalunitrole",
            name="default_role",
            field=models.BooleanField(default=False, verbose_name="Default Role"),
        ),
        migrations.AddField(
            model_name="organisationalunitrole",
            name="manage_role",
            field=models.BooleanField(default=False, verbose_name="Manager Role"),
        ),
    ]
