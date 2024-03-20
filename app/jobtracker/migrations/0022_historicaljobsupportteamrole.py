# Generated by Django 5.0.3 on 2024-03-20 15:03

import django.db.models.deletion
import simple_history.models
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("jobtracker", "0021_jobsupportteamrole_billed_hours_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="HistoricalJobSupportTeamRole",
            fields=[
                (
                    "id",
                    models.BigIntegerField(
                        auto_created=True, blank=True, db_index=True, verbose_name="ID"
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
                    models.FloatField(
                        default=0.0,
                        help_text="Hours allocated to this person",
                        verbose_name="Allocated Hours",
                    ),
                ),
                (
                    "billed_hours",
                    models.FloatField(
                        default=0.0,
                        help_text="Hours actually billed from the allocated amount",
                        verbose_name="Billed Hours",
                    ),
                ),
                ("history_id", models.AutoField(primary_key=True, serialize=False)),
                ("history_date", models.DateTimeField(db_index=True)),
                ("history_change_reason", models.CharField(max_length=100, null=True)),
                (
                    "history_type",
                    models.CharField(
                        choices=[("+", "Created"), ("~", "Changed"), ("-", "Deleted")],
                        max_length=1,
                    ),
                ),
                (
                    "history_user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "job",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="jobtracker.job",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "historical job support team role",
                "verbose_name_plural": "historical job support team roles",
                "ordering": ("-history_date", "-history_id"),
                "get_latest_by": ("history_date", "history_id"),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
    ]
