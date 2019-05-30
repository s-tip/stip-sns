# -*- coding: utf-8 -*-
import io
import os
import pytz
import json
import hashlib
import tempfile
import codecs
import traceback
import StringIO
import datetime
import threading
import zipfile
import ctirs.models.sns.feeds.rs as rs
import stip.common.const as const

from decorators import ajax_required
try:
    from jira import JIRA
    imported_jira = True
except ImportError:
    imported_jira = False

from stix.core.stix_package import STIXPackage
from stix.extensions.marking.ais import AISMarkingStructure  # @UnusedImport
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse,HttpResponseServerError
from django.shortcuts import get_object_or_404, render
from django.template.context_processors import csrf
from django.template.loader import render_to_string
from django.http.response import JsonResponse

from ctirs.models import STIPUser
from ctirs.models import Feed,AttachFile,SNSConfig
from feeds.feed_stix import FeedStix
from feeds.feed_pdf import FeedPDF
from feeds.feed_stix_like import FeedStixLike
from feeds.feed_stix_comment import FeedStixComment
from ctirs.models import Group
from feeds.extractor.base import Extractor
from feeds.adapter.crowd_strike import search_indicator,get_report_info
from feeds.feed_stix2 import get_stix2_bundle

FEEDS_NUM_PAGES = 10

KEY_USERNAME = 'username'
KEY_TLP = 'TLP'
KEY_TITLE = 'title'
KEY_POST = 'post'
KEY_ANONYMOUS = 'anonymous'
KEY_PUBLICATION = 'publication'
KEY_REFERRED_URL = 'referred_url'
KEY_GROUP = 'group'
KEY_PEOPLE = 'people'
KEY_INDICATORS = 'indicators'
KEY_TTPS = 'ttps'
KEY_TAS = 'tas'
KEY_STIX2 = 'stix2'
KEY_STIX2_TITLES = 'stix2_titles'
KEY_STIX2_CONTENTS = 'stix2_contents'
KEY_ATTACH_CONFIRM = 'attach_confirm'

PUBLICATION_VALUE_GROUP = 'group'
PUBLICATION_VALUE_PEOPLE = 'people'
PUBLICATION_VALUE_ALL = 'all'

DEFAULT_GV_PORT = 10000
L2_GV_PATH = '/L2'

@login_required
def feeds(request):
    feeds = Feed.get_feeds(
        api_user=request.user,
        index=0,
        size=FEEDS_NUM_PAGES)
    #最終更新時間
    last_reload = str(datetime.datetime.now())
    #anonymous以外の全ユーザを返却する
    users_list = STIPUser.objects.filter(is_active=True).exclude(username='anonymous').order_by('username')
    
    if feeds:
        #feedsがあれば、 last_feedを一番最新のfeed id に指定する　
        from_feed = feeds[0].package_id
    else:
        from_feed = None
        

    r = render(request, 'feeds/feeds.html', {
        'feeds': feeds,
        'jira': imported_jira,
        'from_feed': from_feed,
        'last_reload': last_reload,
        'page': 1,
        'users': users_list,
        'sharing_groups' : Group.objects.all(),
        })
    r.set_cookie(key='username',value=str(request.user))
    return r

def feed(request, pk):
    feed = get_object_or_404(Feed, pk=pk)
    return render(request, 'feeds/feed.html', {
        'feed': feed,
        'jira': imported_jira,
        })


@login_required
@ajax_required
#次のページの読み込み時に呼ばれる
def load(request):
    from_feed = request.GET.get('from_feed')
    page = int(request.GET.get('page'))
    feed_source = request.GET.get('feed_source')
    user_id = None
    if feed_source is not None:
        if feed_source != 'all':
            user_id = feed_source
    #from_feed 指定の STIXPacakge ID の produced 時間を取得する
    if from_feed != 'None':
        #from_feed が設定されている場合
        package_from_feed = rs.get_package_info_from_package_id(request.user,from_feed) 
        produced_str = package_from_feed['produced']

        #RS から produced 時間より古い最新の Feed を取得する
        last_reload = Feed.get_datetime_from_string(produced_str)

        #Feed 取得する
        index = (page - 1) * FEEDS_NUM_PAGES
        feeds = Feed.get_feeds(
            api_user=request.user,
            last_reload=last_reload,
            user_id=user_id,
            index=index,
            size=FEEDS_NUM_PAGES)
    else:
        #from_feed が設定されていない場合 (投稿がない場合)
        feeds = []
    html = ''
    csrf_token = (csrf(request)['csrf_token'])
    for feed in feeds:
        html = '{0}{1}'.format(html,
                               render_to_string('feeds/partial_feed.html',
                                                {
                                                    'feed': feed,
                                                    'jira': imported_jira,
                                                    'user': request.user,
                                                    'csrf_token': csrf_token,
                                                    }).encode('utf-8'))

    return HttpResponse(html)


def _html_feeds(last_feed_datetime, user, csrf_token, feed_source='all'):
    user_id = None
    if feed_source != 'all':
        user_id = feed_source
    feeds = Feed.get_feeds_after(last_feed_datetime=last_feed_datetime,api_user=user,user_id=user_id)
    html = ''
    for feed in feeds:
        html = '{0}{1}'.format(html,
                               render_to_string('feeds/partial_feed.html',
                                                {
                                                    'feed': feed,
                                                    'jira': imported_jira,
                                                    'user': user,
                                                    'csrf_token': csrf_token
                                                    }).encode('utf-8'))

    return html


