# Generated by Django 5.0.6 on 2024-08-29 22:53

import chaotica_utils.models
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("chaotica_utils", "0009_alter_leaverequest_type_of_leave"),
        ("jobtracker", "0020_alter_job_account_manager_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="leaverequest",
            name="authorised_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.SET(chaotica_utils.models.get_sentinel_user),
                related_name="leave_records_authorised",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="leaverequest",
            name="declined_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.SET(chaotica_utils.models.get_sentinel_user),
                related_name="leave_records_declined",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="leaverequest",
            name="timeslot",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="leaverequest",
                to="jobtracker.timeslot",
            ),
        ),
        migrations.AlterField(
            model_name="leaverequest",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="leave_records",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
