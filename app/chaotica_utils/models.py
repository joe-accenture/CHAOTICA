from django.db import models
from django.contrib.auth.models import AbstractUser
from django.templatetags.static import static
import uuid, os, random
from .managers import SystemNoteManager
from .enums import GlobalRoles, LeaveRequestTypes, NotificationTypes
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.conf import settings
from django.db.models import Q
from django.urls import reverse
from django.contrib.auth import get_user_model
from simple_history.models import HistoricalRecords
import django.contrib.auth
from guardian.shortcuts import get_objects_for_user
from django.utils import timezone
from datetime import timedelta, date
from dateutil.relativedelta import relativedelta
from phonenumber_field.modelfields import PhoneNumberField
from django_countries.fields import CountryField
from .tasks import task_send_notifications
from jobtracker.enums import DefaultTimeSlotTypes, UserSkillRatings
from business_duration import businessDuration
from constance import config
from django.template.loader import render_to_string
from django.core.mail import send_mail


def get_sentinel_user():
    return get_user_model().objects.get_or_create(email='deleted@chaotica.app')[0]


class Note(models.Model):
    create_date = models.DateTimeField(verbose_name="Created", auto_now_add=True, help_text="Date the record was created")
    mod_date = models.DateTimeField(verbose_name="Last Modified", auto_now=True, help_text="Date the record was last modified")
    history = HistoricalRecords()
    content = models.TextField(verbose_name="Content", blank=True, help_text="Note Text")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET(get_sentinel_user),)
    is_system_note = models.BooleanField(default=False, help_text="Is the note generated by the system", verbose_name="System Note")
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    system_objects = SystemNoteManager()
    objects = models.Manager()

    class Meta:
        verbose_name = "Note"
        verbose_name_plural = "Notes"
        ordering = ['-create_date']


