from django.shortcuts import get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.template import loader
from django.views.generic.edit import DeleteView
from django.urls import reverse_lazy
from chaotica_utils.views import page_defaults
from chaotica_utils.views import ChaoticaBaseView
from chaotica_utils.models import User
from guardian.shortcuts import get_objects_for_user
from ..models import Job, TimeSlot, UserSkill
from ..forms import CreateTimeSlotModalForm, SchedulerFilter
from ..enums import UserSkillRatings
import logging
from django.contrib.auth.decorators import login_required


logger = logging.getLogger(__name__)


@login_required
def view_scheduler(request):
    context = {}
    template = loader.get_template('scheduler.html')
    context = {**context, **page_defaults(request)}
    context['filterForm'] = SchedulerFilter(request.GET)
    return HttpResponse(template.render(context, request))


def _filter_users_on_query(request):
    from pprint import pprint
    users_pk = []
    for org_unit in get_objects_for_user(request.user, 'jobtracker.view_users_schedule'):
        for user in org_unit.get_activeMembers():
            if user.pk not in users_pk:
                users_pk.append(user.pk)

    users = User.objects.filter(pk__in=users_pk)

    # Now lets apply the filters from the query...

    ## Filter users
    users_q = request.GET.get('users', None)
    if users_q:
        pprint(users_q)
        users = users.filter(pk__in=users_q)

    ## Filter on skills
    skills_specialist = request.GET.get('skills_specialist', None)
    if skills_specialist:
        users = users.filter(skills__in=UserSkill.objects.filter(skill__pk__in=skills_specialist, rating=UserSkillRatings.SPECIALIST))

    skills_can_do_alone = request.GET.get('skills_can_do_alone', None)
    if skills_can_do_alone:
        users = users.filter(skills__in=UserSkill.objects.filter(skill__pk__in=skills_can_do_alone, rating=UserSkillRatings.CAN_DO_ALONE))

    skills_can_do_support = request.GET.get('skills_can_do_support', None)
    if skills_can_do_support:
        users = users.filter(skills__in=UserSkill.objects.filter(skill__pk__in=skills_can_do_support, rating=UserSkillRatings.CAN_DO_WITH_SUPPORT))

    return users


@login_required
def view_scheduler_slots(request):
    data = []
    scheduled_users = _filter_users_on_query(request)
    for user in scheduled_users:
        data = data + user.get_timeslots(
            start=request.GET.get('start', None),
            end=request.GET.get('end', None),
            )
    return JsonResponse(data, safe=False)


@login_required
def view_scheduler_members(request):
    data = []
    scheduled_users = _filter_users_on_query(request)
    for user in scheduled_users:
        user_title = str(user)
        data.append({
            "id": user.pk,
            "title": user_title,
            # "businessHours": {
            #     "startTime": org_unit.businessHours_startTime,
            #     "endTime": org_unit.businessHours_endTime,
            #     "daysOfWeek": org_unit.businessHours_days,
            # }
        })
    return JsonResponse(data, safe=False)

@login_required
def view_own_schedule_timeslots(request):
    data = request.user.get_timeslots(
        start=request.GET.get('start', None),
        end=request.GET.get('end', None),
        )
    return JsonResponse(data, safe=False)


@login_required
def create_scheduler_slot(request):
    data = dict()
    start = request.GET.get('start', None)
    end = request.GET.get('end', None)
    resource_id = request.GET.get('resource_id', None)

    if request.method == 'POST':
        form = CreateTimeSlotModalForm(request.POST, start=start, end=end, resource_id=resource_id)
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
        else:
            data['form_is_valid'] = False
    else:
        form = CreateTimeSlotModalForm(start=start, end=end, resource_id=resource_id)

    context = {'form': form}
    data['html_form'] = loader.render_to_string("jobtracker/modals/job_slot_create.html",
                                                context,
                                                request=request)
    return JsonResponse(data)


class SlotDeleteView(ChaoticaBaseView, DeleteView):
    """View to delete a slot"""
    model = TimeSlot  
    template_name = "jobtracker/modals/job_slot_delete.html"  

    def get_success_url(self):
        slug = self.kwargs['slug']
        return reverse_lazy('job_schedule', kwargs={'slug': slug})

    def get_context_data(self, **kwargs):
        context = super(SlotDeleteView, self).get_context_data(**kwargs)
        if 'slug' in self.kwargs:
            context['job'] = get_object_or_404(Job, slug=self.kwargs['slug'])
        return context