#string から datetime型を取得する (YYYYMMDDHHMMSS)
def get_datetime_from_string(s):
    try:
        local_time_dt = datetime.datetime.strptime(s,'%Y%m%d%H%M%S.%f')
        #UTC に直して返却
        ret =  pytz.utc.localize(local_time_dt)
    except:
        #取得できない場合は UTC の現在時刻とする
        ret = datetime.datetime.now(tz=pytz.utc)
    return ret

@login_required
@ajax_required
def load_new(request):
    last_feed_datetime = get_datetime_from_string(request.GET.get('last_feed'))
    user = request.user
    csrf_token = (csrf(request)['csrf_token'])
    html = _html_feeds(last_feed_datetime, user, csrf_token)
    return HttpResponse(html)


@login_required
@ajax_required
def check(request):
    last_feed_datetime = get_datetime_from_string(request.GET.get('last_feed'))
    #feed_source は 全員のフィード取得の際は ALL,それ以外は STIPUserのid数値文字列
    feed_source = request.GET.get('feed_source')
    user = None
    if feed_source != 'all':
        user = feed_source
    #引数 rs 呼び出し用api_user,user(全員の場合はNone,それ以外はid STIP UserのID数値文字列)
    feeds = Feed.get_feeds_after(last_feed_datetime=last_feed_datetime,api_user=request.user,user_id=user)
    count = len(feeds)
    return HttpResponse(count)

def check_via_poll(request):
    last_feed_datetime = get_datetime_from_string(request.GET.get('last_feed'))
    feed_source = request.GET.get('feed_source')
    feed_source = feed_source if feed_source is not None else 'all'
    username = request.GET.get('username')
    user = STIPUser.objects.get(username=username)
    feeds = Feed.get_feeds_after(last_feed_datetime=last_feed_datetime,api_user=user)
    if feed_source != 'all':
        feeds = feeds.filter(user__id=feed_source)
    count = len(feeds)
    return HttpResponse(count)

#同一の language が複数指定されているかどうか確認する
def is_duplicate_languages(values):
    languages = []
    for value in values:
        language = value[u'language']
        if language in languages:
            return True
        languages.append(language)
    return False

#Web経由 / REST API 経由共通
def post_common(request,user):
    #Feed作成
    feed = Feed()
    #ManyToMany をクリアする
    feed.files.clear()
    feed.sharing_people.clear()
    #POSTデータ格納
    if request.POST.has_key(KEY_POST) == False:
        raise Exception('No Post.')
    post = request.POST[KEY_POST]
    post = post.strip()
    if len(post) == 0:
        raise Exception('No Content.')
    #Title格納
    if request.POST.has_key(KEY_TITLE) == False:
        raise Exception('No Title.')
    feed.title = request.POST[KEY_TITLE]
    #TLP格納
    if request.POST.has_key(KEY_TLP) == False:
        raise Exception('No TLP.')
    feed.tlp = request.POST[KEY_TLP]

    #stix2 投稿か？
    is_stix2 = is_stix2_post(request)
    stix2_titles = []
    stix2_contents = []
    if request.POST.has_key(KEY_STIX2_TITLES) == True:
        stix2_titles = json.loads(request.POST[KEY_STIX2_TITLES])
        #同一 language が複数に定義されている場合はエラー
        if is_duplicate_languages(stix2_titles) == True:
            raise Exception('Duplicate Same Language Title')
        #stix2_titles から stix 1.x に格納する title を決める
        #default は 先頭
        feed.title = stix2_titles[0][u'title']
        for stix2_title in stix2_titles:
            if stix2_title[u'language'] == request.user.language:
                feed.title = stix2_title[u'title']
                break

    if request.POST.has_key(KEY_STIX2_CONTENTS) == True:
        stix2_contents = json.loads(request.POST[KEY_STIX2_CONTENTS])
        #同一 language が複数に定義されている場合はエラー
        if is_duplicate_languages(stix2_contents) == True:
            raise Exception('Duplicate Same Language Content')
        #stix2_contents から stix 1.x に格納する post を決める
        #default は 先頭
        post = stix2_contents[0][u'content']
        for stix2_content in stix2_contents:
            if stix2_content[u'language'] == request.user.language:
                post = stix2_content[u'content']
                break

    #anonymous投稿か？
    if request.POST.has_key(KEY_ANONYMOUS) == True:
        #投稿ユーザーはアノニマス
        feed.user = STIPUser.get_anonymous_user()
    else:
        feed.user = user

    #publication取得
    if request.POST.has_key(KEY_PUBLICATION) == True:
        publication = request.POST[KEY_PUBLICATION] 
    else:
        publication = PUBLICATION_VALUE_ALL

    #referred_url 取得
    if request.POST.has_key(KEY_REFERRED_URL) == True:
        referred_url = request.POST[KEY_REFERRED_URL] 
        if len(referred_url) == 0:
            referred_url = None
    else:
        referred_url = None

    feed.referred_url = referred_url
        
    group = None
    people = None
    #Sharing Rangeがgroup
    if publication == PUBLICATION_VALUE_GROUP:
        group = request.POST[KEY_GROUP]
        feed.sharing_range_type = const.SHARING_RANGE_TYPE_KEY_GROUP
        feed.sharing_group = Group.objects.get(en_name=group)
    #Sharing Rangeがpeople
    elif publication == PUBLICATION_VALUE_PEOPLE:
        feed.sharing_range_type = const.SHARING_RANGE_TYPE_KEY_PEOPLE
        people = request.POST[KEY_PEOPLE].split(',')
        feed.tmp_sharing_people = []
        for user_id in people:
            #user_id は STIPUser の id
            stip_user = STIPUser.objects.get(id=user_id)
            #一時的に sharing_people リストに格納
            feed.tmp_sharing_people.append(stip_user)
    #Sharing Rangeがall
    elif publication == PUBLICATION_VALUE_ALL:
        feed.sharing_range_type = const.SHARING_RANGE_TYPE_KEY_ALL
    feed.save()
        
    #ファイル添付対応
    for f in request.FILES.values():
        attach_file = save_attach_file(f.name,f,feed.package_id)
        feed.files.add(attach_file)
        
    #indicators があるか
    if request.POST.has_key(KEY_INDICATORS) == True:
        indicators = json.loads(request.POST[KEY_INDICATORS])
    else:
        indicators = []

    #ttps があるか
    if request.POST.has_key(KEY_TTPS) == True:
        ttps = json.loads(request.POST[KEY_TTPS])
    else:
        ttps = []

    #threat_actors があるか
    if request.POST.has_key(KEY_TAS) == True:
        tas = json.loads(request.POST[KEY_TAS])
    else:
        tas = []

    #POSTする
    save_post(
        request,
        feed,post,
        indicators,
        ttps,
        tas,
        is_stix2,
        stix2_titles,
        stix2_contents)
    return feed

