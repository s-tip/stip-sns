import json
import time
import requests
import datetime
import pytz
import re
import tempfile
import asyncio
import nest_asyncio
import slack
import threading

from django.http.request import HttpRequest
from django.core.files.uploadedfile import SimpleUploadedFile
from boot_sns import StipSnsBoot
from ctirs.models import System, STIPUser, SNSConfig, AttachFile, Feed
from stip.common.const import TLP_CHOICES, SNS_SLACK_BOT_ACCOUNT
from feeds.views import get_merged_conf_list, post_common
from feeds.extractor.base import Extractor
from feeds.views import KEY_TLP as STIP_PARAMS_INDEX_TLP
from feeds.views import KEY_POST as STIP_PARAMS_INDEX_POST
from feeds.views import KEY_REFERRED_URL as STIP_PARAMS_INDEX_REFERRED_URL
from feeds.views import KEY_TITLE as STIP_PARAMS_INDEX_TITLE
from feeds.views import KEY_INDICATORS as STIP_PARAMS_INDEX_INDICATORS
from feeds.views import KEY_TTPS as STIP_PARAMS_INDEX_TTPS
from feeds.views import KEY_TAS as STIP_PARAMS_INDEX_TAS
from feeds.views import KEY_USERNAME as STIP_PARAMS_INDEX_USER_NAME

nest_asyncio.apply()

TLP_REGEX_PATTERN_STR = r'^.*{TLP:\s*([a-zA-Z]+)}.*$'
TLP_REGEX_PATTERN = re.compile(
    TLP_REGEX_PATTERN_STR,
    flags=(re.MULTILINE))
REFERRED_URL_PATTERN_STR = r'^.*{URL:\s*<(\S+)>}.*$'
REFERRED_URL_PATTERN = re.compile(
    REFERRED_URL_PATTERN_STR,
    flags=(re.MULTILINE))
COMMAND_STIX_PATTERN_STR = r'^:stix\s*(\S+)$'
COMMAND_STIX_PATTERN = re.compile(COMMAND_STIX_PATTERN_STR)
CHANNEL_PATTERN_STR = r'(?P<channel_info><#[0-9A-Z]+?\|(?P<channel_name>.+?)>)'
CHANNEL_PATTERN = re.compile(
    CHANNEL_PATTERN_STR,
    flags=(re.MULTILINE))
USER_ID_PATTERN_STR = '(?P<user_info><@(?P<user_id>[0-9A-Z]+?)>)'
USER_ID_PATTERN = re.compile(
    USER_ID_PATTERN_STR,
    flags=(re.MULTILINE))

# TLP_LIST 初期化
TLP_LIST = []
for choice in TLP_CHOICES:
    TLP_LIST.append(choice[0])


class SlackThread(threading.Thread):
    def __init__(self, slack_rtm_client):
        super().__init__()
        self.started = threading.Event()
        self.alive = True
        self.slack_rtm_client = slack_rtm_client
        self.start()

    def begin(self):
        self.started.set()

    def end(self):
        self.slack_rtm_client._stopped = True
        self.started.clear()

    def run(self):
        asyncio.ensure_future(
            self.slack_rtm_client.start(),
            loop=self.slack_rtm_client._event_loop)
        self.slack_rtm_client.stop()


def start_receive_slack_thread():
    slack_token = SNSConfig.get_slack_bot_token()
    if slack_token is None:
        print('Slack token is undefined.')
        return None, None, None
    if len(slack_token) == 0:
        print('Slack token length is 0.')
        return None, None, None
    # Slack ユーザがいなければ作る
    slack_users = STIPUser.objects.filter(username=SNS_SLACK_BOT_ACCOUNT)
    if len(slack_users) == 0:
        # slack ユーザ作成する
        slack_user = STIPUser.objects.create_user(
            SNS_SLACK_BOT_ACCOUNT,
            SNS_SLACK_BOT_ACCOUNT,
            SNS_SLACK_BOT_ACCOUNT,
            is_admin=False)
        slack_user.save()
    proxies = System.get_request_proxies()
    proxy_str = None
    if proxies:
        if 'https' in proxies:
            proxy_str = proxies['https']
    slack_web_client = slack.WebClient(
        token=slack_token,
        proxy=proxy_str)
    slack_rtm_client = slack.RTMClient(
        token=slack_token,
        proxy=proxy_str)
    th = SlackThread(slack_rtm_client)
    return slack_web_client, slack_rtm_client, th


def restart_receive_slack_thread():
    from boot_sns import StipSnsBoot
    th = StipSnsBoot.get_slack_thread()
    slack_rtm_client = StipSnsBoot.get_slack_rtm_client()
    slack_web_client = StipSnsBoot.get_slack_web_client()
    slack_token = SNSConfig.get_slack_bot_token()

    if th:
        th.end()
        th.join()

    proxies = System.get_request_proxies()
    proxy_str = None
    if proxies:
        if 'https' in proxies:
            proxy_str = proxies['https']
    if not slack_rtm_client:
        loop = asyncio.new_event_loop()
        slack_rtm_client = slack.RTMClient(
            token=slack_token,
            loop=loop,
            proxy=proxy_str)
    else:
        slack_rtm_client = slack.RTMClient(
            token=slack_token,
            loop=slack_rtm_client._event_loop,
            proxy=proxy_str)
    th = SlackThread(slack_rtm_client)
    return slack_web_client, slack_rtm_client, th


