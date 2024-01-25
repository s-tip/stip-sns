import json
import traceback
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http.response import HttpResponse, HttpResponseServerError
from django.utils.datastructures import MultiValueDict
from feeds.views import post_common
from api.v1.views import get_request_via_confirm_indicator
from ctirs.models import Group, STIPUser


@login_required
def entry(request):
    users_list = STIPUser.objects.filter(is_active=True).exclude(username='anonymous').order_by('username')
    return render(request, 'bulk_upload_entry.html', {
        'users': users_list,
        'sharing_groups': Group.objects.all(),
    })


@login_required
def post(request):
    try:
        stix_title = request.POST['stix_title']
        stix_description = request.POST['stix_description']
        if not stix_title:
            stix_title = 'default'
        if not stix_description:
            stix_description = stix_title
        tlp = request.POST['stix_tlp'].upper()

        confirm_data = None
        if 'confirm_data' in request.POST:
            if request.POST['confirm_data']:
                confirm_data = json.loads(request.POST['confirm_data'])

        upload(request, stix_title, stix_description, tlp, confirm_data)
        return HttpResponse()
    except Exception:
        traceback.print_exc()
        return HttpResponseServerError()


def upload(request, title, post, tlp, confirm_data):
    publication = request.POST['publication']
    if 'group' in request.POST:
        group = request.POST['group']
    if 'people' in request.POST:
        people = request.POST['people']
    new_post = {}
    new_post['title'] = title
    new_post['post'] = post
    new_post['TLP'] = tlp
    new_post['publication'] = publication
    request.POST = new_post

    if not confirm_data:
        request = get_request_via_confirm_indicator(request)
    else:
        request.POST['indicators'] = json.dumps(confirm_data['indicators'])
        request.POST['tas'] = json.dumps(confirm_data['tas'])
        request.POST['ttps'] = json.dumps(confirm_data['ttps'])

    if publication == 'group':
        request.POST['group'] = group
    elif publication == 'people':
        request.POST['people'] = people
    post_common(request, request.user)
    return
