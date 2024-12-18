from django.db import models
from ..enums import QualificationStatus
from django.conf import settings
from django.templatetags.static import static
from chaotica_utils.utils import unique_slug_generator
from django.utils import timezone
from django.urls import reverse
from simple_history.models import HistoricalRecords
from django.db.models import JSONField
from django.db.models.functions import Lower
from django.db.models import Q
import uuid, os
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django_bleach.models import BleachField
from guardian.shortcuts import assign_perm, remove_perm, get_users_with_perms


def get_media_image_file_path(_, filename):
    ext = filename.split(".")[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join("images", filename)


class Team(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(null=False, default="", unique=True)
    description = BleachField(blank=True, null=True, default="")
    profile_image = models.ImageField(
        blank=True,
        upload_to=get_media_image_file_path,
    )
    cover_image = models.ImageField(
        blank=True,
        upload_to=get_media_image_file_path,
    )
    is_hidden = models.BooleanField(
        verbose_name="Hidden",
        help_text="Team is only visible to admins, owners and members",
        default=False,
    )
    owners = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        limit_choices_to={"is_active": True},
        help_text="Users responsible for the management of the team.",
    )
    history = HistoricalRecords()
    data = JSONField(verbose_name="Data", null=True, blank=True, default=dict)

    class Meta:
        ordering = [Lower("name")]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slug_generator(self, self.name)
        super(Team, self).save(*args, **kwargs)

    def active_users(self):
        now = timezone.now()
        return self.users.filter(
            Q(left_at__isnull=True) | Q(left_at__gte=now), joined_at__lte=now
        )

    def get_absolute_url(self):
        return reverse(
            "team_detail",
            kwargs={"slug": self.slug},
        )

    def get_avatar_url(self):
        if self.profile_image:
            return self.profile_image.url
        else:
            return static("assets/img/team/avatar-rounded.webp")

    def get_cover_url(self):
        if self.cover_image:
            return self.cover_image.url
        else:
            return static("assets/img/bg/bg-11.png")


# method for updating
@receiver(m2m_changed, sender=Team.owners.through, dispatch_uid="update_owner_perms")
def update_owner_perms(sender, instance, **kwargs):
    if instance:
        for user in instance.owners.all():
            assign_perm("change_team", user, instance)
            assign_perm("delete_team", user, instance)
        all_perms = get_users_with_perms(instance, attach_perms=True)
        for user, perms in all_perms.items():
            if user not in instance.owners.all():
                for perm in perms:
                    remove_perm(perm, user, instance)


class TeamMember(models.Model):
    team = models.ForeignKey(Team, related_name="users", on_delete=models.CASCADE)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="teams",
    )
    history = HistoricalRecords()

    last_updated_on = models.DateTimeField(auto_now=True)
    joined_at = models.DateField(
        "Joined",
        null=True,
        blank=True,
        help_text="Date this user joined the group",
    )
    left_at = models.DateField(
        "Left",
        null=True,
        blank=True,
        help_text="Date this user left the group",
    )

    class Meta:
        ordering = [
            "team",
            "user",
        ]

    def is_active(self):
        now = timezone.now().date()
        if (not self.left_at and self.joined_at <= now) or (
            self.joined_at <= now and self.left_at > now
        ):
            return True
        else:
            return False

    def __str__(self):
        return "%s - %s" % (
            self.user,
            self.team,
        )
