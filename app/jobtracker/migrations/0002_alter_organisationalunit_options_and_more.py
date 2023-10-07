# Generated by Django 4.2.2 on 2023-10-07 20:28

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("jobtracker", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="organisationalunit",
            options={
                "ordering": ["name"],
                "permissions": (
                    ("assign_members_organisationalunit", "Assign Members"),
                    ("can_view_unit_jobs", "Can view jobs"),
                    ("can_add_job", "Can add jobs"),
                    ("can_approve_leave_requests", "Can approve leave requests"),
                    ("can_tqa_jobs", "Can TQA jobs"),
                    ("can_pqa_jobs", "Can PQA jobs"),
                    ("can_scope_jobs", "Can scope jobs"),
                    ("can_signoff_scopes", "Can signoff scopes"),
                    ("can_signoff_own_scopes", "Can signoff own scopes"),
                    ("view_users_schedule", "View Members Schedule"),
                    ("can_schedule_phases", "Can schedule phases"),
                ),
            },
        ),
        migrations.AlterField(
            model_name="timeslot",
            name="deliveryRole",
            field=models.IntegerField(
                choices=[
                    (0, "None"),
                    (1, "Delivery"),
                    (2, "Reporting"),
                    (3, "Management"),
                    (4, "QA"),
                    (5, "Oversight"),
                    (6, "Debrief"),
                    (7, "Contingency"),
                    (8, "Other"),
                ],
                default=0,
                help_text="Type of role in job",
                verbose_name="Delivery Type",
            ),
        ),
        migrations.AlterField(
            model_name="timeslot",
            name="slotType",
            field=models.IntegerField(
                choices=[(0, "Generic"), (1, "Internal"), (2, "Delivery")],
                default=0,
                help_text="Type of time",
                verbose_name="Slot Type",
            ),
        ),
    ]
