import re
import codecs
import datetime
import hashlib
import io
import json
import os
import tempfile
import threading
import requests
import zipfile
import traceback
import iocextract
import urllib
import pytz
try:
    from jira import JIRA
    imported_jira = True
except ImportError:
    imported_jira = False

import stip.common.const as const
import ctirs.models.sns.feeds.rs as rs
import feeds.feed_stix2_sighting as stip_sighting

from decorators import ajax_required
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseServerError
from django.http.response import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.template.context_processors import csrf
from django.template.loader import render_to_string

from ctirs.models import AttachFile, Feed, Group, SNSConfig, STIPUser, System
from feeds.adapter.phantom import call_run_phantom_playbook
from feeds.adapter.splunk import get_sightings
from feeds.extractor.base import Extractor
from feeds.feed_pdf import FeedPDF
from feeds.feed_stix import FeedStix
from feeds.feed_stix2 import get_post_stix2_bundle, get_attach_stix2_bundle, get_comment_stix2_bundle, get_like_stix2_bundle
from feeds.feed_stix_common import FeedStixCommon
from stix.core.stix_package import STIXPackage
from stix2 import parse
import stix2.v21.sdo as sdo_21
import stix2.v20.sdo as sdo_20


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
KEY_MULTI_LANGUAGE = 'multi_language'
KEY_STIX2_TITLES = 'stix2_titles'
KEY_STIX2_CONTENTS = 'stix2_contents'
KEY_ATTACH_CONFIRM = 'attach_confirm'
KEY_SCREEN_NAME = 'screen_name'

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
    # 最終更新時間
    last_reload = str(datetime.datetime.now())
    # anonymous以外の全ユーザを返却する
    users_list = STIPUser.objects.filter(is_active=True).exclude(username='anonymous').order_by('username')

    if feeds:
        # feedsがあれば、 last_feedを一番最新のfeed id に指定する　
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
        'sharing_groups': Group.objects.all(),
    })
    r.set_cookie(key='username', value=str(request.user))
    return r


def feed(request, pk):
    feed = get_object_or_404(Feed, pk=pk)
    return render(request, 'feeds/feed.html', {
        'feed': feed,
        'jira': imported_jira,
    })


@ajax_required
# 次のページの読み込み時に呼ばれる
def load(request):
    from_feed = request.GET.get('from_feed')
    page = int(request.GET.get('page'))
    feed_source = request.GET.get('feed_source')
    user_id = None
    query_string = request.GET.get(key='query_string', default=None)
    if feed_source is not None:
        if feed_source != 'all':
            user_id = feed_source
    # from_feed 指定の STIXPacakge ID の produced 時間を取得する
    if from_feed != 'None':
        # from_feed が設定されている場合
        package_from_feed = rs.get_package_info_from_package_id(request.user, from_feed)
        produced_str = package_from_feed['produced']

        # RS から produced 時間より古い最新の Feed を取得する
        last_reload = Feed.get_datetime_from_string(produced_str)

        # Feed 取得する
        index = (page - 1) * FEEDS_NUM_PAGES
        feeds = Feed.get_feeds(
            api_user=request.user,
            last_reload=last_reload,
            user_id=user_id,
            index=index,
            query_string=query_string,
            size=FEEDS_NUM_PAGES)
    else:
        # from_feed が設定されていない場合 (投稿がない場合)
        feeds = []
    html = ''
    csrf_token = (csrf(request)['csrf_token'])
    for feed in feeds:
        html = '{0}{1}'.format(
            html,
            render_to_string(
                'feeds/partial_feed.html',
                {
                    'feed': feed,
                    'jira': imported_jira,
                    'user': request.user,
                    'csrf_token': csrf_token,
                }
            )
        )
    return HttpResponse(html)


def _html_feeds(last_feed_datetime, user, csrf_token, feed_source='all'):
    user_id = None
    if feed_source != 'all':
        user_id = feed_source
    feeds = Feed.get_feeds_after(last_feed_datetime=last_feed_datetime, api_user=user, user_id=user_id)
    html = ''
    for feed in feeds:
        html = '{0}{1}'.format(
            html,
            render_to_string(
                'feeds/partial_feed.html',
                {
                    'feed': feed,
                    'jira': imported_jira,
                    'user': user,
                    'csrf_token': csrf_token
                }
            )
        )
    return html


# string から datetime型を取得する (YYYYMMDDHHMMSS)
def get_datetime_from_string(s):
    try:
        local_time_dt = datetime.datetime.strptime(s, '%Y%m%d%H%M%S.%f')
        # UTC に直して返却
        ret = pytz.utc.localize(local_time_dt)
    except BaseException:
        # 取得できない場合は UTC の現在時刻とする
        ret = datetime.datetime.now(tz=pytz.utc)
    return ret


@ajax_required
def load_new(request):
    last_feed_datetime = get_datetime_from_string(request.GET.get('last_feed'))
    user = request.user
    csrf_token = (csrf(request)['csrf_token'])
    html = _html_feeds(last_feed_datetime, user, csrf_token)
    return HttpResponse(html)


@ajax_required
def check(request):
    last_feed_datetime = get_datetime_from_string(request.GET.get('last_feed'))
    # feed_source は 全員のフィード取得の際は ALL,それ以外は STIPUserのid数値文字列
    feed_source = request.GET.get('feed_source')
    user = None
    if feed_source != 'all':
        user = feed_source
    # 引数 rs 呼び出し用api_user,user(全員の場合はNone,それ以外はid STIP UserのID数値文字列)
    feeds = Feed.get_feeds_after(
        last_feed_datetime=last_feed_datetime,
        api_user=request.user,
        user_id=user)
    count = len(feeds)
    return HttpResponse(count)


def check_via_poll(request):
    last_feed_datetime = get_datetime_from_string(request.GET.get('last_feed'))
    feed_source = request.GET.get('feed_source')
    feed_source = feed_source if feed_source is not None else 'all'
    username = request.GET.get('username')
    user = STIPUser.objects.get(username=username)
    feeds = Feed.get_feeds_after(last_feed_datetime=last_feed_datetime, api_user=user)
    if feed_source != 'all':
        feeds = feeds.filter(user__id=feed_source)
    count = len(feeds)
    return HttpResponse(count)


# 同一の language が複数指定されているかどうか確認する
def is_duplicate_languages(values):
    languages = []
    for value in values:
        language = value['language']
        if language in languages:
            return True
        languages.append(language)
    return False


