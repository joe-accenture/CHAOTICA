# Generated by Django 4.2.2 on 2023-10-24 19:37

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("jobtracker", "0004_timeslottype_is_working"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="timeslottype",
            name="type_id",
        ),
    ]
