from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.conf import settings as django_settings
from django.template import loader, Template as tmpl, Context
from django.http import HttpResponseForbidden, JsonResponse, HttpResponse, HttpResponseRedirect, Http404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
import json, os, random
from .forms import *
from .models import *
from .enums import *
from .utils import *
from dal import autocomplete
from django.db.models import Q, Sum
from django.utils.html import format_html
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.admin.views.decorators import staff_member_required
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from guardian.shortcuts import get_objects_for_user, assign_perm, remove_perm
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib import messages 
from django.shortcuts import get_object_or_404
from constance import config
from .tasks import task_updateHolidays
from django.views.decorators.http import require_http_methods, require_safe
    

def pageDefaults(request):
    from jobtracker.models import Job, Phase
    context = {}
    context['notifications'] = Notification.objects.filter(user=request.user)
    context['config'] = config

    myJobs = Job.objects.jobs_for_user(request.user)
    context['myJobs'] = myJobs
    myPhases = Phase.objects.phases_for_user(request.user)
    context['myPhases'] = myPhases
    return context


def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


@login_required
@require_safe
def updateHolidays(request):
    task_updateHolidays(request)
    return HttpResponse("")
    return HttpResponseRedirect(reverse('home'))


@require_safe
def trigger_error(request):
    division_by_zero = 1 / 0


@require_safe
def test_notification(request):
    SendUserNotification(
        request.user, NotificationTypes.SYSTEM,
        "Test Notification", "This is a test notification. At ease.",
        "emails/test_email.html")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@require_safe
def maintenance(request):
    if not settings.MAINTENANCE_MODE:
        return HttpResponseRedirect(reverse('home'))
    return render(request, 'maintenance.html')


@login_required
@require_safe
def view_own_leave(request):
    from jobtracker.models import Skill, UserSkill
    context = {}
    leave_list = LeaveRequest.objects.filter(user=request.user)
    context = {
        'leave_list': leave_list,
        }
    template = loader.get_template('view_own_leave.html')
    context = {**context, **pageDefaults(request)}
    return HttpResponse(template.render(context, request))


@login_required
@require_http_methods(["POST", "GET"])
def request_leave(request):
    if request.method == "POST":
        form = LeaveRequestForm(request.POST)
        if form.is_valid():
            leave = form.save(commit=False)
            leave.user = request.user
            leave.save()
            return HttpResponseRedirect(reverse('view_own_leave'))
    else:
        form = LeaveRequestForm()
    
    context = {'form': form}
    template = loader.get_template('forms/add_leave_form.html')
    context = {**context, **pageDefaults(request)}
    return HttpResponse(template.render(context, request))


@login_required
@require_safe
def manage_leave(request):
    from jobtracker.models import Skill, UserSkill
    context = {}
    leave_list = LeaveRequest.objects.filter()
    context = {
        'leave_list': leave_list,
        }
    template = loader.get_template('manage_leave.html')
    context = {**context, **pageDefaults(request)}
    return HttpResponse(template.render(context, request))


@login_required
@require_safe
def view_own_profile(request):
    from jobtracker.models import Skill, UserSkill
    context = {}
    skills = Skill.objects.all()
    languages = Language.objects.all()
    userSkills = UserSkill.objects.filter(user=request.user)
    profileForm = ProfileBasicForm(instance=request.user)
    context = {
        'skills': skills, 
        'userSkills': userSkills,
        'languages': languages,
        'profileForm': profileForm,
        }
    template = loader.get_template('profile.html')
    context = {**context, **pageDefaults(request)}
    return HttpResponse(template.render(context, request))


@login_required
@require_http_methods(["POST", "GET"])
def update_own_profile(request):
    data = {}
    data['form_is_valid'] = False
    if request.method == "POST":
        form = ProfileBasicForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
            data['changed_data'] = form.changed_data
    else:
        form = ProfileBasicForm(instance=request.user)
    
    context = {'profileForm': form}
    data['html_form'] = loader.render_to_string("partials/profile/basic_profile_form.html",
                                                context,
                                                request=request)

    return JsonResponse(data)


@login_required
@require_safe
def notifications_feed(request):
    data = {}
    data['notifications'] = []
    notifications = Notification.objects.filter(user=request.user)
    if is_ajax(request):
        for notice in notifications:
            data['notifications'].append({
                "title": notice.title,
                "msg": notice.message,
                "icon": notice.icon,
                "timestamp": notice.timestamp,
                "is_read": notice.is_read,
                "url": notice.link,
            }
        )    
        context = {'notifications': notifications,}
        data['html_form'] = loader.render_to_string("partials/notifications.html",
                                                    context,
                                                    request=request)
        return JsonResponse(data)
    else:
        return HttpResponseForbidden()


@login_required
@require_safe
def notifications_mark_read(request):
    notifications = Notification.objects.filter(user=request.user, is_read=False)
    for notice in notifications:
        notice.is_read = True
        notice.save()
    data = {
        'result': True
    }
    return JsonResponse(data, safe=False)

