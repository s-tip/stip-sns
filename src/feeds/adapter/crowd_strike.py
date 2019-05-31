# -*- coding: utf-8 -*-
import json
import requests
from ctirs.models import SNSConfig

def get_crowd_strike_request_header():
    query_http_headers = {}
    custid = SNSConfig.get_cs_custid()
    custkey = SNSConfig.get_cs_custkey()
    if custid is not None:
        query_http_headers['X-CSIX-CUSTID'] = custid
    else:
        raise Exception ('No X-CSIX-CUSTID configuration.')
    if custkey is not None:
        query_http_headers['X-CSIX-CUSTKEY'] = custkey
    else:
        raise Exception ('No X-CSIX-CUSTKEY configuration.')
    query_http_headers['Content-Type'] = 'application/json'
    return query_http_headers

def request(url):
    #指定の url (CrowdStrike API) に request する
    resp = requests.get(url,headers=get_crowd_strike_request_header())
    return json.loads(resp.text)

def query_actors(query_value):
    #URL に query 指定する
    attack_query_url = u'https://intelapi.crowdstrike.com/actors/queries/actors/v1?q=' + query_value
    return request(attack_query_url)

def get_actor_entities(actor_id):
    #URL に actor_id  を指定する
    attacker_entities_url = u'https://intelapi.crowdstrike.com/actors/entities/actors/v1?ids=' + actor_id
    return request(attacker_entities_url)

def search_indicator(value):
    #URL に actor_id  を指定する
    search_indicator_url = u'https://intelapi.crowdstrike.com/indicator/v2/search/indicator?equal=' + value 
    j = request(search_indicator_url)
    return j

def query_reports(query_value):
    #URL に query 指定する
    reports_query_url = u'https://intelapi.crowdstrike.com/reports/queries/reports/v1?name=' + query_value
    return request(reports_query_url)

def get_report_entities(report_id):
    #URL に query 指定する
    reports_entity_url = u'https://intelapi.crowdstrike.com/reports/entities/reports/v1?ids=' + report_id
    return request(reports_entity_url)

#report id から report title と URL の tuple を返却する
def get_report_info(report_name):
    resp = query_reports(report_name)
    report_id = resp[u'resources'][0]
    resp = get_report_entities(report_id)
    #最初の要素を使う
    resource = resp['resources'][0]
    return (resource['name'],resource['url'])