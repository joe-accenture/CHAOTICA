from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.template import loader
from chaotica_utils.views import log_system_activity, ChaoticaBaseView, pageDefaults
from chaotica_utils.utils import *
from ..models import *
from ..forms import *
from ..tasks import *
import logging
from django.contrib.auth.decorators import login_required
import uuid

logger = logging.getLogger(__name__)


@login_required
def run_tasks(request):
    """A view that manually runs tasks normally run in the background.

    Args:
        request (HttpRequest): The request

    Returns:
        HttpResponse: A redirect
    """
    task_progress_job_workflows.delay()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required
def view_scheduler(request):
    context = {}
    template = loader.get_template('scheduler.html')
    context = {**context, **pageDefaults(request)}
    return HttpResponse(template.render(context, request))

@login_required
def reset_cal_feed(request):    
    # Okay, lets go!    
    data = dict()
    if request.method == "POST":        
        data['form_is_valid'] = False
        # We need to check which button was pressed... accept or reject!
        if request.POST.get('user_action') == "approve_action":
            # Approve it!
            request.user.schedule_feed_id = uuid.uuid4()
            request.user.save()
            data['form_is_valid'] = True
            data['next'] = reverse('view_own_profile')        

    context = {}
    data['html_form'] = loader.render_to_string("modals/feed_reset.html",
                                                context,
                                                request=request)
    return JsonResponse(data)


@login_required
def reset_cal_family_feed(request):    
    # Okay, lets go!    
    data = dict()
    if request.method == "POST":        
        data['form_is_valid'] = False
        # We need to check which button was pressed... accept or reject!
        if request.POST.get('user_action') == "approve_action":
            # Approve it!
            request.user.schedule_feed_family_id = uuid.uuid4()
            request.user.save()
            data['form_is_valid'] = True
            data['next'] = reverse('view_own_profile')        

    context = {}
    data['html_form'] = loader.render_to_string("modals/feed_family_reset.html",
                                                context,
                                                request=request)
    return JsonResponse(data)


@login_required
def view_stats(request):
    context = {}
    template = loader.get_template('stats.html')
    context = {**context, **pageDefaults(request)}
    return HttpResponse(template.render(context, request))


@login_required
def view_reports(request):
    context = {}
    template = loader.get_template('reports.html')
    context = {**context, **pageDefaults(request)}
    return HttpResponse(template.render(context, request))
