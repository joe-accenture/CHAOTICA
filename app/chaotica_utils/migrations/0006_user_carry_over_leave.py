# Generated by Django 5.0.6 on 2024-08-22 21:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("chaotica_utils", "0005_user_notification_email"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="carry_over_leave",
            field=models.IntegerField(
                default=25, verbose_name="Days Leave Carried Over"
            ),
        ),
    ]
