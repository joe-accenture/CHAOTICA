# Generated by Django 5.0.6 on 2024-08-22 21:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("jobtracker", "0010_alter_userskill_rating"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="job",
            options={"ordering": ["-id"], "verbose_name": "Job"},
        ),
    ]
