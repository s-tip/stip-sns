# -*- coding: utf-8 -*-
import datetime
import pytz
import feeds.extractor.common  as fec
from stix2.properties import StringProperty, ReferenceProperty, ListProperty
from stix2.v21.bundle import Bundle
from stix2.v21.sdo import Report, CustomObject, Vulnerability, ThreatActor, Indicator
from stix2.v21.common import LanguageContent, GranularMarking
from stip.common.stip_stix2 import _get_stip_identname

#S-TIP オブジェクトに格納する固定値
STIP_IDENTITY_CLASS = 'organization'
STIP_NAME = 'Fujitsu System Integration Laboratories.'

#S-TIP SNS 用カスタムオブジェクト
@CustomObject('x-stip-sns',[
    ('post_type', StringProperty(required=True)),
    ('name', StringProperty(required=True)),
    ('description', StringProperty(required=True)),
    ('created_by_ref', ReferenceProperty(type='identity')),
    ('lang', StringProperty()),
    ('granular_markings', ListProperty(GranularMarking)),
])
class StipSns(object):
    pass

#stix2_titles と stix2_contents から language_content の contents に格納する辞書を作成する
def _get_language_contents(stix2_titles,stix2_contents):
    contents = {}
    for stix2_title in stix2_titles:
        language = stix2_title[u'language']
        if contents.has_key(language) == True:
                d = contents[language]
                d[u'name'] = stix2_title[u'title']
                contents[language] = d
        else:
                d = {}
                d[u'name'] = stix2_title[u'title']
                contents[language] = d

    for stix2_content in stix2_contents:
        language = stix2_content[u'language']
        if contents.has_key(language) == True:
            d = contents[language]
            d[u'description'] = stix2_content[u'content']
            contents[language] = d
        else:
            d = {}
            d[u'description'] = stix2_content[u'content']
            contents[language] = d
    return contents

#json データから Vulunerability 作成する
def _get_vulnerability_object(ttp,stip_identity):
    cve = ttp[u'value']
    title = ttp[u'title']
    name = u'%s (%s)' % (title,cve)

    external_references = []
    external_reference = {}
    external_reference[u'source_name'] = u'cve'
    external_reference[u'external_id'] = cve
    external_references.append(external_reference)

    vulnerability = Vulnerability(
        name=name,
        created_by_ref=stip_identity,
        external_references=external_references
    )
    return vulnerability

#json データから ThreatActor 作成する
def _get_threat_actor_object(ta,stip_identity):
    name = ta[u'value']
    description = ta[u'title']
    threat_actor_types = u'crime-syndicate'

    threat_actor = ThreatActor(
        name=name,
        description=description,
        created_by_ref=stip_identity,
        threat_actor_types=threat_actor_types)
    return threat_actor

#json データから Indicator 作成する
def _get_indicator_object(indicator,stip_identity):
    name = indicator[u'title']
    description = indicator[u'title']
    type_ = indicator[u'type']
    value = indicator[u'value']

    indicator_types = u'compromised'

    if type_ == fec.JSON_OBJECT_TYPE_IPV4:
        pattern = u'[ipv4-addr:value = \'%s\']' % (value)
    elif type_ == fec.JSON_OBJECT_TYPE_URI:
        pattern = u'[url:value = \'%s\']' % (value)
    elif type_ == fec.JSON_OBJECT_TYPE_MD5:
        pattern = u'[file:hashes.\'MD5\' = \'%s\']' % (value)
    elif type_ == fec.JSON_OBJECT_TYPE_SHA1:
        pattern = u'[file:hashes.\'SHA1\' = \'%s\']' % (value)
    elif type_ == fec.JSON_OBJECT_TYPE_SHA256:
        pattern = u'[file:hashes.\'SHA256\' = \'%s\']' % (value)
    elif type_ == fec.JSON_OBJECT_TYPE_SHA512:
        pattern = u'[file:hashes.\'SHA512\' = \'%s\']' % (value)
    elif type_ == fec.JSON_OBJECT_TYPE_FILE_NAME:
        pattern = u'[file:name = \'%s\']' % (value)
    else:
        return None

    indicator_o = Indicator(
        name=name,
        description=description,
        indicator_types=indicator_types,
        pattern=pattern,
        created_by_ref=stip_identity)
    return indicator_o

#GlanularMarkings 作成する 
def _make_granular_markings(stix2_title,stix2_content,lang):
    granular_markings = []
    if stix2_title[u'language'] != lang:
        granular_marking = GranularMarking(lang=stix2_title[u'language'],selectors=[u'name'])
        granular_markings.append(granular_marking)
    if stix2_content[u'language'] != lang:
        granular_marking = GranularMarking(lang=stix2_content[u'language'],selectors=[u'description'])
        granular_markings.append(granular_marking)
    if len(granular_markings) == 0:
        return None
    return granular_markings

#stix2 の Bundle 作成する
def get_stix2_bundle(
    indicators,
    ttps,
    tas,
    title,
    content,
    stix2_titles=[],
    stix2_contents=[],
    stip_user=None):

    #S-TIP Identity 作成する
    stip_identity = _get_stip_identname(stip_user)
    
    #Report と StipSns に格納する granular_markings を取得する
    granular_markings = _make_granular_markings(stix2_titles[0],stix2_contents[0],stip_user.language) 
    
    #共通 lang
    common_lang = stip_user.language
    
    #StipSns Object (Custom Object)
    stip_sns = StipSns(
        lang=common_lang,
        granular_markings=granular_markings,
        post_type='post',
        created_by_ref=stip_identity,
        name=title,
        description=content)

    #ReportObject
    report = Report(
        lang=common_lang,
        granular_markings=granular_markings,
        name=title,
        description=content,
        created_by_ref=stip_identity,
        published=datetime.datetime.now(tz=pytz.utc),
        report_types=['threat-report'],
        object_refs=[stip_sns])
    
    #language-content 作成
    if granular_markings is None:
        #S-TIP オブジェクト用の language-content 作成
        language_contents = _get_language_contents(stix2_titles,stix2_contents)
        if language_contents.has_key(common_lang) == True:
            del language_contents[common_lang]
        
        s_tip_lc = LanguageContent(
            created_by_ref=stip_identity,
            object_ref=stip_sns,
            object_modified=stip_sns.created,
            contents = language_contents
        )

        #Report オブジェクト用の language-content 作成
        report_lc = LanguageContent(
            object_ref=report,
            created_by_ref=stip_identity,
            object_modified=report.created,
            contents = language_contents
        )
        #bundle 作成
        bundle = Bundle(stip_identity,report,stip_sns,s_tip_lc,report_lc)
    else:
        #granular_markings が存在するときは language-content は作成しない
        #bundle 作成
        bundle = Bundle(stip_identity,report,stip_sns)


    #objects に Vulnerability 追加
    for ttp in ttps:
        bundle.objects.append(_get_vulnerability_object(ttp,stip_identity))

    #objects に ThreatActor 追加
    for ta in tas:
        bundle.objects.append(_get_threat_actor_object(ta,stip_identity))

    #objects に Indicator 追加
    for indicator in indicators:
        indicator_o = _get_indicator_object(indicator,stip_identity)
        if indicator_o is not None:
            bundle.objects.append(indicator_o)
    return bundle

