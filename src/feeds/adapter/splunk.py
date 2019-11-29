import sys
import ssl
import pytz
import urllib.request
import urllib.parse
import urllib.error
import datetime
import splunklib.client as client
import splunklib.results as r
from splunklib.six.moves import urllib as splunk_urllib
from io import BytesIO
from ctirs.models import System

STATS_QUERY = '|stats earliest_time(_time),latest_time(_time),count'


def request(url, message, **kwargs):
    method = message['method'].lower()
    data = message.get('body', "") if method == 'post' else None
    headers = dict(message.get('headers', []))
    req = splunk_urllib.request.Request(url, data, headers)
    try:
        response = splunk_urllib.request.urlopen(req)
    except splunk_urllib.error.URLError as response:
        # If running Python 2.7.9+, disable SSL certificate validation and try again
        if sys.version_info >= (2, 7, 9):
            response = splunk_urllib.request.urlopen(req, context=ssl._create_unverified_context())
        else:
            raise
    except splunk_urllib.error.HTTPError as response:
        pass  # Propagate HTTP errors via the returned response message
    return {
        'status': response.code,
        'reason': response.msg,
        'headers': dict(response.info()),
        'body': BytesIO(response.read().encode('utf-8'))
    }


def handler(proxy_dict):
    proxy_handler = splunk_urllib.request.ProxyHandler(proxy_dict)
    opener = splunk_urllib.request.build_opener(proxy_handler)
    splunk_urllib.request.install_opener(opener)
    return request


def get_connect(sns_profile):
    proxies = System.get_request_proxies()
    con = client.connect(
        host=sns_profile.splunk_host,
        port=sns_profile.splunk_api_port,
        handler=handler(proxies),
        username=sns_profile.splunk_username,
        password=sns_profile.splunk_password,
        scheme=sns_profile.splunk_scheme)
    return con


def get_oneshot_query_count(con, query, timezone, **kwargs):
    results = con.jobs.oneshot(query, **kwargs)
    reader = r.ResultsReader(results)
    result = next(reader)
    sighting = {}
    sighting['count'] = int(result['count'])
    if sighting['count'] == 0:
        sighting['first_seen'] = 'N/A'
        sighting['last_seen'] = 'N/A'
    else:
        sighting['first_seen'] = get_datetime_from_epoch(result['earliest_time(_time)'], timezone)
        sighting['last_seen'] = get_datetime_from_epoch(result['latest_time(_time)'], timezone)
    return sighting


def get_datetime_from_epoch(epoch, timezone):
    dt = datetime.datetime.fromtimestamp(float(epoch), tz=pytz.timezone(timezone))
    dt_str = dt.strftime('%Y/%m/%d %H:%M:%S%z')
    return dt_str


def get_splunk_timestamp(dt):
    s_1 = dt.strftime('%Y-%m-%dT%H:%M:%S.000')
    s_2 = dt.strftime('%z')
    s = '%s%s:00' % (s_1, s_2[:3])
    return s


def get_sighting(stip_user, type_, value, id_, earliest_dt=None, latest_dt=None):
    kwargs = {
        'earliest_time': '' if earliest_dt is None else get_splunk_timestamp(earliest_dt),
        'latest_time': '' if latest_dt is None else get_splunk_timestamp(latest_dt),
    }

    sns_profile = stip_user.sns_profile
    con = get_connect(sns_profile)
    web_query = sns_profile.splunk_query.replace('%s', value)
    api_query = web_query + STATS_QUERY
    sighting = get_oneshot_query_count(con, api_query, stip_user.timezone, **kwargs)
    sighting['url'] = '%s://%s:%d/app/search/search?q=%s' % (sns_profile.splunk_scheme, sns_profile.splunk_host, sns_profile.splunk_web_port, urllib.parse.quote(web_query))
    sighting['type'] = type_
    sighting['value'] = value
    sighting['observable_id'] = id_
    return sighting


def get_sightings(stip_user, indicators):
    ALLOW_QUERY_INDICATOR_TYPES = ['ipv4', 'domain']
    sightings = []
    for indicator in indicators:
        type_, value, id_ = indicator
        if type_ in ALLOW_QUERY_INDICATOR_TYPES:
            sightings.append(get_sighting(stip_user, type_, value, id_))
    return sightings