@login_required
@require_safe
def update_own_theme(request):
    if 'mode' in request.GET:
        mode = request.GET.get('mode', 'light')
        validModes = ['dark', 'light']
        if mode in validModes:
            request.user.site_theme = mode
            request.user.save()
            return HttpResponse("OK")    
    return HttpResponseForbidden()


@login_required
@require_http_methods(["POST", "GET"])
def update_own_skills(request):
    from jobtracker.models import Skill, UserSkill
    if request.method == "POST":
        # Lets loop through the fields!
        for field in request.POST:
            # get skill..
            try:
                skill = Skill.objects.get(slug=field)
                value = int(request.POST.get(field))
                skill, added = UserSkill.objects.get_or_create(
                    user=request.user, skill=skill)
                if skill.rating != value:
                    skill.rating = value
                    skill.last_updated_on = timezone.now()
                    skill.save()
            except:
                # invalid skill!
                pass


        return HttpResponseRedirect(reverse('view_own_profile'))
    else:
        return HttpResponseRedirect(reverse('view_own_profile'))


@staff_member_required
@require_http_methods(["POST", "GET"])
def app_settings(request):
    context = {}
    if request.method == "POST":
        form = CustomConfigForm(request.POST)
        if form.is_valid():
            form.save()
        else:
            messages.error(request, "Form is invalid")
        return HttpResponseRedirect(reverse('app_settings'))
    else:
        # Send the modal
        form = CustomConfigForm(initial=settings.CONSTANCE_CONFIG)

    context = {'app_settings': form}
    template = loader.get_template('app_settings.html')
    context = {**context, **pageDefaults(request)}
    return HttpResponse(template.render(context, request))


@staff_member_required
@require_http_methods(["POST", "GET"])
def user_assign_global_role(request, username):
    user = get_object_or_404(User, username=username)
    data = dict()
    if request.method == 'POST':
        form = AssignRoleForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True         
        else:
            data['form_is_valid'] = False
    else:
        form = AssignRoleForm(instance=user)
    
    context = {'form': form,}
    data['html_form'] = loader.render_to_string("modals/assign_user_role.html",
                                                context,
                                                request=request)
    return JsonResponse(data)


@staff_member_required
@require_http_methods(["POST", "GET"])
def import_site_data(request):
    return HttpResponseForbidden()
    data = dict()
    if request.method == 'POST':
        form = ImportSiteDataForm(request.POST)
        if form.is_valid():
            # lets process the file!
            importFile = request.FILES['importFile']
            if importFile:
                try:


                    data['form_is_valid'] = True

                except ValueError:
                    data['form_is_valid'] = False
                    messages.error(request, "File was not a valid JSON import")
            else:
                data['form_is_valid'] = False            
        else:
            data['form_is_valid'] = False
    else:
        form = ImportSiteDataForm()
    
    context = {'form': form,}
    data['html_form'] = loader.render_to_string("modals/import_site_data.html",
                                                context,
                                                request=request)
    return JsonResponse(data)


@staff_member_required
@require_http_methods(["GET"])
def export_site_data(request):
    return HttpResponseForbidden()


class ChaoticaBaseView(LoginRequiredMixin, View):
    """Base view to enforce everything else"""

    def form_invalid(self, form):
        response = super().form_invalid(form)
        if self.request.accepts("text/html"):
            return response
        else:
            return JsonResponse(form.errors, status=400)

    def form_valid(self, form):
        # We make sure to call the parent's form_valid() method because
        # it might do some processing (in the case of CreateView, it will
        # call form.save() for example).
        response = super().form_valid(form)
        if self.request.accepts("text/html"):
            return response
        else:
            data = {
                "pk": self.object.pk,
            }
        return JsonResponse(data)
    
    def get_context_data(self,*args, **kwargs):
        context = super(ChaoticaBaseView, self).get_context_data(*args,**kwargs)
        context = {**context, **pageDefaults(self.request)}
        return context


class ChaoticaBaseGlobalRoleView(ChaoticaBaseView, UserPassesTestMixin):

    role_required = None

    def test_func(self):
        # Check if the user is in the global admin group
        grp = Group.objects.get(name=settings.GLOBAL_GROUP_PREFIX+GlobalRoles.CHOICES[GlobalRoles.ADMIN][1])
        if self.role_required:
            return self.request.user.groups.filter(
                name=settings.GLOBAL_GROUP_PREFIX+GlobalRoles.CHOICES[self.role_required][1]).exists()
        else:
            return False


class ChaoticaBaseAdminView(ChaoticaBaseView, UserPassesTestMixin):

    def test_func(self):
        # Check if the user is in the global admin group
        return self.request.user.groups.filter(name=settings.GLOBAL_GROUP_PREFIX+GlobalRoles.CHOICES[GlobalRoles.ADMIN][1])


def log_system_activity(refObj, msg):
    noteNote = Note(content=msg,
                 is_system_note=True,
                 content_object=refObj)
    noteNote.save()


