# Generated by Django 5.0.3 on 2024-03-22 20:59

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("jobtracker", "0025_alter_organisationalunit_options"),
    ]

    operations = [
        migrations.CreateModel(
            name="OrganisationalUnitRole",
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
                    "name",
                    models.IntegerField(
                        choices=[
                            (0, "Pending Approval"),
                            (1, "Consultant"),
                            (2, "Sales"),
                            (3, "Service Delivery"),
                            (4, "Manager"),
                            (5, "Tech QA'er"),
                            (6, "Pres QA'er"),
                            (7, "Scoper"),
                            (8, "Super Scoper"),
                        ],
                        default=1,
                        verbose_name="Name",
                    ),
                ),
            ],
        ),
        migrations.AlterModelOptions(
            name="organisationalunitmember",
            options={"get_latest_by": "mod_date", "ordering": ["member"]},
        ),
        migrations.RemoveField(
            model_name="historicalorganisationalunitmember",
            name="role",
        ),
        migrations.RemoveField(
            model_name="organisationalunitmember",
            name="role",
        ),
        migrations.AddField(
            model_name="organisationalunitmember",
            name="roles",
            field=models.ManyToManyField(
                blank=True, to="jobtracker.organisationalunitrole", verbose_name="Roles"
            ),
        ),
    ]
