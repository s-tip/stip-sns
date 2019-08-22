# -*- coding: utf-8 -*
import json
import datetime
import pytz
import requests
from ctirs.models import SNSConfig, System

requests.packages.urllib3.disable_warnings()

# STATIC VALUE
ARTIFACT_TYPE = 's-tip_artifact'
CONTAINER_LABEL = 'events'


def get_base_url(sns_profile):
    return 'https://%s/rest' % (sns_profile.phantom_host)


def get_phantom_request_headers(sns_profile):
    headers = {
        'ph-auth-token': sns_profile.phantom_auth_token
    }
    return headers


def create_container_id(container_name, sns_profile, artifacts=[]):
    url = '%s/container' % (get_base_url(sns_profile))

    d = {
        "name": container_name,
        "label": CONTAINER_LABEL,
        "artifacts": artifacts,
    }

    headers = get_phantom_request_headers(sns_profile)
    resp = requests.post(
        url,
        headers=headers,
        proxies=System.get_request_proxies(),
        data=json.dumps(d),
        verify=False)

    if resp.status_code != 200:
        print '!!!! container error: status_code=%d' % (resp.status_code)
        print '!!!! container error: body =%s' % (json.dumps(resp.json()))
        return None
    j = resp.json()
    if j['success']:
        return j['id']
    else:
        print '!!!!error: body =%s' % (json.dumps(resp.json()))
        return None


def run_play_book(sns_profile, container_id, playbook_name):
    url = '%s/playbook_run' % (get_base_url(sns_profile))
    print url

    d = {
        "container_id": container_id,
        "playbook_id": playbook_name,
        "run": True,
        "scope": "new"
    }

    print d

    headers = get_phantom_request_headers(sns_profile)
    resp = requests.post(
        url,
        headers=headers,
        proxies=System.get_request_proxies(),
        data=json.dumps(d),
        verify=False)

    if resp.status_code != 200:
        print '!!!! playbook_run error: status_code=%d' % (resp.status_code)
        print '!!!! playbook_run error: body=%s' % (json.dumps(resp.json()))
        return None

    j = resp.json()
    if j['recieved']:
        return j['playbook_run_id']
    else:
        print '!!!!playbook_run error: body=%s' % (json.dumps(resp.json()))
        return None


def get_container_name(timezone):
    d = datetime.datetime.now(tz=pytz.timezone(timezone))
    t_str = d.strftime('%Y/%m/%d %H:%M:%S')
    return 'Event from S-TIP (%s)' % (t_str)


def get_artifact(cef):
    d = {
        "cef": cef,
        "type": ARTIFACT_TYPE,
    }
    return d


def get_cef(fileHash='', destinationAddress='', destinationDnsDomain='',requestURL=''):
    # Artifact Details
    cef = {
        "destinationAddress": destinationAddress,
        "destinationDnsDomain": destinationDnsDomain,
        "dst": destinationAddress,
        "fileHash": fileHash,
        "requestURL": requestURL,
    }
    return cef


def call_run_phantom_playbook(stip_user, indicators):
    artifacts = []
    for indicator in indicators:
        type_, value = indicator
        cef = None
        if type_ == 'ipv4':
            cef = get_cef(destinationAddress=value)
        elif type_ == 'domain':
            cef = get_cef(destinationDnsDomain=value)
        elif type_ == 'url':
            cef = get_cef(requestURL=value)
        if cef is None:
            continue
        artifacts.append(get_artifact(cef))

    container_name = get_container_name(stip_user.timezone)
    sns_profile = stip_user.sns_profile
    container_id = create_container_id(container_name, sns_profile, artifacts)
    playbook_name = '%s/%s' % (sns_profile.phantom_source_name, sns_profile.phantom_playbook_name)
    _ = run_play_book(sns_profile, container_id, playbook_name)
    return container_id
