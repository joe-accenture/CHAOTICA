# Generated by Django 5.0.6 on 2024-08-27 19:09

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("jobtracker", "0014_alter_historicalorganisationalunit_lead_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="client",
            name="onboarded_users",
            field=models.ManyToManyField(
                blank=True,
                help_text="Users who have been onboarded",
                related_name="onboarded_to",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Onboarded Users",
            ),
        ),
        migrations.AddField(
            model_name="client",
            name="onboarding_required",
            field=models.BooleanField(
                default=False,
                help_text="If enabled, only onboarded users can be scheduled on jobs for this client.",
            ),
        ),
        migrations.AddField(
            model_name="historicalclient",
            name="onboarding_required",
            field=models.BooleanField(
                default=False,
                help_text="If enabled, only onboarded users can be scheduled on jobs for this client.",
            ),
        ),
    ]