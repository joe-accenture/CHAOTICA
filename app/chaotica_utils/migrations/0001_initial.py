# Generated by Django 4.2.2 on 2023-09-12 14:51

import chaotica_utils.models
from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.db.models.manager
import django.utils.timezone
import phonenumber_field.modelfields
import simple_history.models
import uuid


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
        ("contenttypes", "0002_remove_content_type_name"),
    ]

    operations = [
        migrations.CreateModel(
            name="User",
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
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "username",
                    models.CharField(
                        error_messages={
                            "unique": "A user with that username already exists."
                        },
                        help_text="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.",
                        max_length=150,
                        unique=True,
                        validators=[
                            django.contrib.auth.validators.UnicodeUsernameValidator()
                        ],
                        verbose_name="username",
                    ),
                ),
                (
                    "first_name",
                    models.CharField(
                        blank=True, max_length=150, verbose_name="first name"
                    ),
                ),
                (
                    "last_name",
                    models.CharField(
                        blank=True, max_length=150, verbose_name="last name"
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        blank=True, max_length=254, verbose_name="email address"
                    ),
                ),
                (
                    "is_staff",
                    models.BooleanField(
                        default=False,
                        help_text="Designates whether the user can log into this admin site.",
                        verbose_name="staff status",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.",
                        verbose_name="active",
                    ),
                ),
                (
                    "date_joined",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="date joined"
                    ),
                ),
                (
                    "job_title",
                    models.CharField(
                        blank=True,
                        default="",
                        max_length=255,
                        null=True,
                        verbose_name="Job Title",
                    ),
                ),
                (
                    "location",
                    models.CharField(
                        blank=True,
                        default="",
                        max_length=255,
                        null=True,
                        verbose_name="Location",
                    ),
                ),
                (
                    "external_id",
                    models.CharField(
                        blank=True,
                        db_index=True,
                        default="",
                        max_length=255,
                        null=True,
                        verbose_name="External ID",
                    ),
                ),
                (
                    "phone_number",
                    phonenumber_field.modelfields.PhoneNumberField(
                        blank=True, max_length=128, region=None
                    ),
                ),
                (
                    "show_help",
                    models.BooleanField(
                        default=True,
                        help_text="Should help be shown",
                        verbose_name="Show Tips",
                    ),
                ),
                (
                    "site_theme",
                    models.CharField(
                        default="light", max_length=20, verbose_name="Site Theme"
                    ),
                ),
                (
                    "schedule_feed_id",
                    models.UUIDField(
                        default=uuid.uuid4, verbose_name="Calendar Feed Key"
                    ),
                ),
                (
                    "profile_image",
                    models.ImageField(
                        default="default.jpg",
                        upload_to=chaotica_utils.models.get_media_image_file_path,
                    ),
                ),
                (
                    "acting_manager",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=models.SET(chaotica_utils.models.get_sentinel_user),
                        related_name="users_acting_managed",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "user",
                "verbose_name_plural": "users",
                "abstract": False,
            },
            managers=[
                ("objects", django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name="Group",
            fields=[],
            options={
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("auth.group",),
            managers=[
                ("objects", django.contrib.auth.models.GroupManager()),
            ],
        ),
        migrations.CreateModel(
            name="Notification",
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
                ("timestamp", models.DateTimeField(auto_now_add=True)),
                ("title", models.CharField(default="", max_length=255)),
                ("icon", models.CharField(default="", max_length=255)),
                ("message", models.TextField(default="")),
                ("link", models.URLField(blank=True, null=True)),
                ("is_read", models.BooleanField(default=False)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-timestamp"],
            },
        ),
        migrations.CreateModel(
            name="Note",
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
                    "create_date",
                    models.DateTimeField(
                        auto_now_add=True,
                        help_text="Date the record was created",
                        verbose_name="Created",
                    ),
                ),
                (
                    "mod_date",
                    models.DateTimeField(
                        auto_now=True,
                        help_text="Date the record was last modified",
                        verbose_name="Last Modified",
                    ),
                ),
                (
                    "content",
                    models.TextField(
                        blank=True,
                        help_text="Note Text",
                        null=True,
                        verbose_name="Content",
                    ),
                ),
                (
                    "is_system_note",
                    models.BooleanField(
                        default=False,
                        help_text="Is the note generated by the system",
                        verbose_name="System Note",
                    ),
                ),
                ("object_id", models.PositiveIntegerField()),
                (
                    "author",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=models.SET(chaotica_utils.models.get_sentinel_user),
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "content_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="contenttypes.contenttype",
                    ),
                ),
            ],
            options={
                "verbose_name": "Note",
                "verbose_name_plural": "Notes",
                "ordering": ["-create_date"],
            },
            managers=[
                ("system_objects", django.db.models.manager.Manager()),
            ],
        ),
        migrations.CreateModel(
            name="Language",
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
                ("lang_code", models.CharField(max_length=10)),
                ("display_name", models.CharField(max_length=255)),
            ],
            options={
                "ordering": ["display_name"],
                "unique_together": {("lang_code", "display_name")},
            },
        ),
        migrations.CreateModel(
            name="HistoricalNote",
            fields=[
                (
                    "id",
                    models.BigIntegerField(
                        auto_created=True, blank=True, db_index=True, verbose_name="ID"
                    ),
                ),
                (
                    "create_date",
                    models.DateTimeField(
                        blank=True,
                        editable=False,
                        help_text="Date the record was created",
                        verbose_name="Created",
                    ),
                ),
                (
                    "mod_date",
                    models.DateTimeField(
                        blank=True,
                        editable=False,
                        help_text="Date the record was last modified",
                        verbose_name="Last Modified",
                    ),
                ),
                (
                    "content",
                    models.TextField(
                        blank=True,
                        help_text="Note Text",
                        null=True,
                        verbose_name="Content",
                    ),
                ),
                (
                    "is_system_note",
                    models.BooleanField(
                        default=False,
                        help_text="Is the note generated by the system",
                        verbose_name="System Note",
                    ),
                ),
                ("object_id", models.PositiveIntegerField()),
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
                    "author",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "content_type",
                    models.ForeignKey(
                        blank=True,
                        db_constraint=False,
                        null=True,
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="+",
                        to="contenttypes.contenttype",
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
            ],
            options={
                "verbose_name": "historical Note",
                "verbose_name_plural": "historical Notes",
                "ordering": ("-history_date", "-history_id"),
                "get_latest_by": ("history_date", "history_id"),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.AddField(
            model_name="user",
            name="groups",
            field=models.ManyToManyField(
                blank=True,
                help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                related_name="user_set",
                related_query_name="user",
                to="chaotica_utils.group",
                verbose_name="groups",
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="languages",
            field=models.ManyToManyField(
                blank=True, to="chaotica_utils.language", verbose_name="Languages"
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="manager",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=models.SET(chaotica_utils.models.get_sentinel_user),
                related_name="users_managed",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="user_permissions",
            field=models.ManyToManyField(
                blank=True,
                help_text="Specific permissions for this user.",
                related_name="user_set",
                related_query_name="user",
                to="auth.permission",
                verbose_name="user permissions",
            ),
        ),
        migrations.CreateModel(
            name="UserCost",
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
                    "effective_from",
                    models.DateField(
                        blank=True,
                        help_text="Date cost applies from",
                        null=True,
                        verbose_name="Effective From",
                    ),
                ),
                (
                    "cost_per_hour",
                    models.DecimalField(
                        blank=True,
                        decimal_places=2,
                        help_text="Cost of the user per hour",
                        max_digits=10,
                        null=True,
                        verbose_name="Cost Per Hour",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=models.SET(chaotica_utils.models.get_sentinel_user),
                        related_name="costs",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["user", "-effective_from"],
                "unique_together": {("user", "effective_from")},
            },
        ),
    ]