import json
import requests
from ctirs.models import SNSConfig, System


BASE_URL = 'https://api.crowdstrike.com'


def get_crowd_strike_request_header(access_token=None):
    query_http_headers = {}
    query_http_headers['accept'] = 'application/json'
    if access_token is not None:
        query_http_headers['Authorization'] = 'Bearer ' + access_token
    return query_http_headers


def get_access_token(proxies):
    OAUTH2_URL = BASE_URL + '/oauth2/token'
    payload = {}
    payload['client_id'] = SNSConfig.get_cs_custid()
    payload['client_secret'] = SNSConfig.get_cs_custkey()
    headers = get_crowd_strike_request_header()
    return requests.post(
        url=OAUTH2_URL,
        params=headers,
        data=payload,
        proxies=proxies)


def request_get(url):
    # 指定の url (CrowdStrike API) に request する
    proxies = System.get_request_proxies()
    access_token_rsp = get_access_token(proxies)
    if access_token_rsp.status_code != 201:
        return json.loads(access_token_rsp.text)
    else:
        access_token = access_token_rsp.json()['access_token']
    resp = requests.get(
        url,
        headers=get_crowd_strike_request_header(access_token),
        proxies=proxies)
    return json.loads(resp.text)


def request_post(url, data):
    # 指定の url (CrowdStrike API) に request する
    proxies = System.get_request_proxies()
    access_token_rsp = get_access_token(proxies)
    if access_token_rsp.status_code != 201:
        return json.loads(access_token_rsp.text)
    else:
        access_token = access_token_rsp.json()['access_token']
    resp = requests.post(
        url,
        headers=get_crowd_strike_request_header(access_token),
        json=data,
        proxies=proxies)
    return json.loads(resp.text)


def query_actors(query_value):
    # URL に query 指定する
    attack_query_url = BASE_URL + '/intel/queries/actors/v1?q=' + query_value
    return request_get(attack_query_url)


def get_actor_entities(actor_id):
    # URL に actor_id  を指定する
    attacker_entities_url = BASE_URL + '/intel/entities/actors/v1?ids=' + actor_id
    return request_get(attacker_entities_url)