# 指定の stix id を返却する
def download_stix_id(command_stix_id):
    wc = StipSnsBoot.get_slack_web_client()
    # cache の STIX を返却
    stix_file_path = Feed.get_cached_file_path(
        command_stix_id.replace(':', '--'))
    file_name = '%s.xml' % (command_stix_id)
    post_slack_channel = SNSConfig.get_slack_bot_chnnel()
    wc.files_upload(
        initial_comment='',
        channels=post_slack_channel,
        file=open(stix_file_path, 'rb'),
        filename=file_name)
    return


# <#channel_id|channel_name> を channel_name に変更
def convert_channel_info(post):
    try:
        return CHANNEL_PATTERN.sub(r'#\g<channel_name>', post)
    except TypeError:
        return post


# <@USERID> を ユーザ名に変更
def convert_user_id(post):
    for user_info in USER_ID_PATTERN.finditer(post):
        user_profile = get_user_profile(user_info.group('user_id'))
        user_name = user_profile['real_name']
        post = post.replace(
            user_info.group('user_info'),
            '"@%s"' % (user_name))
    return post


# user_id から user_profile取得
def get_user_profile(user_id):
    wc = StipSnsBoot.get_slack_web_client()
    return wc.users_info(user=user_id)['user']['profile']


# slack 投稿データから stip 投稿を行う
def post_stip_from_slack(receive_data, slack_bot_channel_name, slack_user):
    wc = StipSnsBoot.get_slack_web_client()
    POST_INDEX_TITLE = 0

    if 'subtype' in receive_data:
        # 投稿以外のメッセージなので対象外
        return
    # user_id から user_info 取得
    try:
        user_id = receive_data['user']
    except KeyError:
        return
    user_profile = get_user_profile(user_id)

    # bot からの発言は対象外
    if 'bot_id' in user_profile:
        return

    # S-TIP 投稿データを取得する
    text = receive_data['text']
    stip_params = get_stip_params(text, user_profile['display_name'])
    if stip_params is None:
        return

    # 添付file データ取得
    files_for_cti_extractor, files_for_stip_post = get_attached_files(receive_data)

    # CTI Element Extractor 追加
    stip_params = set_extractor_info(
        stip_params,
        files_for_cti_extractor,
        user_profile['display_name'])

    # 本文に各種 footer 情報を追加
    post = stip_params[STIP_PARAMS_INDEX_POST]

    # command 関連
    command_stix_id = get_command_stix_id(post)
    # :stix <stix_id>
    if command_stix_id is not None:
        download_stix_id(command_stix_id)
        return

    # <!here> が含まれている場合
    post = post.replace('<!here>', '@here')
    # <!channel> が含まれている場合
    post = post.replace('<!channel>', '@channel')
    # <@user_id> が含まれている場合
    post = convert_user_id(post)
    # <#channel_id|channnel_name> が含まれている場合
    post = convert_channel_info(post)

    post = post.replace('&', '&amp;')
    post = post.replace('<', '&lt;')
    post = post.replace('>', '&gt;')
    post += '\n----------Slack Message Info----------\n'

    # 1行目がtitle
    stip_params[STIP_PARAMS_INDEX_TITLE] = post.splitlines()[POST_INDEX_TITLE]

    # channle_id から channel 情報取得
    try:
        channel_id = receive_data['channel']
        channel_name = None
        try:
            resp = wc.conversations_info(channel=channel_id)
            # public channel
            channel_name = resp['channel']['name']
        except slack.errors.SlackApiError:
            # private channnel
            resp = wc.groups_info(channel=channel_id)
            channel_name = resp['group']['name']
        except Exception:
            # チャンネル名が取れないので skip
            pass
        if channel_name != slack_bot_channel_name:
            # 該当チャンネルではないの skip
            return
        post += ('%s: %s\n' % ('Channel', channel_name))
    except KeyError:
        # チャンネル名が取れないので skip
        return

    # アカウント名
    try:
        post += ('Full name: %s\n' % (user_profile['real_name']))
    except KeyError:
        # アカウント名が取れないので skip
        return

    # メッセージ id
    if 'client_msg_id' in receive_data:
        post += ('%s: %s\n' % ('Message ID', receive_data['client_msg_id']))

    if 'ts' in receive_data:
        ts = receive_data['ts']
        dt = datetime.datetime(*time.gmtime(float(ts))[:6], tzinfo=pytz.utc)
        post += ('%s: %s\n' % ('Timestamp', dt.strftime('%Y-%m-%dT%H:%M:%S.%f%z')))
    stip_params[STIP_PARAMS_INDEX_POST] = post

    # ここから SNS に投稿する
    try:
        request = HttpRequest()
        request.method = 'POST'
        request.POST = stip_params
        request.FILES = files_for_stip_post
        request.META['SERVER_NAME'] = 'localhost'
        request.user = slack_user
        post_common(request, slack_user)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise e
    return


