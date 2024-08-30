# Generated by Django 5.0.6 on 2024-08-29 10:52

import chaotica_utils.utils
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("jobtracker", "0018_alter_organisationalunitmember_unique_together"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name="job",
            name="associated_framework",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="associated_jobs",
                to="jobtracker.frameworkagreement",
            ),
        ),
        migrations.AlterField(
            model_name="job",
            name="created_by",
            field=models.ForeignKey(
                on_delete=models.SET(chaotica_utils.models.get_sentinel_user),
                related_name="jobs_created",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Created By",
            ),
        ),
        migrations.AlterField(
            model_name="job",
            name="primary_client_poc",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="jobs_poc_for",
                to="jobtracker.contact",
                verbose_name="Primary Point of Contact",
            ),
        ),
        migrations.AlterField(
            model_name="organisationalunit",
            name="lead",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="units_lead",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