# Web経由 / REST API 経由共通
def post_common(request, user):
    # Feed作成
    feed = Feed()
    # ManyToMany をクリアする
    feed.files.clear()
    feed.sharing_people.clear()
    # POSTデータ格納
    if KEY_POST not in request.POST:
        raise Exception('No Post.')
    post = request.POST[KEY_POST]
    post = post.strip()
    if len(post) == 0:
        raise Exception('No Content.')
    # Title格納
    if KEY_TITLE not in request.POST:
        raise Exception('No Title.')
    feed.title = request.POST[KEY_TITLE]
    # TLP格納
    if KEY_TLP not in request.POST:
        raise Exception('No TLP.')
    feed.tlp = request.POST[KEY_TLP]

    # multi language 投稿か？
    stix2_titles = []
    stix2_contents = []
    if KEY_STIX2_TITLES in request.POST:
        stix2_titles = json.loads(request.POST[KEY_STIX2_TITLES])
        # 同一 language が複数に定義されている場合はエラー
        if is_duplicate_languages(stix2_titles):
            raise Exception('Duplicate Same Language Title')
        # stix2_titles から stix 1.x に格納する title を決める
        # default は 先頭
        feed.title = stix2_titles[0]['title']
        for stix2_title in stix2_titles:
            if stix2_title['language'] == request.user.language:
                feed.title = stix2_title['title']
                break

    if KEY_STIX2_CONTENTS in request.POST:
        stix2_contents = json.loads(request.POST[KEY_STIX2_CONTENTS])
        # 同一 language が複数に定義されている場合はエラー
        if is_duplicate_languages(stix2_contents):
            raise Exception('Duplicate Same Language Content')
        # stix2_contents から stix 1.x に格納する post を決める
        # default は 先頭
        post = stix2_contents[0]['content']
        for stix2_content in stix2_contents:
            if stix2_content['language'] == request.user.language:
                post = stix2_content['content']
                break

    # anonymous投稿か？
    if KEY_ANONYMOUS in request.POST:
        # 投稿ユーザーはアノニマス
        feed.user = STIPUser.get_anonymous_user()
    else:
        feed.user = user

    # publication取得
    if KEY_PUBLICATION in request.POST:
        publication = request.POST[KEY_PUBLICATION]
    else:
        publication = PUBLICATION_VALUE_ALL

    # referred_url 取得
    if KEY_REFERRED_URL in request.POST:
        referred_url = request.POST[KEY_REFERRED_URL]
        if len(referred_url) == 0:
            referred_url = None
    else:
        referred_url = None

    feed.referred_url = referred_url

    group = None
    people = None
    # Sharing Rangeがgroup
    if publication == PUBLICATION_VALUE_GROUP:
        group = request.POST[KEY_GROUP]
        feed.sharing_range_type = const.SHARING_RANGE_TYPE_KEY_GROUP
        feed.sharing_group = Group.objects.get(en_name=group)
    # Sharing Rangeがpeople
    elif publication == PUBLICATION_VALUE_PEOPLE:
        feed.sharing_range_type = const.SHARING_RANGE_TYPE_KEY_PEOPLE
        people = request.POST[KEY_PEOPLE].split(',')
        feed.tmp_sharing_people = []
        for user_id in people:
            # user_id は STIPUser の id
            stip_user = STIPUser.objects.get(id=user_id)
            # 一時的に sharing_people リストに格納
            feed.tmp_sharing_people.append(stip_user)
    # Sharing Rangeがall
    elif publication == PUBLICATION_VALUE_ALL:
        feed.sharing_range_type = const.SHARING_RANGE_TYPE_KEY_ALL

    # indicators があるか
    if KEY_INDICATORS in request.POST:
        indicators = json.loads(request.POST[KEY_INDICATORS])
    else:
        indicators = []

    # ttps があるか
    if KEY_TTPS in request.POST:
        ttps = json.loads(request.POST[KEY_TTPS])
    else:
        ttps = []

    # threat_actors があるか
    if KEY_TAS in request.POST:
        tas = json.loads(request.POST[KEY_TAS])
    else:
        tas = []

    # POSTする
    save_post(
        request,
        feed, post,
        indicators,
        ttps,
        tas,
        request.FILES.values(),
        stix2_titles,
        stix2_contents)

    feed.save()
    return feed


# Multi Language の投稿か?
def is_multi_language(request):
    is_multi_language = False
    if KEY_MULTI_LANGUAGE in request.POST:
        if request.POST[KEY_MULTI_LANGUAGE] == 'true':
            is_multi_language = True
    return is_multi_language