#stix2 の投稿か?
def is_stix2_post(request):
    stix2 = False
    if request.POST.has_key(KEY_STIX2) == True:
        if request.POST[KEY_STIX2] == 'true':
            stix2 = True
    return stix2

@login_required
@ajax_required
#添付されたファイルに indicators が含まれているかを確認する
def confirm_indicator(request):
    #添付ファイルごとに AttachFile を作成し list に格納　
    files = []
    for f in request.FILES.values():
        attach_file = AttachFile()
        attach_file.file_name = f.name
        _,tmp_file_path = tempfile.mkstemp()
        attach_file.file_path = tmp_file_path
        with open(attach_file.file_path,'w') as fp:
            fp.write(f.read())
        files.append(attach_file)
        
    #attach_confirm があるか
    if request.POST.has_key(KEY_ATTACH_CONFIRM) == True:
        s = request.POST[KEY_ATTACH_CONFIRM]
        if (s.lower() == 'true'):
            attach_confirm = True
        else:
            attach_confirm = False
    else:
        attach_confirm = True
        
    #stix2 の投稿可？
    stix2 = is_stix2_post(request)
    
    #posts 取得
    posts = []
    if stix2 == True:
        #STIX2.x の場合は post が複数ある
        if request.POST.has_key(KEY_STIX2_CONTENTS) == True:
            stix2_contents = json.loads(request.POST[KEY_STIX2_CONTENTS])
            for stix2_content in stix2_contents:
                posts.append(stix2_content['content'])
    else:
        #STIX1.x の場合は post が 1 つのみ
        if request.POST.has_key(KEY_POST) == True:
            post = request.POST[KEY_POST]
        else:
            post = ''
        posts.append(post)

    #referred_url取得
    if request.POST.has_key(KEY_REFERRED_URL) == True:
        referred_url = request.POST[KEY_REFERRED_URL] 
        if len(referred_url) == 0:
            referred_url = None
    else:
        referred_url = None

    if attach_confirm == True:
        #threat_actors list を取得する
        ta_list = get_threat_actors_list(request)
        #white_list list を取得する
        white_list = get_white_list(request)
        #STIX element を取得する
        confirm_indicators,confirm_ets,confirm_tas = Extractor.get_stix_element(
            files,
            referred_url,
            posts,
            ta_list,
            white_list,
            request.user.sns_profile.scan_csv,
            request.user.sns_profile.scan_pdf,
            request.user.sns_profile.scan_post,
            request.user.sns_profile.scan_txt)
    else:
        #attach_confrim 指定なし
        #pending
        pass

    #添付ファイル削除
    for file_ in files:
        try:
            os.remove(file_.file_path)
        except:
            pass
    data = {}
    data[KEY_INDICATORS] = get_json_from_extractor(confirm_indicators)
    data[KEY_TTPS] = get_json_from_extractor(confirm_ets)
    data[KEY_TAS] = get_json_from_extractor(confirm_tas)
    return JsonResponse(data)

#共通設定と個人設定をマージして返却
def get_merged_conf_list(common_config_content,personal_list_content):
    l_ = []
    #共通設定から
    for item in common_config_content.split('\n'):
        l = item.rstrip('\n\r');
        if len(l) != 0:
            l_.append(l)
        
    #個人設定から
    for personal_item in personal_list_content.split('\r\n'):
        if len(personal_item) != 0:
            l_.append(personal_item.encode('utf-8'))
    #重複を取り除いて返却
    return list(set(l_))


