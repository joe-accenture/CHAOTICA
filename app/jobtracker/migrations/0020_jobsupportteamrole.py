# Generated by Django 5.0.3 on 2024-03-20 14:41

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("jobtracker", "0019_billingcode_is_internal"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="JobSupportTeamRole",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "role",
                    models.IntegerField(
                        choices=[
                            (0, "Other"),
                            (1, "Commercial"),
                            (1, "QA"),
                            (2, "Scope"),
                        ],
                        default=0,
                        verbose_name="Role",
                    ),
                ),
                (
                    "allocated_hours",
                    models.FloatField(default=0.0, verbose_name="Allocated Hours"),
                ),
                (
                    "job",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="supporting_team",
                        to="jobtracker.job",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="job_support_roles",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