class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=255, default="")
    icon = models.CharField(max_length=255, blank=True, null=True, default="")
    message = models.TextField(default="")
    link = models.URLField(blank=True, null=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-timestamp']


class Group(django.contrib.auth.models.Group):

    class Meta:
        proxy = True

    def getGlobalRoleINT(self):
        # If we're a global role group... return the int value
        for role in GlobalRoles.CHOICES:
            name_to_check = settings.GLOBAL_GROUP_PREFIX+role[1]
            if self.name == name_to_check:
                return role[0]
        return None

    def role_bs_colour(self):
        val = self.getGlobalRoleINT()
        if val != None:
            return GlobalRoles.BS_COLOURS[val][1]
        else:
            return ""
        
def get_media_profile_file_path(_, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join('profile_pics', filename)
        
def get_media_image_file_path(_, filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join('images', filename)

class Language(models.Model):
    lang_code = models.CharField(max_length=10)
    display_name = models.CharField(max_length=255)

    class Meta:
        ordering = ['display_name']
        unique_together = ['lang_code', 'display_name']

    def __str__(self):
        return '{}'.format(self.display_name)
    
class UserInvitation(models.Model):
    invited_email = models.EmailField(verbose_name="Email Address", max_length=255, unique=True)
    accepted = models.BooleanField(verbose_name="Accepted", help_text="Has the invitation been accepted", default=False)
    invite_id = models.UUIDField(verbose_name="Invitation ID", default=uuid.uuid4)
    sent = models.DateTimeField(null=True, blank=True)
    invited_by = models.ForeignKey(settings.AUTH_USER_MODEL,
        related_name='users_invited',
        null=True, blank=True,
        on_delete=models.PROTECT,
    )

    def is_expired(self):
        expiry_date = self.sent + timedelta(days=config.USER_INVITE_EXPIRY)
        return expiry_date <= timezone.now()    
    
    def get_absolute_url(self):
        return reverse('signup', kwargs={'invite_id': self.invite_id})
    
    def send_email(self):
        from .utils import ext_reverse
        ## Email notification
        context = {}
        context['SITE_DOMAIN'] = settings.SITE_DOMAIN
        context['SITE_PROTO'] = settings.SITE_PROTO
        context['title'] = "You're invited to Chaotica"
        context['message'] = "You've been invited to join Chaotica - (Centralised Hub for Assigning Operational Tasks, Interactive Calendaring and Alerts). Follow the link below to accept the invitation and setup your account."
        context['action_link'] = ext_reverse(self.get_absolute_url())
        msg_html = render_to_string("emails/user_invite.html", context)
        send_mail(  
            context['title'], context['message'], None, [self.invited_email], html_message=msg_html,
        )

        self.sent = timezone.now()
        self.save()


class User(AbstractUser):
    # Fields to enforce email as the auth field
    username = None
    email = models.EmailField('Email Address', unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    manager = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET(get_sentinel_user),
                            related_name="users_managed", null=True, blank=True)
    acting_manager = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET(get_sentinel_user),
                            related_name="users_acting_managed", null=True, blank=True)
    pref_timezone = models.CharField(verbose_name="Time Zone", max_length=255, null=True, blank=True, default="UTC")
    job_title = models.CharField(verbose_name="Job Title", max_length=255, null=True, blank=True, default="")
    location = models.CharField(verbose_name="Location", max_length=255, null=True, blank=True, default="")
    country = CountryField(default="GB")
    external_id = models.CharField(verbose_name="External ID", db_index=True, max_length=255, null=True, blank=True, default="")
    phone_number = PhoneNumberField(blank=True)
    show_help = models.BooleanField(verbose_name="Show Helpful Tips", help_text="Should help be shown", default=True)
    site_theme = models.CharField(verbose_name="Site Theme", max_length=20, default="light")
    schedule_feed_id = models.UUIDField(verbose_name="Calendar Feed Key", default=uuid.uuid4)
    schedule_feed_family_id = models.UUIDField(verbose_name="Calendar Feed Family Key", default=uuid.uuid4)
    groups = models.ManyToManyField(Group, verbose_name='groups',
            blank=True, help_text='The groups this user belongs to. A user will '
                                    'get all permissions granted to each of '
                                    'their groups.',
            related_name="user_set", related_query_name="user")
    languages = models.ManyToManyField(Language, verbose_name='Languages', blank=True)
    profile_image = models.ImageField(blank=True,
                                     upload_to=get_media_profile_file_path,)
    contracted_leave = models.IntegerField(verbose_name="Contracted Days Leave", default=25)
    contracted_leave_renewal = models.DateField(verbose_name="Leave Renewal Date", default=date(day=1, month=9, year=2023))
    
    class Meta:
        ordering = ['last_name']

    def can_scope(self):
        from jobtracker.models.orgunit import OrganisationalUnit
        return get_objects_for_user(self, "can_scope_jobs", OrganisationalUnit)
    
    def can_signoff_scope(self):
        from jobtracker.models.orgunit import OrganisationalUnit
        return get_objects_for_user(self, "can_signoff_scopes", OrganisationalUnit)

    def _get_last_leave_renewal_date(self):
        today = timezone.now().date()
        renewal_date = self.contracted_leave_renewal.replace(year=today.year)
        if renewal_date < today:
            return renewal_date
        else:
            return renewal_date.replace(year=today.year-1)

    def _get_next_leave_renewal_date(self):
        today = timezone.now().date()
        renewal_date = self.contracted_leave_renewal.replace(year=today.year)
        if renewal_date > today:
            return renewal_date
        else:
            return renewal_date.replace(year=today.year+1)
    
    def remaining_leave(self):
        return self.contracted_leave - self.pending_leave() - self.used_leave()

    def pending_leave(self):
        total = 0
        for leave in LeaveRequest.objects.filter(
            user=self, cancelled=False, authorised=True, 
            start_date__gte=self._get_last_leave_renewal_date(),
            end_date__lte=self._get_next_leave_renewal_date()).filter(
            start_date__gte=timezone.now()):
            total = total + leave.affected_days()
        return total

    def used_leave(self):
        total = 0
        for leave in LeaveRequest.objects.filter(
            user=self, cancelled=False, authorised=True, 
            start_date__gte=self._get_last_leave_renewal_date(),
            end_date__lte=self._get_next_leave_renewal_date()).filter(
            start_date__lte=timezone.now(),
            end_date__lte=timezone.now()):
            total = total + leave.affected_days()
        return total
    
    def unread_notifications(self):
        return Notification.objects.filter(user=self, is_read=False)

    def get_avatar_url(self):
        if self.profile_image:
            return self.profile_image.url
        else:
            return static('assets/img/team/avatar-rounded.webp')
    
    def get_current_status(self):
        # online, offline, away, do-not-disturb
        # Used to decorate avatars
        return "online"
    
    def get_timeslots(self, start=None, end=None, phase_focus=None):
        from jobtracker.models import TimeSlot
        from .utils import fullcalendar_to_datetime
        data = []

        today = timezone.now().today()
        start_of_week = today - timedelta(days = today.weekday())
        end_of_week = start_of_week + timedelta(days = 6)

        if start:
            start = fullcalendar_to_datetime(start)
        if end:
            end = fullcalendar_to_datetime(end)
            
        start = start or start_of_week
        end = end or end_of_week

        slots = TimeSlot.objects.filter(user=self, start__gte=start, start__lte=end)
        for slot in slots:
            slot_json = slot.get_schedule_json()
            is_focused = False
            if phase_focus:
                if slot.phase:
                    if slot.phase == phase_focus:
                        is_focused = True
                    if not is_focused and slot.phase.job == phase_focus:
                        is_focused = True
            if phase_focus and not is_focused:
                slot_json['display'] = "background"
            data.append(slot_json)
        return data
    
    def get_holidays(self, start=None, end=None):
        from .utils import fullcalendar_to_datetime
        data = []

        today = timezone.now().today()
        start_of_week = today - timedelta(days = today.weekday())
        end_of_week = start_of_week + timedelta(days = 6)

        if start:
            start = fullcalendar_to_datetime(start)
        if end:
            end = fullcalendar_to_datetime(end)

        start = start or start_of_week
        end = end or end_of_week

        slots = Holiday.objects.filter(country__country=self.country, date__gte=start.date(), date__lte=end.date())
        for slot in slots:
            data.append(slot.get_schedule_json())
        return data
    
    def is_people_manager(self):
        if self.users_managed.exists() or self.users_acting_managed.exists():
            return True
        else:
            return False

    def save(self, *args, **kwargs):
        # Lets check if we're the only user...
        if User.objects.all().count() == 1:
            # We're the first real user. Bump us to superuser
            self.is_superuser = True
            self.is_staff = True
            super().save(*args, **kwargs)
            # Make sure they are a global admin too!
            g_admin, _ = Group.objects.get_or_create(name=settings.GLOBAL_GROUP_PREFIX+GlobalRoles.CHOICES[GlobalRoles.ADMIN][1])
            self.groups.add(g_admin)
        return super().save(*args, **kwargs)
    
    def services_can_lead(self):
        from jobtracker.models import Service

        return Service.objects.filter(
            Q(skillsRequired__in=self.get_skills_specialist()) |
            Q(skillsRequired__in=self.get_skills_alone())
        )
    
    def services_can_contribute(self):
        from jobtracker.models import Service

        return Service.objects.filter(
            Q(skillsRequired__in=self.get_skills_specialist()) |
            Q(skillsRequired__in=self.get_skills_alone()) |
            Q(skillsRequired__in=self.get_skills_support())
        )
    
    def get_skills_specialist(self):
        from jobtracker.models import Skill
        return Skill.objects.filter(pk__in=self.skills.filter(rating=UserSkillRatings.SPECIALIST).values("skill")).distinct()
    
    def get_skills_alone(self):
        from jobtracker.models import Skill
        return Skill.objects.filter(pk__in=self.skills.filter(rating=UserSkillRatings.CAN_DO_ALONE).values("skill")).distinct()
    
    def get_skills_support(self):
        from jobtracker.models import Skill
        return Skill.objects.filter(pk__in=self.skills.filter(rating=UserSkillRatings.CAN_DO_WITH_SUPPORT).values("skill")).distinct()
    
    def __str__(self):
        if self.first_name and self.last_name:
            return '{} {}'.format(self.first_name, self.last_name)
        else:
            return '{}'.format(self.email)
        
    def get_average_qa_rating(self, qa_field, 
                            from_range=timezone.now() - relativedelta(months=12), 
                            to_range=timezone.now()):
        my_reports = self.phase_where_report_author.filter(
            actual_completed_date__gte=from_range, actual_completed_date__lte=to_range)
        total_reports = my_reports.count()
        combined_score = 0
        total_score = 0
        
        for report in my_reports:
            # check we've got rating!
            if getattr(report, qa_field):
                combined_score = combined_score + int(getattr(report, qa_field))

        if total_reports > 0:
            total_score = combined_score / total_reports
        
        return total_score

    def get_average_techqa_feedback(self, 
                                         from_range=timezone.now() - relativedelta(months=12), 
                                         to_range=timezone.now()):
        return self.get_average_qa_rating("techqa_report_rating", from_range, to_range)
        

    def get_average_presqa_feedback(self, 
                                         from_range=timezone.now() - relativedelta(months=12), 
                                         to_range=timezone.now()):
        return self.get_average_qa_rating("presqa_report_rating", from_range, to_range)
    
        
    def get_average_qa_rating_12mo(self, qa_field):
        from chaotica_utils.utils import last_day_of_month
        # Get the last 12 months of tech feedback
        months = []
        data = []
        today = timezone.now()
        for i in range(12,-1, -1):
            month = today-relativedelta(months=i)
            start_month = month+relativedelta(day=1)
            end_month = last_day_of_month(start_month)
            avg = self.get_average_qa_rating(qa_field, from_range=start_month, to_range=end_month)
            months.append(str(start_month.date()))
            data.append(avg)

        data = {
            'months': months,
            'data': data,
        }
        return data
    
        
    def get_average_techqa_feedback_12mo(self):
        return self.get_average_qa_rating_12mo("techqa_report_rating")
    
        
    def get_average_presqa_feedback_12mo(self):
        return self.get_average_qa_rating_12mo("presqa_report_rating")
    
    
    def get_absolute_url(self):
        if self.email:
            return reverse('user_profile', kwargs={'email': self.email})
        else:
            return None
    
    def current_cost(self):
        if self.costs.all().exists():
            return self.costs.all().last()
        else:
            return None
    
    def update_cost(self, cost, effective_from=timezone.now()):
        return UserCost.objects.create(user=self, effective_from=effective_from, cost_per_hour=cost)


class UserCost(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET(get_sentinel_user),
                            related_name="costs")
    effective_from = models.DateField(verbose_name="Effective From", null=True, blank=True, help_text="Date cost applies from")
    cost_per_hour = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
        verbose_name="Cost Per Hour", help_text="Cost of the user per hour")

    class Meta:
        ordering = ['user', '-effective_from']
        unique_together = ['user', 'effective_from']
    
    def __str__(self):
        return '{} {}'.format(str(self.user), str(self.cost_per_hour))


class HolidayCountry(models.Model):
    country = CountryField()

    class Meta:
        ordering = ['country',]
    
    def __str__(self):
        return '{}'.format(str(self.country.name))


class Holiday(models.Model):
    date = models.DateField(db_index=True)
    country = models.ForeignKey(HolidayCountry, on_delete=models.CASCADE)
    subdivs = models.JSONField(default=list, blank=True)
    reason = models.CharField(max_length=255)

    def __str__(self):
        return '{} ({})'.format(str(self.reason), str(self.country))
    
    def get_schedule_json(self):            
        return {
            "title": "{} ({})".format(self.reason, str(self.country)),
            "start": self.date,
            "end": self.date,
            "allDay": True,
            "display": "background",
            "id": self.pk,
        }

    class Meta:
        ordering = ['-date',]
        unique_together = ['date', 'country', 'reason']



class LeaveRequest(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET(get_sentinel_user),
                            related_name="leave_records")
    
    requested_on = models.DateTimeField(auto_now_add=True)
    start_date = models.DateTimeField(db_index=True)
    end_date = models.DateTimeField(db_index=True)

    type_of_leave = models.IntegerField(choices=LeaveRequestTypes.CHOICES)
    notes = models.TextField(blank=True)

    authorised = models.BooleanField(default=False)
    authorised_on = models.DateTimeField(null=True, blank=True)
    authorised_by = models.ForeignKey(settings.AUTH_USER_MODEL,
        related_name='leave_records_authorised',
        null=True, blank=True,
        on_delete=models.PROTECT,
    )

    timeslot = models.ForeignKey('jobtracker.TimeSlot', null=True, blank=True, on_delete=models.CASCADE)

    cancelled = models.BooleanField(default=False)
    cancelled_on = models.DateTimeField(null=True, blank=True)

    declined = models.BooleanField(default=False)
    declined_on = models.DateTimeField(null=True, blank=True)
    declined_by = models.ForeignKey(settings.AUTH_USER_MODEL,
        related_name='leave_records_declined',
        null=True, blank=True,
        on_delete=models.PROTECT,
    )

    class Meta:
        verbose_name = 'Leave Request'
        ordering = ['start_date']
    
    def overlaps_work(self):
        from jobtracker.models.timeslot import TimeSlotType, TimeSlot
        return TimeSlot.objects.filter(user=self.user, slot_type=TimeSlotType.get_builtin_object(DefaultTimeSlotTypes.DELIVERY),
            start__lte=self.end_date,
            end__gte=self.start_date).exists()
    
    def overlaps_confirmed_work(self):
        from jobtracker.models.timeslot import TimeSlotType, TimeSlot
        from jobtracker.enums import PhaseStatuses
        return TimeSlot.objects.filter(user=self.user, slot_type=TimeSlotType.get_builtin_object(DefaultTimeSlotTypes.DELIVERY),
            phase__status__gte=PhaseStatuses.SCHEDULED_CONFIRMED, 
            start__lte=self.end_date,
            end__gte=self.start_date).exists()

    def requested_late(self):
        return self.start_date < (self.requested_on + timedelta(days=config.LEAVE_DAYS_NOTICE))
    
    def affected_days(self):
        unit='day'
        days = businessDuration(self.start_date, self.end_date, unit=unit)
        return round(days, 2)
    
    def can_cancel(self):
        # Only situ we can't cancel is if it's in the past or it's already cancelled.
        if self.start_date < timezone.now():
            return False
        if self.cancelled:
            return False
        return True
    
    def can_approve_by(self):
        # Update to reflect logic...
        user_pks = []
        if self.user.manager:
            user_pks.append(self.user.manager.pk)
        if self.user.acting_manager:
            user_pks.append(self.user.acting_manager.pk)
        
        if not user_pks:
            # No managers - lets default to unit managers...
            for membership in self.user.unit_memberships.all():
                user_pks.append(membership.unit.get_active_members_with_perm("can_approve_leave_requests").values_list('pk', flat=True))
        return User.objects.filter(pk__in=user_pks).distinct()
    
    def can_user_auth(self, user):
        if self.cancelled:
            return False
        return user in self.can_approve_by()
    
    EMAIL_TEMPLATE = "emails/leave.html"
    
    def send_request_notification(self):
        from .utils import AppNotification, ext_reverse
        # Send a notice to... people?!
        users_to_notify = self.can_approve_by()
        notice = AppNotification(
            NotificationTypes.PHASE, 
            "Leave Requested - Please review", 
            str(self.user)+" has requested leave. Please review the request", 
            self.EMAIL_TEMPLATE, action_link=ext_reverse(reverse('manage_leave')), leave=self)
        task_send_notifications(notice, users_to_notify)

    
    def send_approved_notification(self):
        from .utils import AppNotification, ext_reverse
        # Send a notice to... people?!
        users_to_notify = [self.user]
        notice = AppNotification(
            NotificationTypes.PHASE, 
            "Leave Approved", 
            "Your leave has been approved!",
            self.EMAIL_TEMPLATE, action_link=ext_reverse(reverse('view_own_leave')), leave=self)
        task_send_notifications(notice, users_to_notify)

    
    def send_declined_notification(self):
        from .utils import AppNotification, ext_reverse
        # Send a notice to... people?!
        users_to_notify = [self.user]
        notice = AppNotification(
            NotificationTypes.PHASE, 
            "Leave DECLINED", 
            "Your leave has been declined. Please contact "+str(self.declined_by)+" for information.",
            self.EMAIL_TEMPLATE, action_link=ext_reverse(reverse('view_own_leave')), leave=self)
        task_send_notifications(notice, users_to_notify)

    
    def send_cancelled_notification(self):
        from .utils import AppNotification, ext_reverse
        # Send a notice to... people?!
        users_to_notify = [self.user]
        notice = AppNotification(
            NotificationTypes.PHASE, 
            "Leave Cancelled", 
            "You have cancelled your leave.",
            self.EMAIL_TEMPLATE, action_link=ext_reverse(reverse('view_own_leave')), leave=self)
        task_send_notifications(notice, users_to_notify)
    

    def authorise(self, approved_by):
        from jobtracker.models.timeslot import TimeSlot, TimeSlotType
        if self.cancelled:
            # Can't auth at this stage
            return False
        if not self.authorised:
            # Set our important fields
            self.authorised = True
            self.authorised_by = approved_by
            self.authorised_on = timezone.now()
            self.save()
            # Lets add the timeslot...
            TimeSlot.objects.get_or_create(
                user=self.user, start=self.start_date, end=self.end_date,
                slot_type=TimeSlotType.get_builtin_object(DefaultTimeSlotTypes.LEAVE)
            )
            self.send_approved_notification()
    

    def decline(self, declined_by):
        from jobtracker.models.timeslot import TimeSlot
        if self.authorised or self.cancelled:
            # Can't decline at this stage
            return False
        if not self.declined:
            # Set our important fields
            self.declined = True
            self.declined_by = declined_by
            self.declined_on = timezone.now()
            self.save()
            self.send_declined_notification()

    
    def cancel(self):
        from jobtracker.models.timeslot import TimeSlot, TimeSlotType
        if not self.cancelled:
            # Set our important fields
            self.cancelled = True
            self.cancelled_on = timezone.now()
            self.authorised = False
            self.declined = False
            self.save()
            # Lets delete the timeslot...
            if TimeSlot.objects.filter(user=self.user, start=self.start_date, end=self.end_date,
                slot_type=TimeSlotType.get_builtin_object(DefaultTimeSlotTypes.LEAVE)).exists():
                
                TimeSlot.objects.filter(user=self.user, start=self.start_date, end=self.end_date,
                slot_type=TimeSlotType.get_builtin_object(DefaultTimeSlotTypes.LEAVE)).delete()
            self.send_cancelled_notification()
