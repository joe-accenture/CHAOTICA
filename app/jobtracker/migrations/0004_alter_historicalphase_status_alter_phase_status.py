# Generated by Django 4.2.2 on 2023-10-09 16:46

from django.db import migrations
import django_fsm


class Migration(migrations.Migration):
    dependencies = [
        ("jobtracker", "0003_alter_historicalphase_actual_completed_date_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="historicalphase",
            name="status",
            field=django_fsm.FSMIntegerField(
                choices=[
                    (0, "Draft"),
                    (1, "Pending Scheduling"),
                    (2, "Schedule Tentative"),
                    (3, "Schedule Confirmed"),
                    (4, "Pre-checks"),
                    (5, "Client Not Ready"),
                    (6, "Ready to Begin"),
                    (7, "In Progress"),
                    (8, "Pending Technical QA"),
                    (9, "Tech QA"),
                    (10, "Author Tech Updates"),
                    (11, "Pending Presentation QA"),
                    (12, "Pres QA"),
                    (13, "Author Pres Updates"),
                    (14, "Completed"),
                    (15, "Delivered"),
                    (16, "Cancelled"),
                    (17, "Postponed"),
                    (18, "Deleted"),
                    (19, "Archived"),
                ],
                db_index=True,
                default=0,
                protected=True,
            ),
        ),
        migrations.AlterField(
            model_name="phase",
            name="status",
            field=django_fsm.FSMIntegerField(
                choices=[
                    (0, "Draft"),
                    (1, "Pending Scheduling"),
                    (2, "Schedule Tentative"),
                    (3, "Schedule Confirmed"),
                    (4, "Pre-checks"),
                    (5, "Client Not Ready"),
                    (6, "Ready to Begin"),
                    (7, "In Progress"),
                    (8, "Pending Technical QA"),
                    (9, "Tech QA"),
                    (10, "Author Tech Updates"),
                    (11, "Pending Presentation QA"),
                    (12, "Pres QA"),
                    (13, "Author Pres Updates"),
                    (14, "Completed"),
                    (15, "Delivered"),
                    (16, "Cancelled"),
                    (17, "Postponed"),
                    (18, "Deleted"),
                    (19, "Archived"),
                ],
                db_index=True,
                default=0,
                protected=True,
            ),
        ),
    ]