@ajax_required
# 添付されたファイルに indicators が含まれているかを確認する
def confirm_indicator(request):
    # 添付ファイルごとに AttachFile を作成し list に格納　
    files = []
    for f in request.FILES.values():
        attach_file = AttachFile()
        attach_file.file_name = f.name
        _, tmp_file_path = tempfile.mkstemp()
        attach_file.file_path = tmp_file_path
        with open(attach_file.file_path, 'wb') as fp:
            fp.write(f.read())
        files.append(attach_file)

    # attach_confirm があるか
    if KEY_ATTACH_CONFIRM in request.POST:
        s = request.POST[KEY_ATTACH_CONFIRM]
        if (s.lower() == 'true'):
            attach_confirm = True
        else:
            attach_confirm = False
    else:
        attach_confirm = True

    # Multi Language の投稿可？
    multi_language = is_multi_language(request)

    # posts 取得
    posts = []
    if multi_language:
        # STIX2.x の場合は post が複数ある
        if KEY_STIX2_CONTENTS in request.POST:
            stix2_contents = json.loads(request.POST[KEY_STIX2_CONTENTS])
            for stix2_content in stix2_contents:
                posts.append(stix2_content['content'])
    else:
        # STIX1.x の場合は post が 1 つのみ
        if KEY_POST in request.POST:
            post = request.POST[KEY_POST]
        else:
            post = ''
        posts.append(post)

    # referred_url取得
    if KEY_REFERRED_URL in request.POST:
        referred_url = request.POST[KEY_REFERRED_URL]
        if len(referred_url) == 0:
            referred_url = None
    else:
        referred_url = None

    if attach_confirm:
        # threat_actors list を取得する
        ta_list = get_threat_actors_list(request)
        # white_list list を取得する
        white_list = get_white_list(request)
        # STIX element を取得する
        confirm_indicators, confirm_ets, confirm_tas = Extractor.get_stix_element(
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
        # attach_confrim 指定なし
        # pending
        pass

    # 添付ファイル削除
    for file_ in files:
        try:
            os.remove(file_.file_path)
        except BaseException:
            pass
    data = {}
    data[KEY_INDICATORS] = get_json_from_extractor(confirm_indicators)
    data[KEY_TTPS] = get_json_from_extractor(confirm_ets)
    data[KEY_TAS] = get_json_from_extractor(confirm_tas)
    return JsonResponse(data)


# 共通設定と個人設定をマージして返却
def get_merged_conf_list(common_config_content, personal_list_content):
    l_ = []
    # 共通設定から
    for item in common_config_content.split('\n'):
        str_ = item.rstrip('\n\r')
        if len(str_) != 0:
            l_.append(str_)

    # 個人設定から
    for personal_item in personal_list_content.split('\r\n'):
        if len(personal_item) != 0:
            l_.append(personal_item)
    # 重複を取り除いて返却
    return list(set(l_))


# white_list を取得する
def get_white_list(request):
    return get_merged_conf_list(SNSConfig.get_common_white_list(), request.user.sns_profile.indicator_white_list)


# threat_actors とみなすリストを取得する
def get_threat_actors_list(request):
    return get_merged_conf_list(SNSConfig.get_common_ta_list(), request.user.sns_profile.threat_actors)


# 抽出した indicators/TTPs/threat_actors から返却データを作成する
def get_json_from_extractor(datas):
    d = {}
    for data in datas:
        type_ = data[0]
        value_ = data[1]
        title = data[2]
        file_name = data[3]
        checked = data[4]
        if file_name not in d:
            d[file_name] = [(type_, value_, title, checked)]
        else:
            d[file_name].append((type_, value_, title, checked))
    return d


@ajax_required
def post(request):
    try:
        last_feed_datetime = get_datetime_from_string(request.POST.get('last_feed'))
        user = request.user
        csrf_token = (csrf(request)['csrf_token'])
        # postする
        post_common(request, user)
        if check_match_query(request, str(user)):
            html = _html_feeds(last_feed_datetime, user, csrf_token)
            return HttpResponse(html)
        else:
            return HttpResponse('')
    except Exception as e:
        traceback.print_exc()
        return HttpResponseServerError(str(e))


@ajax_required
def like(request):
    # Like元のパッケージID
    package_id = request.POST['package_id']
    feed = Feed.get_feeds_from_package_id(request.user, package_id)

    # user は STIPUser
    stip_user = request.user

    # liker情報取得
    likers = rs.get_likers_from_rs(stip_user, package_id)
    # すでにLikeされているか判定
    # 自分自身の liker 文字列は instance_name + space + user_name
    myliker = '%s %s' % (SNSConfig.get_sns_identity_name(), stip_user.username)
    like = myliker in likers
    # Like/Unlike 用の STIX イメージ作成
    x_stip_sns_object_ref_version = '1.2'
    bundle = get_like_stix2_bundle(
        package_id,
        x_stip_sns_object_ref_version,
        like,
        feed.tlp,
        stip_user
    )
    _regist_bundle(stip_user, bundle)

    if like:
        # notify の unlike処理
        stip_user.unotify_liked(package_id, feed.user)
    else:
        # notify の like処理
        stip_user.notify_liked(package_id, feed.user)
    # 現在の Like 情報を取得する
    likers = rs.get_likers_from_rs(stip_user, package_id)
    return HttpResponse(len(likers))


@login_required
def attach(request):
    file_id = request.POST['file_id']
    attach_file_name = Feed.get_attach_file_name(file_id)
    attach_file_path = Feed.get_attach_file_path(file_id).encode('utf-8')
    # response作成
    with open(attach_file_path, 'rb') as fp:
        response = HttpResponse(fp.read(), content_type='application/octet-stream')
        dl_file_name = urllib.parse.quote(attach_file_name)
        response['Content-Disposition'] = "attachment; filename='{}'; filename*=UTF-8''{}".format(dl_file_name, dl_file_name)
    return response


@ajax_required
def comment(request):
    # user は STIPUser
    stip_user = request.user
    if request.method == 'POST':
        # 引数取得
        package_id = request.POST['package_id']
        # コメント投稿
        post_comment(stip_user, package_id, request.POST['post'], stip_user)
        # 表示用
        comments = rs.get_comment_from_rs(stip_user, package_id)
        feeds = []
        for comment in comments:
            feeds.append(Feed.get_feeds_from_package_from_rs(stip_user, comment))
        return render(request, 'feeds/partial_feed_comments.html',
                      {'feeds': feeds})

    else:
        # 引数取得
        package_id = request.GET['package_id']
        comments = rs.get_comment_from_rs(stip_user, package_id)
        feeds = []
        for comment in comments:
            feeds.append(Feed.get_feeds_from_package_from_rs(stip_user, comment))
        return render(request, 'feeds/partial_feed_comments.html',
                      {'feeds': feeds})


# comment postする(共通)
def post_comment(api_user, original_package_id, post, comment_user):
    # Feed 情報作成
    origin_feed = Feed.get_feeds_from_package_id(api_user, original_package_id)
    # comment 作成
    post = post.strip()
    if len(post) > 0:
        post = post[:10240]
    # Comment 用の STIX イメージ作成
    origin_stix_file = rs.get_package_info_from_package_id(
        api_user, original_package_id
    )
    origin_stix_version = origin_stix_file['version']
    bundle = get_comment_stix2_bundle(
        original_package_id,
        origin_stix_version,
        post,
        origin_feed.tlp,
        comment_user
    )
    _regist_bundle(api_user, bundle)
    # 通知
    comment_user.notify_commented(original_package_id, origin_feed.user)
    notify_also_commented(original_package_id, origin_feed.user, comment_user)


# Profile にあった内容をこちらに移動
def notify_also_commented(package_id, feed_user, comment_user):
    from ctirs.models import Notification
    comments = rs.get_comment_from_rs(comment_user, package_id)
    users = []
    for comment in comments:
        uploader_id = int(comment['uploader'])
        # uploader -> かつてのコメントユーザー
        # comment -> 最新のコメントを入力したユーザー
        # feed_user -> root 投稿ユーザー
        if uploader_id != comment_user.id and uploader_id != feed_user.id:
            users.append(comment['uploader'])

    users = list(set(users))
    for user in users:
        Notification(notification_type=Notification.ALSO_COMMENTED,
                     from_user=comment_user,
                     to_user=STIPUser(id=user), package_id=package_id).save()


# Cache dir に feed_stix の中身を一時ファイルとして作成し、ファイルパスを返却する
def write_like_comment_attach_stix(content):
    # 一時的ファイルにstixの中身を書き出す
    _tmp, tmp_file_path = tempfile.mkstemp(dir=const.STIX_CACHE_DIR)
    with open(tmp_file_path, 'wb+') as fp:
        fp.write(content)
    return tmp_file_path


@ajax_required
# 一定期間ごと (30s)に feed_source に関連する like, comment 情報を更新する
def update(request):
    first_feed_datetime = get_datetime_from_string(request.GET.get('first_feed'))
    last_feed_datetime = get_datetime_from_string(request.GET.get('last_feed'))
    feed_source = request.GET.get('feed_source')
    feeds = Feed.get_feeds(
        range_big_datetime=first_feed_datetime,  # 期間範囲指定の大きい方(新しい方)。この時間を含む
        range_small_datetime=last_feed_datetime,  # 期間範囲指定の小さい方(古い方)。この時間を含む
        api_user=request.user)

    if feed_source != 'all':
        list_ = []
        for feed in feeds:
            if feed.package_id == feed_source:
                list_.append(feed)
        feeds = list_
    dump = {}
    for feed in feeds:
        feed = Feed.add_like_comment_info(request.user, feed)
        dump[feed.pk] = {'likes': feed.likes, 'comments': feed.comments}
    data = json.dumps(dump)
    return HttpResponse(data, content_type='application/json')


@ajax_required
def track_comments(request):
    # 引数取得
    stip_user = request.user
    package_id = request.GET['package_id']
    comments = rs.get_comment_from_rs(stip_user, package_id)
    feeds = []
    for comment in comments:
        feeds.append(Feed.get_feeds_from_package_from_rs(stip_user, comment))
    return render(request, 'feeds/partial_feed_comments.html',
                  {'feeds': feeds})


@ajax_required
def remove(request):
    # remove 処理
    package_id = request.POST['package_id']
    sns_config = SNSConfig.objects.get()
    rs_host = sns_config.rs_host
    remove_package_ids = None

    url = rs_host + '/api/v1/stix_files_package_id/' + package_id
    headers = rs._get_ctirs_api_http_headers(request.user)
    # RSへRemove処理
    r = requests.delete(
        url,
        headers=headers,
        verify=False)
    if r.status_code != requests.codes.ok:
        return HttpResponseServerError(r)

    # cache original 削除
    if r.text:
        body = json.loads(r.text)
        remove_package_ids = body.get('remove_package_ids')
    if remove_package_ids:
        for remove_package_id in remove_package_ids:
            remove_file_name_id = rs.convert_package_id_to_filename(remove_package_id)
            remove_path = Feed.get_cached_file_path(remove_file_name_id)
            try:
                os.remove(remove_path)
            # ファイルが見つからない、ディレクトリのときは無視する
            except FileNotFoundError:
                pass
            except IsADirectoryError:
                pass
    return HttpResponse()


# request から L2 の GV の URL を構築する
def _get_ctim_gv_url(request):
    # 設定ファイルに指定があったらその値を使う
    if (SNSConfig.get_gv_l2_url() is not None) and (len(SNSConfig.get_gv_l2_url()) != 0):
        return SNSConfig.get_gv_l2_url()
    # ない場合は request の値から URL 構築する
    scheme = request.scheme
    host = request.get_host()
    host_split = host.split(':')
    if len(host_split) == 1:
        gv_host = '%s:%d' % (host, DEFAULT_GV_PORT)
    else:
        gv_host = '%s:%d' % (host_split[0], DEFAULT_GV_PORT)
    gv_url = '%s://%s%s' % (scheme, gv_host, L2_GV_PATH)
    return gv_url


@ajax_required
def get_ctim_gv_url(request):
    try:
        package_id = request.GET['package_id']
        url = '%s?package_id=%s' % (_get_ctim_gv_url(request), package_id)
        return HttpResponse(url)
    except Exception as e:
        return HttpResponseServerError(str(e))


@ajax_required
def share_misp(request):
    try:
        package_id = request.GET['package_id']
        # user は STIPUser
        stip_user = request.user
        # RS に misp 共有要求
        resp = rs.share_misp(stip_user, package_id)
        return HttpResponse(resp['url'])
    except Exception as e:
        return HttpResponseServerError(str(e))


def _get_indicators_from_feed_id(feed_id):
    feed = Feed.objects.get(filename_pk=feed_id)
    if feed.stix_version.startswith('1.'):
        feed_stix = get_feed_stix(feed_id)
        return FeedStix.get_indicators(feed_stix.stix_package, indicator_only=True)
    else:
        return get_csv_from_bundle_id(feed_id, indicators=True, vulnerabilities=False, threat_actors=False)


@ajax_required
def sighting_splunk(request):
    try:
        feed_file_name_id = request.GET['feed_id']
        indicators = _get_indicators_from_feed_id(feed_file_name_id)
        # user は STIPUser
        stip_user = request.user
        sightings = get_sightings(stip_user, indicators)
        return HttpResponse(json.dumps(sightings))
    except Exception as e:
        traceback.print_exc()
        return HttpResponseServerError(str(e))


@login_required
def create_sighting_object(request):
    try:
        package_id = request.GET['package_id']
        feed_id = request.GET['feed_id']
        value_ = request.GET['value']
        type_ = request.GET['type']
        count = int(request.GET['count'])
        first_seen = request.GET['first_seen']
        last_seen = request.GET['last_seen']
        observable_id = request.GET['observable_id']

        stip_user = request.user
        feed = Feed.get_feeds_from_package_id(stip_user, package_id)
        stix_file_path = Feed.get_cached_file_path(feed_id)
        if feed.stix_version.startswith('1.'):
            stix2 = stip_sighting.convert_to_stix_1x_to_21(stix_file_path)
        elif feed.stix_version == '2.0':
            with open(stix_file_path, 'r') as fp:
                stix20_json = json.load(fp)
            stix2 = stip_sighting.convert_to_stix_20_to_21(stix20_json)
        else:
            with open(stix_file_path, 'rb') as fp:
                stix2 = parse(fp.read(), allow_custom=True)

        stix2 = stip_sighting.insert_sighting_object(
            stix2,
            type_, value_, observable_id,
            count, first_seen, last_seen,
            stip_user)

        stix2_str = stix2.serialize(True, ensure_ascii=False)

        _, stix2_file_path = tempfile.mkstemp()
        with open(stix2_file_path, 'w', encoding='utf-8') as fp:
            fp.write(stix2_str)
        # RS に登録する
        rs.regist_ctim_rs(feed.user, stix2.id, stix2_file_path)
        os.remove(stix2_file_path)

        file_name = '%s.json' % (stix2.id)
        output = io.StringIO()
        output.write(str(stix2_str))
        response = HttpResponse(output.getvalue(), content_type='application/json')
        response['Content-Disposition'] = 'attachment; filename=%s' % (file_name)
        return response
    except Exception as e:
        traceback.print_exc()
        return HttpResponseServerError(str(e))


@ajax_required
def run_phantom_playbook(request):
    try:
        feed_file_name_id = request.GET['feed_id']
        indicators = _get_indicators_from_feed_id(feed_file_name_id)
        # user は STIPUser
        stip_user = request.user
        container_id = call_run_phantom_playbook(stip_user, indicators)
        url = 'https://%s/mission/%s/analyst/timeline' % (stip_user.sns_profile.phantom_host, container_id)
        rsp = {
            'url': url,
        }
        return JsonResponse(rsp)
    except Exception as e:
        traceback.print_exc()
        return HttpResponseServerError(str(e))


@ajax_required
def call_jira(request):
    try:
        # JIRA が import されていない場合は何もしない
        if imported_jira is None:
            rsp = {}
            return JsonResponse(rsp)
        # feed情報取得
        feed_file_name_id = request.GET['feed_id']
        package_id_arg = request.GET['package_id']
        feed = Feed.get_feeds_from_package_id(request.user, package_id_arg)

        # JIRA instance
        proxies = System.get_request_proxies()
        j = JIRA(
            server=SNSConfig.get_jira_host(),
            proxies=proxies,
            basic_auth=(SNSConfig.get_jira_username(), SNSConfig.get_jira_password()))
        # issues作成
        issue = j.create_issue(
            project=SNSConfig.get_jira_project(),
            summary=feed.title,
            description=feed.post,
            issuetype={
                'name': SNSConfig.get_jira_type()
            })
        if feed.stix_version.startswith('1.'):
            j = _set_jira_param_v1(feed, feed_file_name_id, j, issue)
        elif feed.stix_version.startswith('2.'):
            j = _set_jira_param_v2(feed, feed_file_name_id, j, issue)
        else:
            return HttpResponseServerError('Invalid Stix Version')

        # isssue番号返却
        url = SNSConfig.get_jira_host() + '/projects/' + SNSConfig.get_jira_project() + '/issues/' + str(issue)
        rsp = {
            'issues': str(issue),
            'url': url,
        }
        return JsonResponse(rsp)
    except Exception as e:
        traceback.print_exc()
        return HttpResponseServerError(str(e))


def _set_jira_param_v2(feed, feed_file_name_id, j, issue):
    for attach_file in feed.files.all():
        attach_file_path = Feed.get_attach_file_path(attach_file.package_id)
        j.add_attachment(
            issue=issue,
            attachment=attach_file_path,
            filename=attach_file.file_name)

    with open(feed.stix_file_path, 'r') as fp:
        bundle = json.load(fp)
    package_id = bundle['id']
    stix_file_name = '%s.json' % (package_id)
    j.add_attachment(
        issue=issue,
        attachment=feed.stix_file_path,
        filename=stix_file_name)

    indicators = get_csv_from_bundle_id(
        feed.package_id,
        indicators=True,
        vulnerabilities=True,
        threat_actors=False)
    if len(indicators) > 0:
        content = ''
        for indicator in indicators:
            type_, value, _ = indicator
            content += '%s,%s\n' % (type_, value)
        csv_attachment = io.StringIO()
        csv_attachment.write(content)
        csv_file_name = '%s.csv' % (package_id)
        j.add_attachment(
            issue=issue,
            attachment=csv_attachment,
            filename=csv_file_name)

    # PDF
    feed_pdf = FeedPDF()
    pdf_attachment = io.BytesIO()
    feed_pdf.make_pdf_content(pdf_attachment, feed)
    pdf_file_name = '%s.pdf' % (package_id)
    j.add_attachment(
        issue=issue,
        attachment=pdf_attachment,
        filename=pdf_file_name)
    return j


def _set_jira_param_v1(feed, feed_file_name_id, j, issue):
    # 添付があればそれもつける
    for attach_file in feed.files.all():
        file_path = Feed.get_attach_file_path(attach_file.package_id)
        j.add_attachment(
            issue=issue,
            attachment=file_path,
            filename=str(attach_file.file_name))

    # STIX添付
    stix_package = STIXPackage.from_xml(feed.stix_file_path)
    package_id = stix_package.id_
    stix_file_name = '%s.xml' % (package_id)
    j.add_attachment(
        issue=issue,
        attachment=feed.stix_file_path,
        filename=stix_file_name)

    # CSV添付
    # CSVの中身を取得する
    indicators = _get_indicators_from_feed_id(feed_file_name_id)
    content = _get_csv_content_from_indicators(indicators)
    csv_attachment = io.StringIO()
    csv_attachment.write(content)
    csv_file_name = '%s.csv' % (package_id)
    j.add_attachment(
        issue=issue,
        attachment=csv_attachment,
        filename=csv_file_name)

    # PDF添付
    feed_pdf = FeedPDF()
    pdf_attachment = io.BytesIO()
    feed_pdf.make_pdf_content(pdf_attachment, feed)
    pdf_file_name = '%s.pdf' % (package_id)
    j.add_attachment(
        issue=issue,
        attachment=pdf_attachment,
        filename=pdf_file_name)
    return j


@login_required
def download_stix(request):
    package_id = request.GET['package_id']
    version = request.GET['version']

    # rs から stix の中身を取得
    content = rs.get_content_from_rs(
        request.user, package_id, version)

    if version.startswith('2.'):
        response = HttpResponse(content, content_type='application/json')
        file_name = '%s.json' % (package_id)
    else:
        response = HttpResponse(content, content_type='application/xml')
        file_name = '%s.xml' % (package_id)
    response['Content-Disposition'] = 'attachment; filename=%s' % (file_name)
    return response


def get_feed_stix(feed_file_name_id):
    stix_file_path = Feed.get_cached_file_path(feed_file_name_id)
    return FeedStix(stix_file_path=stix_file_path)


def _get_bundle_from_bundle_id(bundle_id):
    stix_file_path = Feed.get_cached_file_path(bundle_id)
    with open(stix_file_path, 'rb') as fp:
        bundle = parse(fp.read(), allow_custom=True)
    return bundle


stix2_pattern_ipv4_reg_str = "ipv4-addr:value\s*=\s*'?(.+)'"
stix2_pattern_ipv4_reg = re.compile(stix2_pattern_ipv4_reg_str)
stix2_pattern_url_reg_str = "url:value\s*=\s*'?(.+)'"
stix2_pattern_url_reg = re.compile(stix2_pattern_url_reg_str)
stix2_pattern_filename_reg_str = "file:name\s*=\s*'?(.+)'"
stix2_pattern_filename_reg = re.compile(stix2_pattern_filename_reg_str)
stix2_pattern_md5_reg_str = "file:hashes.'MD5'\s*=\s*'?(.+)'"
stix2_pattern_md5_reg = re.compile(stix2_pattern_md5_reg_str)
stix2_pattern_sha1_reg_str = "file:hashes.'SHA1'\s*=\s*'?(.+)'"
stix2_pattern_sha1_reg = re.compile(stix2_pattern_sha1_reg_str)
stix2_pattern_sha256_reg_str = "file:hashes.'SHA256'\s*=\s*'?(.+)'"
stix2_pattern_sha256_reg = re.compile(stix2_pattern_sha256_reg_str)
stix2_pattern_sha512_reg_str = "file:hashes.'SHA512'\s*=\s*'?(.+)'"
stix2_pattern_sha512_reg = re.compile(stix2_pattern_sha512_reg_str)
stix2_pattern_domain_reg_str = "domain-name:value\s*=\s*'?(.+)'"
stix2_pattern_domain_reg = re.compile(stix2_pattern_domain_reg_str)
stix2_pattern_email_reg_str = "email-addr:value\s*=\s*'?(.+)'"
stix2_pattern_email_reg = re.compile(stix2_pattern_email_reg_str)
CYBOX_OBJECT_TYPE_LIST = ['ipv4-addr', 'url', 'domain-name', 'email-addr', 'file']


def _get_csv_from_cybox(cybox):
    if cybox.type == 'ipv4-addr':
        return [('ipv4', cybox.value)]
    if cybox.type == 'url':
        return [('url', cybox.value)]
    if cybox.type == 'domain-name':
        return [('domain', cybox.value)]
    if cybox.type == 'email-addr':
        return [('e-mail', cybox.value)]
    if cybox.type == 'file':
        ret = []
        if 'name' in cybox:
            ret.append(('file_name', cybox.name))
        if 'hashes' in cybox:
            hashes = cybox.hashes
            if 'MD5' in hashes:
                ret.append(('md5', hashes['MD5']))
            if 'SHA-1' in hashes:
                ret.append(('sha1', hashes['SHA-1']))
            if 'SHA-256' in hashes:
                ret.append(('sha256', hashes['SHA-256']))
            if 'SHA-512' in hashes:
                ret.append(('sha512', hashes['SHA-512']))
        return ret
    return [(None, None)]


def get_csv_from_bundle_id(bundle_id, indicators=True, vulnerabilities=True, threat_actors=False):
    bundle = _get_bundle_from_bundle_id(bundle_id)
    ret = []
    for o_ in bundle['objects']:
        if isinstance(o_, sdo_20.Indicator) or isinstance(o_, sdo_21.Indicator):
            if not indicators:
                continue
            type_, value = _get_indicator_from_pattern(o_)
            if type_:
                ret.append((type_, value, _get_description(o_)))
        elif isinstance(o_, sdo_20.Vulnerability) or isinstance(o_, sdo_21.Vulnerability):
            if not vulnerabilities:
                continue
            if 'external_references' not in o_:
                continue
            for er in o_.external_references:
                type_, value = _get_cve_from_external_reference(er)
            if type_:
                ret.append((type_, value, _get_description(o_)))
        elif isinstance(o_, sdo_20.ObservedData) or isinstance(o_, sdo_21.ObservedData):
            if not indicators:
                continue
            if 'objects' not in o_:
                continue
            for key in o_.objects.keys():
                cybox = o_.objects[key]
                if cybox.type not in CYBOX_OBJECT_TYPE_LIST:
                    continue
                ret = _append_cybox_csv(ret, cybox)
        elif isinstance(o_, sdo_20.ThreatActor) or isinstance(o_, sdo_21.ThreatActor):
            if not threat_actors:
                continue
            ret.append(('threat_actor', o_.name, _get_description(o_)))
        else:
            if not indicators:
                continue
            if o_.type not in CYBOX_OBJECT_TYPE_LIST:
                continue
            ret = _append_cybox_csv(ret, o_)
    return ret


def _append_cybox_csv(csv_list, cybox):
    cybox_list = _get_csv_from_cybox(cybox)
    for cybox in cybox_list:
        type_, value = cybox
        if type_:
            csv_list.append((type_, value, ''))
    return csv_list


def _get_description(o_):
    if 'description' in o_:
        return o_['description']
    else:
        return ''


def _get_cve_from_external_reference(er):
    return ('cve', er['external_id'])


def _get_indicator_from_pattern(indicator):
    pattern_str = indicator.pattern
    stix2_patterns = [
        ('ipv4', stix2_pattern_ipv4_reg),
        ('url', stix2_pattern_url_reg),
        ('file_name', stix2_pattern_filename_reg),
        ('md5', stix2_pattern_md5_reg),
        ('sha1', stix2_pattern_sha1_reg),
        ('sha256', stix2_pattern_sha256_reg),
        ('sha512', stix2_pattern_sha512_reg),
        ('e-mail', stix2_pattern_email_reg),
        ('domain', stix2_pattern_domain_reg),
    ]
    for stix2_pattern in stix2_patterns:
        type_ = stix2_pattern[0]
        pattern = stix2_pattern[1]
        result = pattern.search(pattern_str)
        if result:
            return (type_, result[1])
    return (None, None)


@ajax_required
def is_exist_indicator(request):
    feed_file_name_id = request.POST['feed_id']
    indicators = _get_indicators_from_feed_id(feed_file_name_id)
    return HttpResponse(len(indicators) != 0)


@login_required
def download_csv(request):
    feed_file_name_id = request.POST['feed_id']
    indicators = _get_indicators_from_feed_id(feed_file_name_id)
    content = _get_csv_content_from_indicators(indicators)
    file_name = '%s.csv' % feed_file_name_id
    output = io.StringIO()
    output.write(content)
    response = HttpResponse(output.getvalue(), content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=%s' % (file_name)
    return response


def _get_csv_content_from_indicators(indicators):
    content = ''
    for indicator in indicators:
        type_, value, _ = indicator
        content += '%s,%s\n' % (type_, value)
    return content


@login_required
def download_pdf(request):
    # 引数取得
    feed_file_name_id = request.POST['feed_id']
    package_id = request.POST['package_id']

    # STIX 情報作成
    feed = Feed.get_feeds_from_package_id(request.user, package_id)
    # PDF 情報作成
    feed_pdf = FeedPDF()

    # HttpResponse作成
    file_name = '%s.pdf' % (feed_file_name_id)
    response = HttpResponse(content='application/pdf')
    # responseにPDF格納
    feed_pdf.make_pdf_content(response, feed)
    response['Content-Disposition'] = 'attachment; filename=%s' % (file_name)
    response['Content-Type'] = 'application/pdf'
    return response


# stix_packageからpostコンテンツを取得する
def get_post_from_stix_content(stix_package):
    description = ''
    short_description = ''
    # headerのdescriptionがあればそこから取得する
    try:
        v = stix_package.stix_header.description
        if v is not None and len(v.value) != 0:
            description = v.value
    except BaseException:
        pass

    # headerのshort_descriptionがあればそこから取得する
    try:
        v = stix_package.stix_header.short_description
        if v is not None and len(v.value) != 0:
            short_description = v.value
    except BaseException:
        pass
    return '<b>Description:</b> %s\n<b>Short Description</b>: %s' % (description, short_description)


# 添付ファイル格納ディレクトリのルートパス取得
def get_attach_root_dir_path():
    return const.ATTACH_FILE_DIR


# IDごとの添付ファイル格納ディレクトリパス取得
def get_attach_dir_path(id_):
    return '%s%s%s' % (get_attach_root_dir_path(), str(id_), os.sep)


# nameのファイル名とfの内容から添付ファイルを保存し、
# attach_fileレコードを作成して返却する
def save_attach_file(filename, content, id_):
    attach_file = AttachFile()
    attach_file.file_name = filename

    # attach格納ディレクトリ作成
    attach_root_dir = get_attach_root_dir_path()
    if not os.path.exists(attach_root_dir):
        os.makedirs(attach_root_dir)
    attach_dir = get_attach_dir_path(id_)
    if not os.path.exists(attach_dir):
        os.makedirs(attach_dir)

    # 一時ファイルに保存
    _, tmp_file_path = tempfile.mkstemp(dir=attach_dir)
    with open(tmp_file_path, 'wb+') as fp:
        # content.read()はstr
        fp.write(content.read())
    # MD5値取得
    with open(tmp_file_path, 'rb') as fp:
        v = fp.read()
        md5 = hashlib.md5(v).hexdigest()

    # rename
    if attach_dir[-1] == '/':
        d_dir = attach_dir[:-1]
    else:
        d_dir = attach_dir
    file_path = d_dir + md5
    os.rename(tmp_file_path, file_path)

    # ファイルパスを保存
    attach_file.file_path = file_path
    attach_file.save()
    return attach_file


# RS に関連 STIX を問い合わせ、結果をコメント表示
def post_rs_indicator_matching_comment(request, feed, id_, concierge_user):
    try:
        # RS にrelated packages 問い合わせ
        matching_data = rs.get_matching_from_rs(concierge_user, id_)
        if len(matching_data) == 0:
            # 存在しない場合はコメントしない
            return

        # 存在する場合
        url = '%s?package_id=%s' % (_get_ctim_gv_url(request), id_)
        msg = str(len(matching_data))
        msg += ' '
        msg += 'related package(s) are found.'
        msg += '\n<br/>\n'
        msg += '<a href= "%s" target="_blank">' % (url)
        msg += 'Check those package(s).'
        msg += '</a>'
        # 指定User で投稿
        post_comment(concierge_user, id_, msg, concierge_user)
    except Exception:
        traceback.print_exc()


# CrowdStrike に関連 Report を問い合わせ、結果をコメント表示
# def post_crowd_strike_indicator_matching_comment(feed, id_, concierge_user, json_indicators):
#    try:
#        realted_reports = []
#        phantom_indicators = []
#        for json_indicator in json_indicators:
#            value = json_indicator['value']
#            results = search_indicator(value)
#            for result in results:
#                if 'reports' not in result:
#                    # reports がない場合は skip
#                    continue
#                else:
#                    phantom_indicators.append(json_indicator)
#                # report を追加する
#                for report in result['reports']:
#                    realted_reports.append(report)
#        # 重複を取り除く
#        realted_reports = list(set(realted_reports))
#        if len(realted_reports) == 0:
#            # 存在しない場合はコメントしない
#            return

#        # 存在する場合
#        msg = str(len(realted_reports))
#        msg += ' '
#        msg += 'related report(s) are found.'
#        msg += '\n<br/>\n'
#        msg += 'Reports: <br/>'
#        for realted_report in realted_reports:
#            # report id から report title と URL を取得する
#            report_title, url = get_report_info(realted_report)
#            msg += ('<a href="%s" target="_blank">%s</a><br/>' % (url, report_title))

#        if len(phantom_indicators) != 0:
#            # phantom 連携できる indicator あり
#            msg += ('<a class="anchor-phantom-run-playbook" data-id="%s">Run Phantom Playbook</a>' % (id_))
#            for phantom_indicator in phantom_indicators:
#                msg += '<div id="%s" data-type="%s" data-value="%s"></div>' % ('phantom-data-' + id_, phantom_indicator['type'], phantom_indicator['value'])
#        # 指定User で投稿
#        post_comment(concierge_user, id_, msg, concierge_user)
#    except Exception:
#        # traceback.print_exc()
#        pass


def _get_package_name_from_bundle(bundle):
    try:
        for o_ in bundle['objects']:
            if o_['type'] == const.STIP_STIX2_X_STIP_SNS_TYPE:
                return o_['name']
        return bundle.id
    except Exception:
        return bundle.id


def _regist_bundle(feed_user, bundle):
    _, stix2_file_path = tempfile.mkstemp()
    with open(stix2_file_path, 'w', encoding='utf-8') as fp:
        fp.write(bundle.serialize(True, ensure_ascii=False))
    # RS に登録する
    package_name = _get_package_name_from_bundle(bundle)
    rs.regist_ctim_rs(feed_user, package_name, stix2_file_path)
    os.remove(stix2_file_path)
    return


def get_produced_str(bundle):
    for o_ in bundle['objects']:
        if o_['type'] == const.STIP_STIX2_X_STIP_SNS_TYPE:
            return o_['created'].strftime('%Y-%m-%d %H:%M:%S.%f')
    return None


# feedを保存する
def save_post(request,
              feed,
              post,
              json_indicators=[],
              ttps=[],
              tas=[],
              request_files=[],
              stix2_titles=[],
              stix2_contents=[]):
    if len(post) == 0:
        return None

    feed.post = post[:10240]
    sharing_range = FeedStixCommon._make_sharing_range_value(feed)

    tmp_feed_files = []
    x_stip_sns_attachment_refs = []
    for feed_file in request_files:
        x_stip_sns_attachment_bundle, x_stip_sns_attachment_id = get_attach_stix2_bundle(
            feed.tlp,
            feed.referred_url,
            sharing_range,
            feed_file,
            request.user)
        d = {}
        d[const.STIP_STIX2_SNS_ATTACHMENT_BUNDLE] = x_stip_sns_attachment_bundle.id
        d[const.STIP_STIX2_SNS_ATTACHMENT_STIP_SNS] = x_stip_sns_attachment_id

        x_stip_sns_attachment_refs.append(d)
        # StixFiles register
        _regist_bundle(feed.user, x_stip_sns_attachment_bundle)

        feed_file.produced_str = get_produced_str(x_stip_sns_attachment_bundle)
        feed_file.bundle_id = x_stip_sns_attachment_bundle.id
        tmp_feed_files.append(feed_file)
    if len(x_stip_sns_attachment_refs) == 0:
        x_stip_sns_attachment_refs = None

    bundle = get_post_stix2_bundle(
        json_indicators,
        ttps,
        tas,
        feed.title,
        post,
        feed.tlp,
        feed.referred_url,
        sharing_range,
        stix2_titles,
        stix2_contents,
        x_stip_sns_attachment_refs,
        request.user)

    feed.stix2_package_id = bundle.id
    feed.package_id = bundle.id

    for feed_file in tmp_feed_files:
        Feed.create_feeds_record_v2(
            feed.user,
            feed_file.bundle_id,
            feed.user.id,
            feed_file.produced_str,
            '2.1')

    _regist_bundle(feed.user, bundle)
    produced_str = get_produced_str(bundle)
    feed = Feed.create_feeds_record_v2(
        feed.user,
        bundle.id,
        feed.user.id,
        produced_str,
        '2.1',
        feed)
    resp = rs.get_package_info_from_package_id(feed.user, bundle.id)

    feed.date = Feed.get_datetime_from_string(resp['produced'])
    feed.stix_file_path = _write_stix_file(bundle)
    feed.save()

    if len(tmp_feed_files) > 1:
        # ファイルが複数
        # ファイルが添付されている場合は file upload をコメント付きで
        temp = tempfile.NamedTemporaryFile()
        with zipfile.ZipFile(temp.name, 'w', compression=zipfile.ZIP_DEFLATED) as new_zip:
            for file_ in tmp_feed_files:
                file_.seek(0)
                new_zip.writestr(file_.name, file_.read())
        uploaded_filename = 'uploaded_files.zip'
    elif len(tmp_feed_files) == 1:
        # ファイルが単数
        temp = tempfile.NamedTemporaryFile(delete=False)
        input_file = tmp_feed_files[0]
        input_file.seek(0)
        with open(temp.name, 'wb') as fp:
            fp.write(input_file.read())
        uploaded_filename = input_file.name
    else:
        temp = None

    if feed.user.username != const.SNS_SLACK_BOT_ACCOUNT:
        slack_post = ''
        slack_post += '[%s]\n' % (iocextract.defang(feed.title))
        slack_post += '\n'
        slack_post += '%s\n' % (iocextract.defang(feed.post))
        slack_post += '\n'
        slack_post += '---------- S-TIP Post Info (TLP: %s) ----------\n' % (feed.tlp)
        slack_post += '%s: %s\n' % ('Account', feed.user.username)
        slack_post += '%s: %s\n' % ('Package_ID', feed.package_id)
        slack_post += '%s: %s\n' % ('Referred URL', feed.referred_url if feed.referred_url is not None else '')
        slack_post = slack_post.replace('&amp;', '%amp;amp;')
        slack_post = slack_post.replace('&lt;', '%amp;lt;')
        slack_post = slack_post.replace('&gt;', '%amp;gt;')

        # Slack 投稿用の添付ファイル作成
        from boot_sns import StipSnsBoot
        wc = StipSnsBoot.get_slack_web_client()
        if wc is not None:
            post_slack_channel = SNSConfig.get_slack_bot_chnnel()
            if temp is not None:
                try:
                    # ファイルが添付されている場合は file uplaod をコメント付きで
                    wc.files_upload(
                        initial_comment=slack_post,
                        channels=post_slack_channel,
                        file=open(temp.name, 'rb'),
                        filename=uploaded_filename)
                finally:
                    # 閉じると同時に削除される
                    temp.close()
            else:
                try:
                    wc.chat_postMessage(
                        text=slack_post,
                        channel=post_slack_channel,
                        as_user='true')
                except Exception:
                    pass

    if len(json_indicators) > 0:
        run_gv_concierge_bot(request, bundle)
        # run_falcon_concierge_bot(request, bundle)
        # run_falcon_concierge_bot(bundle, json_indicators)
    return


# def run_falcon_concierge_bot(bundle, json_indicators):
#     if const.SNS_FALCON_CONCIERGE_ACCOUNT is not None:
#         try:
#             concierge_user = STIPUser.objects.get(
#                 username=const.SNS_FALCON_CONCIERGE_ACCOUNT)
#             crowd_strike_report_th = threading.Thread(
#                 target=post_crowd_strike_indicator_matching_comment,
#                 args=(feed, bundle.id, concierge_user, json_indicators))
#             crowd_strike_report_th.daemon = True
#             crowd_strike_report_th.start()
#         except Exception:
#             import traceback
#             traceback.print_exc()


def run_gv_concierge_bot(request, bundle):
    if const.SNS_GV_CONCIERGE_ACCOUNT is not None:
        try:
            concierge_user = STIPUser.objects.get(
                username=const.SNS_GV_CONCIERGE_ACCOUNT)
            matching_comment_th = threading.Thread(
                target=post_rs_indicator_matching_comment,
                args=(request, feed, bundle.id, concierge_user))
            matching_comment_th.daemon = True
            matching_comment_th.start()
        except Exception:
            pass


def _write_stix_file(bundle):
    stix_file_path = '%s%s%s' % (const.STIX_FILE_DIR, bundle.id, '.json')
    with open(stix_file_path, 'w', encoding='utf-8') as fp:
        fp.write(str(bundle))
    return stix_file_path


# stix_pakcageからTLPを取得する。
# 未定義の場合はuserごとのデフォルトTLPを返却する
def get_tlp_from_stix(stix_package, user):
    try:
        return stix_package.stix_header.handling.markings[0].marking_structures[0].color
    except BaseException:
        pass
    try:
        return stix_package.stix_header.handling[0].marking_structures[0].color
    except BaseException:
        pass
    # AIS用TLP
    try:
        return stix_package.stix_header.handling[0].marking_structures[0].not_proprietary.tlp_marking.color
    except BaseException:
        pass
    return user.tlp


# 投稿を開いた時の like,unlike 情報取得
@ajax_required
def get_like_comment(request):
    package_id = request.GET['package_id']
    # feed の like, comment 情報取得
    # 投稿があることが確定しているので直接 cache からFeed 取得
    feed = Feed.objects.get(package_id=package_id)
    Feed.add_like_comment_info(request.user, feed)
    rsp = {
        'likes': feed.likes,
        'like': feed.like,
        'comments': feed.comments
    }
    return JsonResponse(rsp)


def check_match_query(request, user):
    if 'query_string' in request.POST.keys() and KEY_SCREEN_NAME in request.POST.keys():
        query_string = request.POST['query_string']
        # 空白スペース区切りで分割
        query_strings = query_string.split(' ')
        # 空白スペース区切りで検索文字列が指定されていない場合(検索対象: 投稿/タイトル/ユーザ名/スクリーン名)
        if len(query_strings) == 1:
            if query_strings[0] in request.POST[KEY_POST] or query_strings[0] in request.POST[KEY_TITLE] or query_strings[0] in user or query_strings[0] in request.POST[KEY_SCREEN_NAME]:
                return True
            else:
                return False
        # 空白スペース区切りの場合(検索対象: 投稿/タイトル/ユーザ名/スクリーン名)
        else:
            for q in query_strings:
                if q in request.POST[KEY_POST] or q in request.POST[KEY_TITLE] or q in user or q in request.POST[KEY_SCREEN_NAME]:
                    continue
                else:
                    return False
    return True
