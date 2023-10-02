# Generated by Django 4.2.2 on 2023-09-12 22:49

from django.db import migrations, models
import django.db.models.deletion
import django_fsm


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
                    ("view_users_schedule", "View Members Schedule"),
                    ("can_signoff_scopes", "Can signoff scopes"),
                    ("can_signoff_own_scopes", "Can signoff own scopes"),
                ),
            },
        ),
        migrations.RemoveField(
            model_name="historicalphase",
            name="feedback_presqa",
        ),
        migrations.RemoveField(
            model_name="historicalphase",
            name="feedback_scope",
        ),
        migrations.RemoveField(
            model_name="historicalphase",
            name="feedback_techqa",
        ),
        migrations.RemoveField(
            model_name="phase",
            name="feedback_presqa",
        ),
        migrations.RemoveField(
            model_name="phase",
            name="feedback_scope",
        ),
        migrations.RemoveField(
            model_name="phase",
            name="feedback_techqa",
        ),
        migrations.AddField(
            model_name="feedback",
            name="feedbackType",
            field=models.IntegerField(
                choices=[
                    (0, "Scoping"),
                    (1, "Technical"),
                    (2, "Presentation"),
                    (3, "Other"),
                ],
                default=3,
                help_text="Type of feedback",
                verbose_name="Type",
            ),
        ),
        migrations.AddField(
            model_name="feedback",
            name="phase",
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="feedback",
                to="jobtracker.phase",
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="historicalfeedback",
            name="feedbackType",
            field=models.IntegerField(
                choices=[
                    (0, "Scoping"),
                    (1, "Technical"),
                    (2, "Presentation"),
                    (3, "Other"),
                ],
                default=3,
                help_text="Type of feedback",
                verbose_name="Type",
            ),
        ),
        migrations.AddField(
            model_name="historicalfeedback",
            name="phase",
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                to="jobtracker.phase",
            ),
        ),
        migrations.AlterField(
            model_name="historicaljob",
            name="status",
            field=django_fsm.FSMIntegerField(
                choices=[
                    (0, "Draft"),
                    (1, "Pending Scoping"),
                    (2, "Scoping"),
                    (3, "Additional Scoping Required"),
                    (4, "Pending Scope Signoff"),
                    (5, "Scoping Complete"),
                    (6, "Pending Start"),
                    (7, "In Progress"),
                    (8, "Completed"),
                    (9, "Lost"),
                    (10, "Deleted"),
                    (11, "Archived"),
                ],
                default=0,
                help_text="Current state of the job",
                protected=True,
                verbose_name="Job Status",
            ),
        ),
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
                    (8, "Tech QA"),
                    (9, "Author Tech Updates"),
                    (10, "Pres QA"),
                    (11, "Author Pres Updates"),
                    (12, "Completed"),
                    (13, "Delivered"),
                    (14, "Cancelled"),
                    (15, "Postponed"),
                    (16, "Deleted"),
                    (17, "Archived"),
                ],
                db_index=True,
                default=0,
                protected=True,
            ),
        ),
        migrations.AlterField(
            model_name="job",
            name="status",
            field=django_fsm.FSMIntegerField(
                choices=[
                    (0, "Draft"),
                    (1, "Pending Scoping"),
                    (2, "Scoping"),
                    (3, "Additional Scoping Required"),
                    (4, "Pending Scope Signoff"),
                    (5, "Scoping Complete"),
                    (6, "Pending Start"),
                    (7, "In Progress"),
                    (8, "Completed"),
                    (9, "Lost"),
                    (10, "Deleted"),
                    (11, "Archived"),
                ],
                default=0,
                help_text="Current state of the job",
                protected=True,
                verbose_name="Job Status",
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
                    (8, "Tech QA"),
                    (9, "Author Tech Updates"),
                    (10, "Pres QA"),
                    (11, "Author Pres Updates"),
                    (12, "Completed"),
                    (13, "Delivered"),
                    (14, "Cancelled"),
                    (15, "Postponed"),
                    (16, "Deleted"),
                    (17, "Archived"),
                ],
                db_index=True,
                default=0,
                protected=True,
            ),
        ),
    ]