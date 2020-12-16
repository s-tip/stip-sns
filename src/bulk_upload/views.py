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
        is_merged_single_stix = (request.POST['is_merged_single_stix'].lower()) == 'true'
        stix_title = request.POST['stix_title']
        stix_description = request.POST['stix_description']
        if not stix_title:
            stix_title = 'default'
        if not stix_description:
            stix_description = stix_title

        if is_merged_single_stix:
            upload(request, request.FILES, stix_title, stix_description)
        else:
            counter = 0
            for key, lists in request.FILES.lists():
                files = MultiValueDict({key: lists})
                title = '%s_%04d' % (stix_title, counter)
                description = '%s_%04d' % (stix_description, counter)
                upload(request, files, title, description)
                counter += 1
        return HttpResponse()
    except Exception as e:
        import traceback
        traceback.print_exc()
        return HttpResponseServerError(reason=str(e))


def upload(request, files, title, post):
    publication = request.POST['publication']
    if 'group' in request.POST:
        group = request.POST['group']
    if 'people' in request.POST:
        people = request.POST['people']
    new_post = {}
    new_post['title'] = title
    new_post['post'] = post
    new_post['TLP'] = request.POST['stix_tlp'].upper()
    new_post['publication'] = publication
    request.POST = new_post
    request = get_request_via_confirm_indicator(request)
    if publication == 'group':
        request.POST['group'] = group
    elif publication == 'people':
        request.POST['people'] = people
    post_common(request, request.user)
    return
