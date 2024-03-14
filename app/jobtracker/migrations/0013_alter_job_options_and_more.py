# Generated by Django 5.0.3 on 2024-03-14 15:44

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("jobtracker", "0012_alter_frameworkagreement_end_date"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="job",
            options={
                "ordering": ["id"],
                "permissions": (
                    ("add_note", "Can Add Note"),
                    ("scope_job", "Can Scope Job"),
                    ("view_schedule", "Can View Schedule"),
                    ("change_schedule", "Can Change Schedule"),
                    ("update_workflow", "Can Update the workflow"),
                    ("assign_poc", "Can assign Point of Contact"),
                    ("assign_framework", "Can assign a framework agreement"),
                ),
                "verbose_name": "Job",
            },
        ),
        migrations.RemoveField(
            model_name="frameworkagreement",
            name="associated_jobs",
        ),
        migrations.AddField(
            model_name="historicaljob",
            name="associated_framework",
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                to="jobtracker.frameworkagreement",
            ),
        ),
        migrations.AddField(
            model_name="job",
            name="associated_framework",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="associated_jobs",
                to="jobtracker.frameworkagreement",
            ),
        ),
    ]