#white_list を取得する
def get_white_list(request):
    return get_merged_conf_list(SNSConfig.get_common_white_list(),request.user.sns_profile.indicator_white_list)

#threat_actors とみなすリストを取得する
def get_threat_actors_list(request):
    return get_merged_conf_list(SNSConfig.get_common_ta_list(),request.user.sns_profile.threat_actors)

#抽出した indicators/TTPs/threat_actors から返却データを作成する
def get_json_from_extractor(datas):
    d = {}
    for data in datas:
        type_ = data[0]
        value_ = data[1]
        title = data[2]
        file_name = data[3]
        checked = data[4]
        if d.has_key(file_name) == False:
            d[file_name] = [(type_,value_,title,checked)]
        else:
            d[file_name].append((type_,value_,title,checked))
    return d

@login_required
@ajax_required
def post(request):
    try:
        last_feed_datetime = get_datetime_from_string(request.POST.get('last_feed'))
        user = request.user
        csrf_token = (csrf(request)['csrf_token'])
        #postする
        post_common(request,user)
        html = _html_feeds(last_feed_datetime, user, csrf_token)
        return HttpResponse(html)
    except Exception as e:
        traceback.print_exc()
        return HttpResponseServerError(str(e))

@login_required
@ajax_required
def like(request):
    #Like元のパッケージID
    package_id = request.POST['package_id']
    feed = Feed.get_feeds_from_package_id(request.user,package_id)

    #user は STIPUser
    stip_user = request.user

    #liker情報取得
    likers = rs.get_likers_from_rs(stip_user, package_id)
    #すでにLikeされているか判定
    #自分自身の liker 文字列は instance_name + space + user_name
    myliker = '%s %s' % (SNSConfig.get_sns_identity_name(),stip_user.username)
    like = myliker in likers
    #Like/Unlike 用の STIX イメージ作成
    feed_stix_like = FeedStixLike(feed,like,creator=stip_user)

    if like:
        #notify の unlike処理
        stip_user.unotify_liked(package_id,feed.user)
    else:
        #notify の like処理
        stip_user.notify_liked(package_id,feed.user)
        
    #一時ファイルにstixの中身を書き出す
    tmp_file_path = write_like_comment_attach_stix(feed_stix_like.get_xml_content())
    #RS に登録する
    rs.regist_ctim_rs(stip_user,feed_stix_like.file_name,tmp_file_path)
    os.remove(tmp_file_path)
    
    #現在の Like 情報を取得する
    likers = rs.get_likers_from_rs(stip_user, package_id)
    return HttpResponse(len(likers))

@login_required
def attach(request):
    file_id = request.POST['file_id']
    attach_file_name = Feed.get_attach_file_name(file_id)
    attach_file_path = Feed.get_attach_file_path(file_id)
    #response作成
    with open(attach_file_path,'r') as fp:
        response = HttpResponse(fp.read(),content_type='application/octet-stream')
        response['Content-Disposition'] = 'attachment; filename=%s' % (attach_file_name)
    return response

@login_required
@ajax_required
def comment(request):
    #user は STIPUser
    stip_user = request.user
    if request.method == 'POST':
        #引数取得
        package_id = request.POST['package_id']
        #コメント投稿
        post_comment(stip_user,package_id,request.POST['post'],stip_user)
        #表示用
        comments = rs.get_comment_from_rs(stip_user, package_id)
        feeds = []
        for comment in comments:
            feeds.append(Feed.get_feeds_from_package_from_rs(stip_user,comment))
        return render(request, 'feeds/partial_feed_comments.html',
                      {'feeds': feeds})

    else:
        #引数取得
        package_id = request.GET['package_id']
        comments = rs.get_comment_from_rs(stip_user, package_id)
        feeds = []
        for comment in comments:
            feeds.append(Feed.get_feeds_from_package_from_rs(stip_user,comment))
        return render(request, 'feeds/partial_feed_comments.html',
                      {'feeds': feeds})

#comment postする(共通)
def post_comment(api_user,original_package_id,post,comment_user):
    #Feed 情報作成
    origin_feed = Feed.get_feeds_from_package_id(api_user,original_package_id)
    #comment 作成
    post = post.strip()
    if len(post) > 0:
        post = post[:10240] 
    #Comment 用の STIX イメージ作成
    feed_stix_comment = FeedStixComment(origin_feed,post,api_user)
    #一時ファイルにstixの中身を書き出す
    tmp_file_path = write_like_comment_attach_stix(feed_stix_comment.get_xml_content())
    #RS に登録する
    rs.regist_ctim_rs(api_user,feed_stix_comment.file_name,tmp_file_path)
    #一時ファイルは削除
    os.remove(tmp_file_path)
    #通知
    comment_user.notify_commented(original_package_id,origin_feed.user)
    notify_also_commented(original_package_id,origin_feed.user,comment_user)

