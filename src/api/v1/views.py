import json

from django.http import (HttpResponseBadRequest, HttpResponse,)
from ctirs.models import STIPUser
from django.views.decorators.csrf import csrf_exempt
from django.http.response import HttpResponseNotAllowed
from feeds.views import KEY_ANONYMOUS,KEY_USERNAME,post_common

@csrf_exempt
def post(request):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])
    
    try:
        #anonymous投稿か？
        if KEY_ANONYMOUS in request.POST:
            #投稿ユーザーはアノニマス
            user = STIPUser.get_anonymous_user()
        else:
            #usernameがない
            if KEY_USERNAME not in request.POST:
                raise Exception('No username.')
            #user情報取得
            try:
                username = request.POST[KEY_USERNAME]
                user = STIPUser.objects.get(username=username)
            except:
                raise Exception('Invalid username(%s)' % (username))

        #POSTする
        feed = post_common(request,user)
        
        dump = {
            'status' : 'OK',
            'reason' : 'Successfully',
            'id' : str(feed.package_id)
                }
        data = json.dumps(dump)
        return HttpResponse(data, content_type='application/json')
    except Exception as e:
        dump = {'status' : 'NG',
                'reason' : str(e)}
        data = json.dumps(dump)
        return HttpResponseBadRequest(data, content_type='application/json')








