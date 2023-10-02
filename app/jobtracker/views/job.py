from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponse,HttpResponseRedirect, HttpResponseBadRequest, JsonResponse, HttpResponseForbidden, HttpResponseNotFound
from django.template import loader, Template as tmpl, Context
from guardian.decorators import permission_required_or_403
from guardian.core import ObjectPermissionChecker
from guardian.mixins import PermissionListMixin, PermissionRequiredMixin
from django.views import View
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from chaotica_utils.views import log_system_activity, ChaoticaBaseView, pageDefaults
from chaotica_utils.utils import SendUserNotification
from ..models import *
from ..forms import *
from ..tasks import *
from .helpers import _process_assign_user, _process_assign_contact
import logging
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages 
from django.apps import apps
import json


logger = logging.getLogger(__name__)


@login_required
@permission_required('jobtracker.view_schedule', (Job, 'slug', 'slug'))
def view_job_schedule_slots(request, slug):
    data = []
    job = get_object_or_404(Job, slug=slug)
    slots = TimeSlot.objects.filter(phase__job=job)
    for slot in slots:
        data.append(
            slot.get_web_schedule_format(
                url=reverse('change_job_schedule_slot', kwargs={"slug":job.slug, "pk":slot.pk})
            )
        )
    return JsonResponse(data, safe=False)


@login_required
@permission_required('jobtracker.view_schedule', (Job, 'slug', 'slug'))
def view_job_schedule_members(request, slug):
    data = []
    job = get_object_or_404(Job, slug=slug)
    scheduledUsers = job.get_scheduled_users()
    if scheduledUsers:
        for user in scheduledUsers:
            data.append({
                "id": user.pk,
                "title": str(user),
                "businessHours": {
                    "startTime": job.unit.businessHours_startTime,
                    "endTime": job.unit.businessHours_endTime,
                    "daysOfWeek": job.unit.businessHours_days,
                }
            })
    return JsonResponse(data, safe=False)


@login_required
@permission_required('jobtracker.assign_poc', (Job, 'slug', 'slug'))
def assign_job_poc(request, slug):
    job = get_object_or_404(Job, slug=slug)
    contacts = Contact.objects.filter(company=job.client)
    return _process_assign_contact(request, job, 'primary_client_poc', contacts=contacts)


@login_required
@permission_required('jobtracker.change_job', (Job, 'slug', 'slug'))
def assign_job_field(request, slug, field):
    validFields = [
        'account_manager', 'dept_account_manager',
        'scoped_by', 'scoped_signed_off_by'
    ]
    job = get_object_or_404(Job, slug=slug)
    if field in validFields:
        if field == "scoped_by":
            return _process_assign_user(request, job, field, multiple=True)
        else:
            return _process_assign_user(request, job, field)
    else:
        return HttpResponseBadRequest()


@login_required
@permission_required('jobtracker.change_job', (Job, 'slug', 'slug'))
def assign_job_scoped(request, slug):
    job = get_object_or_404(Job, slug=slug)
    # users = User.objects.filter(is_staff=True)
    # return _process_assign_user(request, job, 'scoped_by', multiple=True, users=users)
    return _process_assign_user(request, job, 'scoped_by', multiple=True)


@login_required
@permission_required('jobtracker.scope_job', (Job, 'slug', 'slug'))
def job_edit_scope(request, slug):
    is_ajax = False
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        is_ajax = True
    
    job = get_object_or_404(Job, slug=slug)
    data = {}
    data['form_is_valid'] = False
    if request.method == 'POST':
        form = ScopeInlineForm(request.POST, instance=job)
        if form.is_valid():
            job = form.save()
            # add activity logs
            data['form_is_valid'] = True
            data['changed_data'] = form.changed_data
            log_system_activity(job, "Scope edited ("+', '.join(form.changed_data)+")")
            if not is_ajax:
                return HttpResponseRedirect(reverse('job_detail', kwargs={'slug': slug}))
    else:
        form = ScopeInlineForm(instance=job)  
    
    context = {'scopeInlineForm': form, 'job': job}
    data['html_form'] = loader.render_to_string("partials/job/forms/scope.html",
                                                context,
                                                request=request)

    return JsonResponse(data)


@permission_required('jobtracker.change_schedule', (Job, 'slug', 'slug'))
def change_job_schedule_slot(request, slug, pk=None):
    job = get_object_or_404(Job, slug=slug)
    slot = None
    if pk:
        slot = get_object_or_404(TimeSlot, pk=pk, phase__job=job)
    data = dict()
    if request.method == "POST":
        form = ChangeTimeSlotModalForm(request.POST, instance=slot, slug=slug)
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
        else:
            data['form_is_valid'] = False
    else:
        # Send the modal
        form = ChangeTimeSlotModalForm(instance=slot, slug=slug)

    context = {'form': form, 'job': job}
    data['html_form'] = loader.render_to_string("jobtracker/modals/job_slot.html",
                                                context,
                                                request=request)
    return JsonResponse(data)