#Profile にあった内容をこちらに移動
def notify_also_commented(package_id,feed_user,comment_user):
    from ctirs.models import Notification
    comments = rs.get_comment_from_rs(comment_user,package_id)
    users = []
    for comment in comments:
        uploader_id = long(comment['uploader'])
        #uploader -> かつてのコメントユーザー
        #comment -> 最新のコメントを入力したユーザー
        #feed_user -> root 投稿ユーザー
        if uploader_id != comment_user.id and uploader_id != feed_user.id:
            users.append(comment['uploader'])

    users = list(set(users))
    for user in users:
        Notification(notification_type=Notification.ALSO_COMMENTED,
                     from_user=comment_user,
                     to_user=STIPUser(id=user), package_id=package_id).save()


#Cache dir に feed_stix の中身を一時ファイルとして作成し、ファイルパスを返却する
def write_like_comment_attach_stix(content):
    #一時的ファイルにstixの中身を書き出す
    _tmp,tmp_file_path = tempfile.mkstemp(dir=const.STIX_CACHE_DIR)
    with open(tmp_file_path,'wb+') as fp:
        fp.write(content)
    return tmp_file_path
    
@login_required
@ajax_required
#一定期間ごと (30s)に feed_source に関連する like, comment 情報を更新する
def update(request):
    first_feed_datetime = get_datetime_from_string(request.GET.get('first_feed'))
    last_feed_datetime = get_datetime_from_string(request.GET.get('last_feed'))
    feed_source = request.GET.get('feed_source')
    feeds = Feed.get_feeds(
        range_big_datetime=first_feed_datetime,  #期間範囲指定の大きい方(新しい方)。この時間を含む
        range_small_datetime=last_feed_datetime, #期間範囲指定の小さい方(古い方)。この時間を含む
        api_user=request.user)
    

    if feed_source != 'all':
        l = []
        for feed in feeds:
            if feed.package_id == feed_source:
                l.append(feed)
        feeds = l
    dump = {}
    for feed in feeds:
        feed = Feed.add_like_comment_info(request.user,feed)
        dump[feed.pk] = {'likes': feed.likes, 'comments': feed.comments}
    data = json.dumps(dump)
    return HttpResponse(data, content_type='application/json')

@login_required
@ajax_required
def track_comments(request):
    #引数取得
    stip_user = request.user
    package_id = request.GET['package_id']
    comments = rs.get_comment_from_rs(stip_user, package_id)
    feeds = []
    for comment in comments:
        feeds.append(Feed.get_feeds_from_package_from_rs(stip_user,comment))
    return render(request, 'feeds/partial_feed_comments.html',
                  {'feeds': feeds})

@login_required
@ajax_required
def remove(request):
    #remove 処理
    # cache original 削除
    #??? attach 削除
    #??? comment,like削除
    # RS から削除は必須
    return HttpResponse()

#request から L2 の GV の URL を構築する
def _get_ctim_gv_url(request):
    #設定ファイルに指定があったらその値を使う
    if (SNSConfig.get_gv_l2_url() is not None) and (len(SNSConfig.get_gv_l2_url()) != 0):
        return SNSConfig.get_gv_l2_url()
    #ない場合は request の値から URL 構築する
    scheme =  request.scheme
    host =  request.get_host()
    host_split = host.split(':')
    if len(host_split) == 1:
        gv_host = '%s:%d' % (host,DEFAULT_GV_PORT)
    else:
        gv_host = '%s:%d' % (host_split[0],DEFAULT_GV_PORT)
    gv_url = '%s://%s%s' % (scheme,gv_host,L2_GV_PATH)
    return gv_url

@login_required
@ajax_required
def get_ctim_gv_url(request):
    try:
        package_id = request.GET['package_id']
        url = '%s?package_id=%s' % (_get_ctim_gv_url(request),package_id)
        return HttpResponse(url)
    except Exception as e:
        return HttpResponseServerError(str(e))

@login_required
@ajax_required
def share_misp(request):
    try:
        package_id = request.GET['package_id']
        #user は STIPUser
        stip_user = request.user
        #RS に misp 共有要求
        resp = rs.share_misp(stip_user, package_id)
        return HttpResponse(resp[u'url'])
    except Exception as e:
        return HttpResponseServerError(str(e))