@require_safe
def get_quote(request):
    lines = json.load(open(os.path.join(django_settings.BASE_DIR, 'chaotica_utils/templates/quotes.json')))
    random_index = random.randint(0, len(lines)-1)
    return JsonResponse(lines[random_index])


@require_http_methods(["POST", "GET"])
def signup(request):
    if request.user.is_authenticated:
        pprint(request.user)
        return redirect('home')
    else:
        if request.method == 'POST':
            form = ChaoticaUserForm(request.POST)
            if form.is_valid():
                form.save()
                username = form.cleaned_data.get('username')
                raw_password = form.cleaned_data.get('password1')
                user = authenticate(username=username, password=raw_password)
                login(request, user)
                return redirect('home')
        else:
            form = ChaoticaUserForm()
        return render(request, 'signup.html', {'form': form})


class UserBaseView(ChaoticaBaseGlobalRoleView):
    model = User
    fields = '__all__'
    success_url = reverse_lazy('user_list')
    role_required = GlobalRoles.ADMIN

    def get_context_data(self, **kwargs):
        context = super(UserBaseView, self).get_context_data(**kwargs)
        return context

    def get_queryset(self) :
        queryset = User.objects.all().exclude(username="AnonymousUser")
        return queryset

class UserListView(UserBaseView, ListView):
    """View to list all jobs.
    Use the 'job_list' variable in the template
    to access all job objects"""

class UserDetailView(UserBaseView, DetailView):

    def get_object(self, queryset=None):
        if self.kwargs.get('username'):
            return get_object_or_404(User, username=self.kwargs.get('username'))
        else:
            raise Http404()

class UserCreateView(UserBaseView, CreateView):
    form_class = ChaoticaUserForm
    fields = None

    def form_valid(self, form):
        return super(UserCreateView, self).form_valid(form)

class UserUpdateView(UserBaseView, UpdateView):
    form_class = ChaoticaUserForm
    fields = None

class UserDeleteView(UserBaseView, DeleteView):
    """View to delete a job"""


######################################
# Autocomplete fields
######################################

class UserAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated:
            return User.objects.none()
        # TODO: Do permission checks...
        qs = User.objects.all()
        if self.q:
            qs = qs.filter(
                Q(username__icontains=self.q) |
                Q(first_name__icontains=self.q) |
                Q(last_name__icontains=self.q), is_active=True).order_by('username')
        return qs

    # def get_result_label(self, result):
    #     return format_html('{} {}', result.first_name, result.last_name)


# class JobAutocomplete(autocomplete.Select2QuerySetView):
#     def get_queryset(self):
#         # Don't forget to filter out results depending on the visitor !
#         if not self.request.user.is_authenticated:
#             return Job.objects.none()
#         # TODO: Do permission checks...
#         qs = Job.objects.all()
#         if self.q:
#             qs = qs.filter()
#         return qs

#     # def get_result_label(self, result):
#     #     return format_html('{} {}', result.first_name, result.last_name)


@login_required
@csrf_exempt
def SiteSearch(request):
    data = {}
    context = {}
    q = request.POST.get('q', '').capitalize()
    results_count = 0
    from jobtracker.models import Job, Phase, Client, Service, Skill, BillingCode
    if is_ajax(request):
        if len(q) > 2:
            ## Jobs
            jobs_search = get_objects_for_user(request.user, 'jobtracker.view_job', Job.objects.all()).filter(
                Q(title__icontains=q) | Q(scoping_information__icontains=q) | Q(slug__icontains=q)
                 | Q(id__icontains=q))
            context['search_jobs'] = jobs_search
            results_count = results_count + jobs_search.count()

            ## Phases
            phases_search = Phase.objects.filter(
                Q(title__icontains=q) | Q(description__icontains=q) | Q(phase_id__icontains=q),
                job__in=jobs_search,)
            context['search_phases'] = phases_search
            results_count = results_count + phases_search.count()

            ## Clients
            cl_search = Client.objects.filter(
                Q(name__icontains=q))
            context['search_clients'] = cl_search
            results_count = results_count + cl_search.count()

            ## BillingCodes
            bc_search = BillingCode.objects.filter(
                Q(code__icontains=q))
            context['search_billingCodes'] = bc_search
            results_count = results_count + bc_search.count()

            ## Services
            sv_search = Service.objects.filter(
                Q(name__icontains=q))
            context['search_services'] = sv_search
            results_count = results_count + sv_search.count()

            ## Skills
            sk_search = Skill.objects.filter(
                Q(name__icontains=q))
            context['search_skills'] = sk_search
            results_count = results_count + sk_search.count()

            ## Users
            if request.user.is_superuser:
                us_search = User.objects.filter(
                    Q(username__icontains=q) | Q(first_name__icontains=q) | Q(last_name__icontains=q)
                )
                context['search_users'] = us_search
                results_count = results_count + us_search.count()
        
    context['results_count'] = results_count
    
    # Get research searches?
    context['recentSearches'] = None

    context['q'] = q
    data['html_form'] = loader.render_to_string("partials/search-results.html",
                                                context,
                                                request=request)

    return JsonResponse(data)