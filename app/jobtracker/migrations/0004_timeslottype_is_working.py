# Generated by Django 4.2.2 on 2023-10-24 19:27

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("jobtracker", "0003_timeslottype_timeslot_slot_type"),
    ]

    operations = [
        migrations.AddField(
            model_name="timeslottype",
            name="is_working",
            field=models.BooleanField(default=False, verbose_name="Is working"),
        ),
    ]