@login_required
@ajax_required
def call_jira(request):
    try:
        #JIRA が import されていない場合は何もしない
        if imported_jira is None:
            rsp = {}
            return JsonResponse(rsp)
        #feed情報取得
        feed_file_name_id = request.GET['feed_id']
        package_id_arg = request.GET['package_id']
        feed = Feed.get_feeds_from_package_id(request.user,package_id_arg)

        #JIRA instance
        j = JIRA(
            server=SNSConfig.get_jira_host(),
            basic_auth=(SNSConfig.get_jira_username(),SNSConfig.get_jira_password()))
        #issues作成
        issue = j.create_issue(
            project = SNSConfig.get_jira_project(),
            summary = feed.title,
            description = feed.post,
            issuetype = {
                'name': SNSConfig.get_jira_type()
                })
        #添付があればそれもつける
        for attach_file in feed.files.all():
            file_path = Feed.get_attach_file_path(attach_file.package_id)
            j.add_attachment(issue=issue,attachment=file_path,filename=str(attach_file.file_name))

        #STIX添付
        stix_package = STIXPackage.from_xml(feed.stix_file_path)
        package_id = stix_package.id_
        stix_file_name = '%s.xml' % (package_id)
        j.add_attachment(issue=issue,attachment=feed.stix_file_path,filename=stix_file_name)

        #CSV添付
        #CSVの中身を取得する
        content = get_csv_content(feed_file_name_id)
        csv_attachment = StringIO.StringIO()
        csv_attachment.write(content)
        csv_file_name = '%s.csv' % (package_id)
        j.add_attachment(issue=issue,attachment=csv_attachment,filename=csv_file_name)

        #PDF添付
        feed_pdf = FeedPDF(feed,stix_package)
        pdf_attachment = StringIO.StringIO()
        feed_pdf.make_pdf_content(pdf_attachment,feed)
        pdf_file_name = '%s.pdf' % (package_id)
        j.add_attachment(issue=issue,attachment=pdf_attachment,filename=pdf_file_name)

        #isssue番号返却
        url = SNSConfig.get_jira_host() + '/projects/' + SNSConfig.get_jira_project() + '/issues/' +str(issue)
        rsp = {
                'issues' : str(issue),
                'url' : url,
             }
        return JsonResponse(rsp)
    except Exception as e:
        traceback.print_exc()
        return HttpResponseServerError(str(e))

@login_required
def download_stix(request):
    feed_file_name_id = request.GET['feed_id']
    #cache の STIX を返却
    stix_file_path = Feed.get_cached_file_path(feed_file_name_id)
    #response作成
    file_name = '%s.xml' % (feed_file_name_id)
    with open(stix_file_path,'r') as fp:
        output = io.StringIO()
        output.write(unicode(fp.read(),'utf-8'))
        response = HttpResponse(output.getvalue(),content_type='application/xml')
        response['Content-Disposition'] = 'attachment; filename=%s' % (file_name)
    return response

@login_required
def download_stix2(request):
    feed_file_name_id = request.GET['feed_id']
    stix_file_path = rs.get_stix_file_path(request.user,feed_file_name_id)
    #response作成
    file_name = '%s.json' % (feed_file_name_id)
    with open(stix_file_path,'r') as fp:
        output = io.StringIO()
        output.write(unicode(fp.read(),'utf-8'))
        response = HttpResponse(output.getvalue(),content_type='application/json')
        response['Content-Disposition'] = 'attachment; filename=%s' % (file_name)
    return response

def get_feed_stix(feed_file_name_id):
    stix_file_path = Feed.get_cached_file_path(feed_file_name_id)
    return FeedStix(stix_file_path=stix_file_path)

@login_required
@ajax_required
def is_exist_indicator(request):
    feed_file_name_id = request.POST['feed_id']
    feed_stix = get_feed_stix(feed_file_name_id)
    #csv 作成
    content = feed_stix.get_csv_content()
    #長さが0ならば存在しない
    return HttpResponse(len(content) != 0)