@slack.RTMClient.run_on(event='message')
def receive_slack(**payload):
    # channel 名から先頭の # を外す
    slack_bot_channel_name = SNSConfig.get_slack_bot_chnnel()[1:]
    slack_user = STIPUser.objects.get(username=SNS_SLACK_BOT_ACCOUNT)
    receive_data = payload['data']

    try:
        post_stip_from_slack(receive_data, slack_bot_channel_name, slack_user)
    except BaseException:
        import traceback
        traceback.print_exc()


def get_attached_file_from_slack(file_path):
    slack_token = SNSConfig.get_slack_bot_token()
    headers = {}
    headers['Authorization'] = 'Bearer ' + slack_token
    proxies = System.get_request_proxies()
    resp = requests.get(
        url=file_path,
        headers=headers,
        proxies=proxies
    )
    return resp


def get_attached_files(receive_data):
    files_for_stip_post = {}
    files_for_cti_extractor = []
    if 'files' in receive_data:
        # 添付ファイルあり
        files = receive_data['files']
        for file_ in files:
            # attached_files 情報
            file_path = file_['url_private']
            file_name = file_['name']
            resp = get_attached_file_from_slack(file_path)
            uploaded_file = SimpleUploadedFile(file_name, resp.content)
            files_for_stip_post[file_name] = uploaded_file
            # django_files 情報
            attach_file = AttachFile()
            attach_file.file_name = file_name
            _, tmp_file_path = tempfile.mkstemp()
            attach_file.file_path = tmp_file_path
            with open(attach_file.file_path, 'wb') as fp:
                fp.write(resp.content)
            files_for_cti_extractor.append(attach_file)
    return files_for_cti_extractor, files_for_stip_post


def get_tlp(s):
    for l in s.split('\n'):
        m = TLP_REGEX_PATTERN.match(l)
        if m is None:
            continue
        else:
            tlp = m.group(1).upper()
            if tlp in TLP_LIST:
                return tlp
            else:
                continue
    return None


def get_referred_url(s):
    for l in s.split('\n'):
        m = REFERRED_URL_PATTERN.match(l)
        if m is None:
            continue
        else:
            return m.group(1)
    return ''


def get_command_stix_id(post):
    try:
        m = COMMAND_STIX_PATTERN.match(post)
        if m is None:
            return None
        else:
            return m.group(1)
    except BaseException:
        return None


def get_stip_params(slack_post, username):
    DEFAULT_TLP = 'WHITE'

    stip_params = {}

    try:
        stip_user = STIPUser.objects.get(username=username)
    except BaseException:
        stip_user = None

    # 投稿はすべて slack bot
    stip_params[STIP_PARAMS_INDEX_USER_NAME] = SNS_SLACK_BOT_ACCOUNT

    # TLP 抽出
    # S-TIP アカウントがあればその TLP を参照する
    tlp = get_tlp(slack_post)
    if tlp is not None:
        stip_params[STIP_PARAMS_INDEX_TLP] = tlp
    else:
        # 指定がない
        if stip_user is not None:
            stip_params[STIP_PARAMS_INDEX_TLP] = stip_user.tlp
        else:
            stip_params[STIP_PARAMS_INDEX_TLP] = DEFAULT_TLP

    # Referred URL 抽出
    referred_url = get_referred_url(slack_post)
    stip_params[STIP_PARAMS_INDEX_REFERRED_URL] = referred_url

    # post はすべて
    stip_params[STIP_PARAMS_INDEX_POST] = slack_post
    return stip_params


def set_extractor_info(stip_params, attached_files, username):
    try:
        stip_user = STIPUser.objects.get(username=username)
    except BaseException:
        stip_user = None

    if stip_user is not None:
        white_list = get_merged_conf_list(
            SNSConfig.get_common_white_list(),
            stip_user.sns_profile.indicator_white_list)
        ta_list = get_merged_conf_list(
            SNSConfig.get_common_ta_list(),
            stip_user.sns_profile.threat_actors)
    else:
        ta_list = []
        white_list = []

    eeb = Extractor.get_stix_element(
        files=attached_files,
        posts=[stip_params[STIP_PARAMS_INDEX_POST]],
        referred_url=stip_params[STIP_PARAMS_INDEX_REFERRED_URL] if len(
            stip_params[STIP_PARAMS_INDEX_REFERRED_URL]) != 0 else None,
        ta_list=ta_list,
        white_list=white_list
    )
    stip_params[STIP_PARAMS_INDEX_INDICATORS] = json.dumps(
        get_extractor_items(eeb.get_indicators()))
    stip_params[STIP_PARAMS_INDEX_TTPS] = json.dumps(
        get_extractor_items(eeb.get_ttps()))
    stip_params[STIP_PARAMS_INDEX_TAS] = json.dumps(
        get_extractor_items(eeb.get_tas()))
    return stip_params


def get_extractor_items(extractor_list):
    items = []
    for item in extractor_list:
        if item[4]:
            format_data = {}
            format_data['type'] = item[0]
            format_data['value'] = item[1]
            format_data['title'] = item[2]
            items.append(format_data)
    return items