@login_required
@permission_required('jobtracker.add_note', (Job, 'slug', 'slug'))
def JobCreateNote(request, slug):
    job = get_object_or_404(Job, slug=slug)
    data = dict()
    if request.method == 'POST':
        form = AddNote(request.POST)
        if form.is_valid():
            newNote = form.save(commit=False)
            newNote.content_object = job
            newNote.author = request.user
            newNote.is_system_note = False
            newNote.save()
            return HttpResponseRedirect(reverse('job_detail', kwargs={"slug": slug})+"#notes")
    return HttpResponseBadRequest()


class JobBaseView(ChaoticaBaseView, View):
    model = Job
    fields = '__all__'

    def get_success_url(self):
        if 'slug' in self.kwargs:
            slug = self.kwargs['slug']
            return reverse_lazy('job_detail', kwargs={'slug': slug})
        else:
            return reverse_lazy('job_list')

    def get_context_data(self, **kwargs):
        context = super(JobBaseView, self).get_context_data(**kwargs)
        noteForm = AddNote()
        context['noteForm'] = noteForm
        return context


class JobListView(JobBaseView, ListView):
    def get_queryset(self):
        # Only return jobs with:
        # - permission
        # - isn't deleted
        # - isn't archived
        # get our units 
        units = OrganisationalUnit.objects.filter(
            pk__in=self.request.user.unit_memberships.filter(role__in=UnitRoles.getRolesWithPermission('jobtracker.view_job')).values_list('unit').distinct())
        myJobs = get_objects_for_user(self.request.user, 'jobtracker.view_job')
        jobs = Job.objects.filter(Q(unit__in=units)|Q(pk__in=myJobs)).exclude(status=JobStatuses.DELETED).exclude(status=JobStatuses.ARCHIVED)
        return jobs


# @permission_required('jobtracker.view_job', (Job, 'slug', 'slug'))
class JobDetailView(PermissionRequiredMixin, JobBaseView, DetailView):
    permission_required = 'jobtracker.view_job'

    def check_permissions(self, request):
        obj = self.get_permission_object()
        checker = ObjectPermissionChecker(self.request.user)
        if obj:
            if self.request.user.is_authenticated:
                units = OrganisationalUnit.objects.filter(
                    pk__in=self.request.user.unit_memberships.filter(
                        role__in=UnitRoles.getRolesWithPermission('jobtracker.view_job')).values_list('unit').distinct()
                        )
                
                if obj.unit in units:
                    return None
                elif checker.has_perm('view_job', obj):
                    return None
            else:
                from django.contrib.auth.views import redirect_to_login
                login_url = settings.LOGIN_URL
                return redirect_to_login(request.get_full_path(),
                                        login_url,
                                        'next')
        return HttpResponseForbidden()

    def get_context_data(self, **kwargs):
        context = super(JobDetailView, self).get_context_data(**kwargs)
        
        scopeInlineForm = ScopeInlineForm(instance=context['job'])
        context['scopeInlineForm'] = scopeInlineForm

        return context