@login_required
def download_csv(request):
    feed_file_name_id = request.POST['feed_id']
    #CSVの中身を取得する
    content = get_csv_content(feed_file_name_id)
    #response作成
    file_name = '%s.csv' % (rs.convert_package_id_to_filename(feed_file_name_id))
    output = io.StringIO()
    output.write(content)
    response = HttpResponse(output.getvalue(),content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=%s' % (file_name)
    return response

#feed情報からcsv contentを取得する
def get_csv_content(feed_file_name_id):
    feed_stix = get_feed_stix(feed_file_name_id)
    #csv 作成
    content = feed_stix.get_csv_content()
    #CSVデータの先頭にBOMを付与
    content = codecs.BOM_UTF8.decode('utf-8') + content
    return content

@login_required
def download_pdf(request):
    #引数取得
    feed_file_name_id = request.POST['feed_id']
    package_id = request.POST['package_id']
    
    #STIX 情報作成
    feed_stix = get_feed_stix(feed_file_name_id)
    feed = Feed.get_feeds_from_package_id(request.user,package_id)
    #PDF 情報作成
    feed_pdf = FeedPDF(feed,feed_stix.stix_package)

    #HttpResponse作成
    file_name = '%s.pdf' % (feed_file_name_id)
    response = HttpResponse(content='application/pdf')
    #responseにPDF格納
    feed_pdf.make_pdf_content(response,feed)
    response['Content-Disposition'] = 'attachment; filename=%s' % (file_name)
    response['Content-Type'] = 'application/pdf' 
    return response

#stix_packageからpostコンテンツを取得する
def get_post_from_stix_content(stix_package):
    description = ''
    short_description = ''
    #headerのdescriptionがあればそこから取得する
    try:
        v = stix_package.stix_header.description
        if v is not None and len(v.value) != 0:
            description = v.value
    except:
        pass

    #headerのshort_descriptionがあればそこから取得する
    try:
        v = stix_package.stix_header.short_description
        if v is not None and len(v.value) != 0:
            short_description = v.value
    except:
        pass
    return '<b>Description:</b> %s\n<b>Short Description</b>: %s' % (description,short_description)

#添付ファイル格納ディレクトリのルートパス取得
def get_attach_root_dir_path():
    return  const.ATTACH_FILE_DIR

#IDごとの添付ファイル格納ディレクトリパス取得
def get_attach_dir_path(id_):
    return '%s%s%s' % (get_attach_root_dir_path(),str(id_),os.sep)

#nameのファイル名とfの内容から添付ファイルを保存し、
#attach_fileレコードを作成して返却する
def save_attach_file(filename,content,id_):
    attach_file = AttachFile()
    attach_file.file_name = filename

    #attach格納ディレクトリ作成
    attach_root_dir = get_attach_root_dir_path()
    if not os.path.exists(attach_root_dir):
        os.makedirs(attach_root_dir)
    attach_dir = get_attach_dir_path(id_)
    if not os.path.exists(attach_dir):
        os.makedirs(attach_dir)
           
    #一時ファイルに保存
    _,tmp_file_path = tempfile.mkstemp(dir=attach_dir)
    with open(tmp_file_path, 'wb+') as fp:
        #content.read()はstr
        fp.write(content.read())
    #MD5値取得
    with open(tmp_file_path,'rb') as fp:
        v = fp.read()
        md5 = hashlib.md5(v).hexdigest()
            
    #rename
    file_path = attach_dir + md5
    os.rename(tmp_file_path,file_path)

    #ファイルパスを保存
    attach_file.file_path = file_path
    attach_file.save()
    return attach_file

#RS に関連 STIX を問い合わせ、結果をコメント表示
def post_rs_indicator_matching_comment(request,feed,id_,concierge_user):
    try:
        #RS にrelated packages 問い合わせ
        matching_data = rs.get_matching_from_rs(concierge_user,id_)
        if len(matching_data) == 0:
            #存在しない場合はコメントしない
            return

        #存在する場合
        url = '%s?package_id=%s' % (_get_ctim_gv_url(request),id_)
        msg = str(len(matching_data))
        msg += ' '
        msg += 'related package(s) are found.'
        msg += '\n<br/>\n'
        msg += '<a href= "%s" target="_blank">' % (url)
        msg += 'Check those package(s).'
        msg += '</a>'
        #指定User で投稿
        post_comment(concierge_user,id_,msg,concierge_user)
    except Exception:
        traceback.print_exc()

#CrowdStrike に関連 Report を問い合わせ、結果をコメント表示
def post_crowd_strike_indicator_matching_comment(request,feed,id_,concierge_user,json_indicators):
    try:
        realted_reports = []
        for json_indicator in json_indicators:
            value = json_indicator[u'value']
            results = search_indicator(value)
            for result in results:
                if result.has_key('reports') == False:
                    #reports がない場合は skip
                    continue
                #report を追加する
                for report in result['reports']:
                    realted_reports.append(report)
        #重複を取り除く
        realted_reports = list(set(realted_reports))
        if len(realted_reports) == 0:
            #存在しない場合はコメントしない
            return

        #存在する場合
        msg = str(len(realted_reports))
        msg += ' '
        msg += 'related report(s) are found.'
        msg += '\n<br/>\n'
        msg += 'Reports: <br/>'
        for realted_report in realted_reports:
            #report id から report title と URL を取得する
            report_title,url = get_report_info(realted_report)
            msg += ('<a href="%s" target="_blank">%s</a><br/>' % (url,report_title))
        #指定User で投稿
        post_comment(concierge_user,id_,msg,concierge_user)
    except Exception:
        traceback.print_exc()

#feedを保存する
def save_post(request,
              feed,
              post,
              json_indicators=[],
              ttps=[],
              tas=[],
              is_stix2=False,
              stix2_titles=[],
              stix2_contents=[]):
    if len(post) == 0:
        return None

    feed.post = post[:10240]

    #STIX 2.x 出力の場合は RS 登録する　
    if is_stix2 == True:
        bundle = get_stix2_bundle(json_indicators,
                          ttps,
                          tas,
                          feed.title,
                          post,
                          stix2_titles,
                          stix2_contents,
                          request.user)
        feed.stix2_package_id = bundle.id
        _,stix2_file_path =tempfile.mkstemp()
        with open(stix2_file_path,'w') as fp:
            fp.write(bundle.serialize(True,ensure_ascii=False).encode('utf-8'))
        #RS に登録する
        rs.regist_ctim_rs(feed.user,bundle.id,stix2_file_path)
        os.remove(stix2_file_path)

    #stixファイルを作成する
    feed_stix = FeedStix(
        feed=feed,
        indicators=json_indicators,
        ttps=ttps,
        tas=tas
    )
        
    #Slack 投稿用の添付ファイル作成
    if feed.files.count() > 1:
        #ファイルが複数
        #ファイルが添付されている場合は file upload をコメント付きで
        temp = tempfile.NamedTemporaryFile()
        with zipfile.ZipFile(temp.name,'w',compression=zipfile.ZIP_DEFLATED) as new_zip:
            for file_ in feed.files.all():
                new_zip.write(file_.file_path,arcname = file_.file_name)
        upploaded_filename = 'uploaded_files.zip'
    elif feed.files.count() == 1:
        #ファイルが単数
        temp = tempfile.NamedTemporaryFile()
        file_ = feed.files.get()
        with open(file_.file_path) as fp:
            temp.write(fp.read())
            temp.seek(0)
        upploaded_filename = file_.file_name
    else:
        temp = None

    feed.stix_file_path = write_stix_file(feed,feed_stix)
    #package_id取得
    feed.package_id = feed_stix.get_stix_package().id_

    #slack 投稿
    if feed.user.username != const.SNS_SLACK_BOT_ACCOUNT:
        slack_post = ''
        slack_post += '[%s]\n' % (feed.title)
        slack_post += '\n'
        slack_post += '%s\n' % (feed.post)
        slack_post += '\n'
        slack_post += '---------- S-TIP Post Info (TLP: %s) ----------\n' % (feed.tlp)
        slack_post += '%s: %s\n' % (u'Account',feed.user.username)
        slack_post += '%s: %s\n' % (u'Package_ID',feed.package_id)
        slack_post += '%s: %s\n' % (u'Referred URL',feed.referred_url if feed.referred_url is not None else '')
        slack_post = slack_post.replace('&amp;','%amp;amp;')
        slack_post = slack_post.replace('&lt;','%amp;lt;')
        slack_post = slack_post.replace('&gt;','%amp;gt;')
        
        #Slack 投稿用の添付ファイル作成
        from daemon.slack.receive import post_slack_channel, sc
        if temp is not None :
            #ファイルが添付されている場合は file uplaod をコメント付きで
            sc.api_call ('files.upload',
                     initial_comment = slack_post,
                     channels = post_slack_channel,
                     file = open(temp.name,'rb'),
                     filename = upploaded_filename)
            #閉じると同時に削除される
            temp.close()
        else:
            sc.api_call('chat.postMessage',
                    text = slack_post,
                    channel = post_slack_channel,
                    as_user = 'true')

    #添付 ファイルstixを送る
    for attachment_file in feed_stix.attachment_files:
        file_name = attachment_file.stix_header.title
        #一時ファイルにstixの中身を書き出す
        tmp_file_path = write_like_comment_attach_stix(attachment_file.to_xml())
        #RS に登録する
        rs.regist_ctim_rs(feed.user,file_name,tmp_file_path)
        #登録後にファイルは削除
        os.remove(tmp_file_path)
    #添付ファイル STIX を　RS に登録後、投稿 STIX を送る
    rs.regist_ctim_rs(feed.user,feed.title,feed.stix_file_path)
        
    #添付ファイル削除
    for file_ in feed.files.all():
        os.remove(file_.file_path)

    #indicatorが存在していれば chatbot 起動する
    indicators = feed_stix.get_stix_package().indicators
    if indicators is not None and len(indicators) != 0:
        #chatbot指定があれば起動する
        if const.SNS_GV_CONCIERGE_ACCOUNT is not None:
            try:
                concierge_user = STIPUser.objects.get(username=const.SNS_GV_CONCIERGE_ACCOUNT)
                #非同期で RS から matching 情報を取得しコメントをつける
                matching_comment_th = threading.Thread(target=post_rs_indicator_matching_comment,args=(request,feed,feed_stix.get_stix_package().id_,concierge_user))
                matching_comment_th.daemon = True
                matching_comment_th.start()
            except Exception:
                pass
        if const.SNS_FALCON_CONCIERGE_ACCOUNT is not None:
            try:
                concierge_user = STIPUser.objects.get(username=const.SNS_FALCON_CONCIERGE_ACCOUNT)
                #非同期で CrowdStrike から indicator に該当する report を取得しコメントをつける
                crowd_strike_report_th = threading.Thread(target=post_crowd_strike_indicator_matching_comment,args=(request,feed,feed_stix.get_stix_package().id_,concierge_user,json_indicators))
                crowd_strike_report_th.daemon = True
                crowd_strike_report_th.start()
            except Exception:
                pass

    return

#feedの中身からSTIX contentを作成し、ファイル出力する
#filepathを返却する
def write_stix_file(feed,feed_stix):
    stix_file_path =  '%s%s%s' % (const.STIX_FILE_DIR,str(feed.filename_pk),'.xml')
    with open(stix_file_path,'w') as fp:
        #STIXの中身を追加
        stix_content = feed_stix.get_xml_content()
        fp.write(stix_content)
    return stix_file_path

#stix_pakcageからTLPを取得する。
#未定義の場合はuserごとのデフォルトTLPを返却する
def get_tlp_from_stix(stix_package,user):
    try:
        return stix_package.stix_header.handling.markings[0].marking_structures[0].color
    except:
        pass
    try:
        return stix_package.stix_header.handling[0].marking_structures[0].color
    except:
        pass
    #AIS用TLP
    try:
        return stix_package.stix_header.handling[0].marking_structures[0].not_proprietary.tlp_marking.color
    except:
        pass
    return user.tlp

#投稿を開いた時の like,unlike 情報取得
@login_required
@ajax_required
def get_like_comment(request):
    package_id = request.GET['package_id']
    #feed の like, comment 情報取得
    #投稿があることが確定しているので直接 cache からFeed 取得
    feed = Feed.objects.get(package_id=package_id)
    Feed.add_like_comment_info(request.user,feed)
    rsp = {
            'likes' : feed.likes,
            'like' : feed.like,
            'comments' : feed.comments 
         }
    return JsonResponse(rsp)