import json

from django.http import (HttpResponseBadRequest, HttpResponse,)
from ctirs.models import STIPUser
from django.views.decorators.csrf import csrf_exempt
from django.http.response import HttpResponseNotAllowed
from feeds.views import KEY_ANONYMOUS, KEY_USERNAME, post_common, confirm_indicator


@csrf_exempt
def post(request):
    POST_KEY_NO_EXTRACT = 'no_extract'
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    try:
        # anonymous投稿か？
        if KEY_ANONYMOUS in request.POST:
            # 投稿ユーザーはアノニマス
            user = STIPUser.get_anonymous_user()
        else:
            # usernameがない
            if KEY_USERNAME not in request.POST:
                raise Exception('No username.')
            # user情報取得
            try:
                username = request.POST[KEY_USERNAME]
                user = STIPUser.objects.get(username=username)
            except BaseException:
                raise Exception('Invalid username(%s)' % (username))
        # extract フラグ
        extract = True
        if POST_KEY_NO_EXTRACT in request.POST:
            extract = False

        if extract:
            # indicators 取得
            request.user = user
            # confirm_indicators から再度 post するデータを取得する
            request = get_request_via_confirm_indicator(request)
        feed = post_common(request, user)

        dump = {
            'status': 'OK',
            'reason': 'Successfully',
            'id': str(feed.package_id)
        }
        data = json.dumps(dump)
        return HttpResponse(data, content_type='application/json')
    except Exception as e:
        dump = {'status': 'NG',
                'reason': str(e)}
        data = json.dumps(dump)
        return HttpResponseBadRequest(data, content_type='application/json')


# RestAPI, Slack 共通
def get_request_via_confirm_indicator(request):
    json_response = confirm_indicator(request)
    j = json.loads(json_response.content)
    # confirm_indicators から再度 post するデータを取得する
    request.POST = get_post_common_post(
        request.POST.copy(), j, request.user.confidence)
    return request


def get_post_common_post(temp_post, j, confidence):
    d = {}
    d['indicators'] = _get_indicators(j, confidence)
    d['tas'] = _get_tas(j, confidence)
    d['ttps'] = _get_ttps(j, confidence)
    d['custom_objects'] = []
    d['other'] = []
    temp_post['confirm_data'] = d
    return temp_post


def _get_indicators(json_response, confidence):
    temp_indicators = []
    for title in json_response['indicators'].keys():
        indicators = json_response['indicators'][title]
        for indicator in indicators:
            item = {}
            item['type'] = indicator[0]
            item['value'] = indicator[1]
            item['title'] = indicator[2]
            item['confidence'] = confidence
            temp_indicators.append(item)
    return temp_indicators


def _get_tas(json_response, confidence):
    temp_tas = []
    for title in json_response['tas'].keys():
        tas = json_response['tas'][title]
        for ta in tas:
            item = {}
            item['value'] = ta[1]
            item['title'] = ta[2]
            item['confidence'] = confidence
            temp_tas.append(item)
    return temp_tas


def _get_ttps(json_response, confidence):
    temp_ttps = []
    for title in json_response['ttps'].keys():
        ttps = json_response['ttps'][title]
        for ttp in ttps:
            item = {}
            item['value'] = ttp[1]
            item['title'] = ttp[2]
            item['confidence'] = confidence
            temp_ttps.append(item)
    return temp_ttps
