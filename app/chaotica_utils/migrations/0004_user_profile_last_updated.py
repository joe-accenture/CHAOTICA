# Generated by Django 4.2.2 on 2024-02-07 16:14

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("chaotica_utils", "0003_alter_user_contracted_leave"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="profile_last_updated",
            field=models.DateField(auto_now=True, verbose_name="Profile Last Updated"),
        ),
    ]