class JobCreateView(JobBaseView, CreateView):
    template_name = "jobtracker/job_form_create.html"
    form_class = JobForm
    fields = None

    # Permissions are handled in the unit selection box... weirdly!

    def get_success_url(self):
        return reverse_lazy('job_detail', kwargs={'slug': self.object.slug})

    def get_form_kwargs(self):
        kwargs = super(JobCreateView, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.save()
        log_system_activity(form.instance, "Created Job")
        return super().form_valid(form)
    

class JobUpdateView(PermissionRequiredMixin, JobBaseView, UpdateView):
    permission_required = 'jobtracker.change_job'
    return_403 = True
    template_name = "jobtracker/job_form_edit.html"
    form_class = JobForm
    fields = None
    """View to update a job"""

    def get_form_kwargs(self):
        kwargs = super(JobUpdateView, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        log_system_activity(form.instance, "Job Updated")
        return super().form_valid(form)


class JobUpdateScopeView(PermissionRequiredMixin, JobBaseView, UpdateView):
    permission_required = 'jobtracker.scope_job'
    return_403 = True
    model = Job
    template_name = "jobtracker/job_form_scope.html"
    form_class = ScopeForm
    fields = None

    def get_form_kwargs(self):
        kwargs = super(JobUpdateView, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        log_system_activity(form.instance, "Scope Updated")
        return super().form_valid(form)    


class JobScheduleView(PermissionRequiredMixin, JobBaseView, DetailView):
    permission_required = 'jobtracker.view_schedule'
    return_403 = True
    """ Renders the schedule for the job """
    template_name = "jobtracker/job_schedule.html"

    def get_context_data(self, **kwargs):
        context = super(JobScheduleView, self).get_context_data(**kwargs)
        userSelect = AssignUserField()
        context['userSelect'] = userSelect
        context['TimeSlotDeliveryRoles'] = TimeSlotDeliveryRole.CHOICES

        typesInUse = context['job'].get_all_total_scheduled_by_type()
        context['TimeSlotDeliveryRolesInUse'] = typesInUse
        return context
    

class JobDeleteView(PermissionRequiredMixin, JobBaseView, DeleteView):
    permission_required = 'jobtracker.delete_job'
    return_403 = True
    """View to delete a job"""
        

@login_required
def JobUpdateWorkflow(request, slug, newState):
    job = get_object_or_404(Job, slug=slug)
    data = dict()
    newStateStr = None
    try:
        for state in JobStatuses.CHOICES:
            if state[0] == newState:
                newStateStr = state[1]
        if newStateStr == None:
            raise TypeError()
    except Exception:
        return HttpResponseBadRequest()
    
    canProceed = True
        
    if newState == JobStatuses.PENDING_SCOPE:
        if job.can_to_pending_scope(request):
            if request.method == 'POST':
                job.to_pending_scope()
        else:
            canProceed = False
    elif newState == JobStatuses.SCOPING:
        if job.can_to_scoping(request):
            if request.method == 'POST':

                if not job.scoped_by.all():
                    if request.user.has_perm('scope_job'):
                        # No one is defined to scope and we have permission - auto add!
                        job.scoped_by.add(request.user)
                        job.save()
                job.to_scoping()
        else:
            canProceed = False
    elif newState == JobStatuses.SCOPING_ADDITIONAL_INFO_REQUIRED:
        if job.can_to_additional_scope_req(request):
            if request.method == 'POST':
                job.to_additional_scope_req()
        else:
            canProceed = False
    elif newState == JobStatuses.PENDING_SCOPING_SIGNOFF:
        if job.can_to_scope_pending_signoff(request):
            if request.method == 'POST':
                job.to_scope_pending_signoff()
        else:
            canProceed = False
    elif newState == JobStatuses.SCOPING_COMPLETE:
        if job.can_to_scope_complete(request):
            if request.method == 'POST':
                job.to_scope_complete(user=request.user)
        else:
            canProceed = False
    elif newState == JobStatuses.PENDING_START:
        if job.can_to_pending_start(request):
            if request.method == 'POST':
                job.to_pending_start()
        else:
            canProceed = False
    elif newState == JobStatuses.IN_PROGRESS:
        if job.can_to_in_progress(request):
            if request.method == 'POST':
                job.to_in_progress()
        else:
            canProceed = False
    elif newState == JobStatuses.COMPLETED:
        if job.can_to_complete(request):
            if request.method == 'POST':
                job.to_complete()
        else:
            canProceed = False
    elif newState == JobStatuses.LOST:
        if job.can_to_lost(request):
            if request.method == 'POST':
                job.to_lost()
        else:
            canProceed = False
    elif newState == JobStatuses.DELETED:
        if job.can_to_delete(request):
            if request.method == 'POST':
                job.to_delete()
        else:
            canProceed = False
    elif newState == JobStatuses.ARCHIVED:
        if job.can_to_archive(request):
            if request.method == 'POST':
                job.to_archive()
        else:
            canProceed = False
    else:
        return HttpResponseBadRequest()

        # sendWebHookStatusAlert(redteam=rt, title="Engagement Status Changed", msg="Engagement "+rt.projectName+" status has changed to: "+str(dict(RTState.choices).get(newState)))
        
    if request.method == 'POST' and canProceed:
        job.save()
        data['form_is_valid'] = True  # This is just to play along with the existing code
    
    tasks = WorkflowTasks.objects.filter(appliedModel=WorkflowTasks.WF_JOB, status=newState)
    context = {
        'job': job,
        'canProceed': canProceed,
        'newStateStr': newStateStr,
        'newState': newState,
        'tasks': tasks,
        }
    data['html_form'] = loader.render_to_string('jobtracker/modals/job_workflow.html',
                                                context,
                                                request=request)
    return JsonResponse(data)