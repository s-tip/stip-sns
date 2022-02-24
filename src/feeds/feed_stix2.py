import datetime
import base64
import pytz
import feeds.extractor.common as fec
import stip.common.const as const
import stix2.v21.sdo as SDO
from stix2.v21.bundle import Bundle
from stix2.properties import IDProperty
from stix2.v21.common import LanguageContent, GranularMarking, TLP_WHITE, TLP_GREEN, TLP_AMBER, TLP_RED
from stip.common.x_stip_sns import StipSns
from ctirs.models import SNSConfig

# S-TIP オブジェクトに格納する固定値
STIP_IDENTITY_CLASS = 'organization'
STIP_NAME = 'Fujitsu System Integration Laboratories.'
STIP_SNS_IDENTITY_VALUE = 's-tip-sns'


# stix2_titles と stix2_contents から language_content の contents に格納する辞書を作成する
def _get_language_contents(stix2_titles, stix2_contents):
    contents = {}
    for stix2_title in stix2_titles:
        language = stix2_title['language']
        if language in contents:
            d = contents[language]
            d['name'] = stix2_title['title']
            contents[language] = d
        else:
            d = {}
            d['name'] = stix2_title['title']
            contents[language] = d

    for stix2_content in stix2_contents:
        language = stix2_content['language']
        if language in contents:
            d = contents[language]
            d['description'] = stix2_content['content']
            contents[language] = d
        else:
            d = {}
            d['description'] = stix2_content['content']
            contents[language] = d
    return contents


# json データから Vulunerability 作成する
def _get_vulnerability_object(ttp, stip_identity, tlp_marking_object):
    cve = ttp['value']
    confidence = ttp['confidence']
    mitre_url = fec.CommonExtractor.get_mitre_url_from_json(cve)

    external_references = []
    external_reference = {}
    external_reference['source_name'] = 'cve'
    external_reference['external_id'] = cve
    external_reference['url'] = mitre_url
    external_references.append(external_reference)

    description = fec.CommonExtractor.get_ttp_common_description(ttp)
    vulnerability = SDO.Vulnerability(
        name=cve,
        description=description,
        created_by_ref=stip_identity,
        confidence=confidence,
        object_marking_refs=[tlp_marking_object],
        external_references=external_references
    )
    return vulnerability


def _get_other_object_boolean_property(prop):
    if prop:
        if prop.lower() == 'true':
            return True
    return False


def _get_other_object_property(prop):
    return prop if len(prop) else None


def _get_custom_attack_pattern_object(j, stip_identity, tlp_marking_object):
    return SDO.AttackPattern(
        name=_get_other_object_property(j['name']),
        description=_get_other_object_property(j['description']),
        created_by_ref=stip_identity,
        confidence=j['confidence'],
        object_marking_refs=[tlp_marking_object],
        aliases=_get_other_object_property(j['aliases']),
    )


def _get_custom_campaign_object(j, stip_identity, tlp_marking_object):
    return SDO.Campaign(
        name=_get_other_object_property(j['name']),
        description=_get_other_object_property(j['description']),
        created_by_ref=stip_identity,
        confidence=j['confidence'],
        object_marking_refs=[tlp_marking_object],
        aliases=_get_other_object_property(j['aliases']),
        objective=_get_other_object_property(j['objective']),
        first_seen=_get_other_object_property(j['first_seen']),
        last_seen=_get_other_object_property(j['last_seen']),
    )


def _get_custom_course_of_action_object(j, stip_identity, tlp_marking_object):
    return SDO.CourseOfAction(
        name=_get_other_object_property(j['name']),
        description=_get_other_object_property(j['description']),
        created_by_ref=stip_identity,
        confidence=j['confidence'],
        object_marking_refs=[tlp_marking_object],
    )


def _get_custom_identity_object(j, stip_identity, tlp_marking_object):
    return SDO.Identity(
        name=_get_other_object_property(j['name']),
        description=_get_other_object_property(j['description']),
        created_by_ref=stip_identity,
        confidence=j['confidence'],
        object_marking_refs=[tlp_marking_object],
        roles=_get_other_object_property(j['roles']),
        identity_class=_get_other_object_property(j['identity_class']),
        sectors=_get_other_object_property(j['sectors']),
        contact_information=_get_other_object_property(j['contact_information']),
    )


def _get_custom_indicator_object(j, stip_identity, tlp_marking_object):
    return SDO.Indicator(
        name=_get_other_object_property(j['name']),
        description=_get_other_object_property(j['description']),
        created_by_ref=stip_identity,
        confidence=j['confidence'],
        object_marking_refs=[tlp_marking_object],
        indicator_types=_get_other_object_property(j['indicator_types']),
        pattern=_get_other_object_property(j['pattern']),
        pattern_type=_get_other_object_property(j['pattern_type']),
        pattern_version=_get_other_object_property(j['pattern_version']),
        valid_from=_get_other_object_property(j['valid_from']),
        valid_until=_get_other_object_property(j['valid_until']),
    )


def _get_custom_infrastructure_object(j, stip_identity, tlp_marking_object):
    return SDO.Infrastructure(
        name=_get_other_object_property(j['name']),
        description=_get_other_object_property(j['description']),
        created_by_ref=stip_identity,
        confidence=j['confidence'],
        object_marking_refs=[tlp_marking_object],
        infrastructure_types=_get_other_object_property(j['infrastructure_types']),
        aliases=_get_other_object_property(j['aliases']),
        first_seen=_get_other_object_property(j['first_seen']),
        last_seen=_get_other_object_property(j['last_seen']),
    )


def _get_custom_intrusion_set_object(j, stip_identity, tlp_marking_object):
    return SDO.IntrusionSet(
        name=_get_other_object_property(j['name']),
        description=_get_other_object_property(j['description']),
        created_by_ref=stip_identity,
        confidence=j['confidence'],
        object_marking_refs=[tlp_marking_object],
        aliases=_get_other_object_property(j['aliases']),
        first_seen=_get_other_object_property(j['first_seen']),
        last_seen=_get_other_object_property(j['last_seen']),
        goals=_get_other_object_property(j['goals']),
        resource_level=_get_other_object_property(j['resource_level']),
        primary_motivation=_get_other_object_property(j['primary_motivation']),
        secondary_motivations=_get_other_object_property(j['secondary_motivations']),
    )


def _get_custom_location_object(j, stip_identity, tlp_marking_object):
    return SDO.Location(
        name=_get_other_object_property(j['name']),
        description=_get_other_object_property(j['description']),
        created_by_ref=stip_identity,
        confidence=j['confidence'],
        object_marking_refs=[tlp_marking_object],
        latitude=_get_other_object_property(j['latitude']),
        longitude=_get_other_object_property(j['longitude']),
        precision=_get_other_object_property(j['precision']),
        region=_get_other_object_property(j['region']),
        country=_get_other_object_property(j['country']),
        administrative_area=_get_other_object_property(j['administrative_area']),
        city=_get_other_object_property(j['city']),
        street_address=_get_other_object_property(j['street_address']),
    )


def _get_custom_malware_object(j, stip_identity, tlp_marking_object):
    return SDO.Malware(
        name=_get_other_object_property(j['name']),
        description=_get_other_object_property(j['description']),
        created_by_ref=stip_identity,
        confidence=j['confidence'],
        object_marking_refs=[tlp_marking_object],
        malware_types=_get_other_object_property(j['malware_types']),
        is_family=_get_other_object_boolean_property(j['is_family']),
        aliases=_get_other_object_property(j['aliases']),
        first_seen=_get_other_object_property(j['first_seen']),
        last_seen=_get_other_object_property(j['last_seen']),
        operating_system_refs=_get_other_object_property(j['operating_system_refs']),
        architecture_execution_envs=_get_other_object_property(j['architecture_execution_envs']),
        implementation_languages=_get_other_object_property(j['implementation_languages']),
        capabilities=_get_other_object_property(j['capabilities']),
        sample_refs=_get_other_object_property(j['sample_refs']),
    )


def _get_custom_malware_analysis_object(j, stip_identity, tlp_marking_object):
    return SDO.MalwareAnalysis(
        created_by_ref=stip_identity,
        confidence=j['confidence'],
        object_marking_refs=[tlp_marking_object],
        product=_get_other_object_property(j['product']),
        version=_get_other_object_property(j['version']),
        host_vm_ref=_get_other_object_property(j['host_vm_ref']),
        operating_system_ref=_get_other_object_property(j['operating_system_ref']),
        installed_software_refs=_get_other_object_property(j['installed_software_refs']),
        configuration_version=_get_other_object_property(j['configuration_version']),
        modules=_get_other_object_property(j['modules']),
        analysis_engine_version=_get_other_object_property(j['analysis_engine_version']),
        analysis_definition_version=_get_other_object_property(j['analysis_definition_version']),
        submitted=_get_other_object_property(j['submitted']),
        analysis_started=_get_other_object_property(j['analysis_started']),
        analysis_ended=_get_other_object_property(j['analysis_ended']),
        result_name=_get_other_object_property(j['result_name']),
        result=_get_other_object_property(j['result']),
        analysis_sco_refs=_get_other_object_property(j['analysis_sco_refs']),
        sample_ref=_get_other_object_property(j['sample_ref']),
    )


def _get_custom_note_object(j, stip_identity, tlp_marking_object):
    return SDO.Note(
        created_by_ref=stip_identity,
        confidence=j['confidence'],
        object_marking_refs=[tlp_marking_object],
        abstract=_get_other_object_property(j['abstract']),
        content=_get_other_object_property(j['content']),
        authors=_get_other_object_property(j['authors']),
        object_refs=_get_other_object_property(j['object_refs']),
    )


def _get_custom_opinion_object(j, stip_identity, tlp_marking_object):
    return SDO.Opinion(
        created_by_ref=stip_identity,
        confidence=j['confidence'],
        object_marking_refs=[tlp_marking_object],
        explanation=_get_other_object_property(j['explanation']),
        authors=_get_other_object_property(j['authors']),
        opinion=_get_other_object_property(j['opinion']),
        object_refs=_get_other_object_property(j['object_refs']),
    )


def _get_custom_report_object(j, stip_identity, tlp_marking_object):
    return SDO.Report(
        created_by_ref=stip_identity,
        confidence=j['confidence'],
        object_marking_refs=[tlp_marking_object],
        name=_get_other_object_property(j['name']),
        description=_get_other_object_property(j['description']),
        report_types=_get_other_object_property(j['report_types']),
        published=_get_other_object_property(j['published']),
        object_refs=_get_other_object_property(j['object_refs']),
    )


def _get_custom_threat_actor_object(j, stip_identity, tlp_marking_object):
    return SDO.ThreatActor(
        created_by_ref=stip_identity,
        confidence=j['confidence'],
        object_marking_refs=[tlp_marking_object],
        name=_get_other_object_property(j['name']),
        description=_get_other_object_property(j['description']),
        threat_actor_types=_get_other_object_property(j['threat_actor_types']),
        aliases=_get_other_object_property(j['aliases']),
        first_seen=_get_other_object_property(j['first_seen']),
        last_seen=_get_other_object_property(j['last_seen']),
        roles=_get_other_object_property(j['roles']),
        goals=_get_other_object_property(j['goals']),
        sophistication=_get_other_object_property(j['sophistication']),
        resource_level=_get_other_object_property(j['resource_level']),
        primary_motivation=_get_other_object_property(j['primary_motivation']),
        secondary_motivations=_get_other_object_property(j['secondary_motivations']),
        personal_motivations=_get_other_object_property(j['personal_motivations']),
    )


def _get_custom_tool_object(j, stip_identity, tlp_marking_object):
    return SDO.Tool(
        created_by_ref=stip_identity,
        confidence=j['confidence'],
        object_marking_refs=[tlp_marking_object],
        name=_get_other_object_property(j['name']),
        description=_get_other_object_property(j['description']),
        tool_types=_get_other_object_property(j['tool_types']),
        aliases=_get_other_object_property(j['aliases']),
        tool_version=_get_other_object_property(j['tool_version']),
    )


def _get_custom_vulnerability_object(j, stip_identity, tlp_marking_object):
    return SDO.Vulnerability(
        created_by_ref=stip_identity,
        confidence=j['confidence'],
        object_marking_refs=[tlp_marking_object],
        name=_get_other_object_property(j['name']),
        description=_get_other_object_property(j['description']),
    )


OO_FUNCS = {
    'attack-pattern': _get_custom_attack_pattern_object,
    'campaign': _get_custom_campaign_object,
    'course-of-action': _get_custom_course_of_action_object,
    'identity': _get_custom_identity_object,
    'indicator': _get_custom_indicator_object,
    'infrastructure': _get_custom_infrastructure_object,
    'intrusion-set': _get_custom_intrusion_set_object,
    'location': _get_custom_location_object,
    'malware': _get_custom_malware_object,
    'malware-analysis': _get_custom_malware_analysis_object,
    'note': _get_custom_note_object,
    'opinion': _get_custom_opinion_object,
    'report': _get_custom_report_object,
    'threat-actor': _get_custom_threat_actor_object,
    'tool': _get_custom_tool_object,
    'vulnerability': _get_custom_vulnerability_object,
}


# json データから ThreatActor 作成する
def _get_threat_actor_object(ta, stip_identity, tlp_marking_object):
    name = ta['value']
    confidence = ta['confidence']
    description = ta['title']
    try:
        threat_actor_types = [ta['type']]
    except KeyError:
        threat_actor_types = ['unknown']

    if SNSConfig.get_cs_custid() and SNSConfig.get_cs_custkey():
        description, aliases = fec.CommonExtractor._get_ta_description_from_crowd_strike(name)
        if not description:
            description, aliases = fec.CommonExtractor._get_ta_description_from_attck(name)
    else:
        description, aliases = fec.CommonExtractor._get_ta_description_from_attck(name)

    threat_actor = SDO.ThreatActor(
        name=name,
        description=description,
        created_by_ref=stip_identity,
        confidence=confidence,
        object_marking_refs=[tlp_marking_object],
        aliases=aliases,
        threat_actor_types=threat_actor_types)
    return threat_actor


# json データから Indicator 作成する
def _get_indicator_object(indicator, stip_identity, tlp_marking_object):
    name = indicator['title']
    description = indicator['title']
    type_ = indicator['type']
    value = indicator['value']
    confidence = indicator['confidence']
    try:
        indicator_types = [indicator['stix2_indicator_types']]
    except KeyError:
        indicator_types = ['malicious-activity']

    if type_ == fec.JSON_OBJECT_TYPE_IPV4:
        pattern = '[ipv4-addr:value = \'%s\']' % (value)
    elif type_ == fec.JSON_OBJECT_TYPE_URI:
        pattern = '[url:value = \'%s\']' % (value)
    elif type_ == fec.JSON_OBJECT_TYPE_MD5:
        pattern = '[file:hashes.\'MD5\' = \'%s\']' % (value)
    elif type_ == fec.JSON_OBJECT_TYPE_SHA1:
        pattern = '[file:hashes.\'SHA-1\' = \'%s\']' % (value)
    elif type_ == fec.JSON_OBJECT_TYPE_SHA256:
        pattern = '[file:hashes.\'SHA-256\' = \'%s\']' % (value)
    elif type_ == fec.JSON_OBJECT_TYPE_SHA512:
        pattern = '[file:hashes.\'SHA-512\' = \'%s\']' % (value)
    elif type_ == fec.JSON_OBJECT_TYPE_FILE_NAME:
        pattern = '[file:name = \'%s\']' % (value)
    elif type_ == fec.JSON_OBJECT_TYPE_DOMAIN:
        pattern = '[domain-name:value = \'%s\']' % (value)
    elif type_ == fec.JSON_OBJECT_TYPE_EMAIL_ADDRESS:
        pattern = '[email-addr:value = \'%s\']' % (value)
    else:
        return None

    indicator_o = SDO.Indicator(
        name=name,
        description=description,
        created_by_ref=stip_identity,
        confidence=confidence,
        object_marking_refs=[tlp_marking_object],
        indicator_types=indicator_types,
        pattern=pattern,
        pattern_type='stix',
        valid_from=datetime.datetime.now(tz=pytz.utc))
    return indicator_o


# GlanularMarkings 作成する
def _make_granular_markings(stix2_title, stix2_content, lang):
    granular_markings = []
    if stix2_title['language'] != lang:
        granular_marking = GranularMarking(lang=stix2_title['language'], selectors=['name'])
        granular_markings.append(granular_marking)
    if stix2_content['language'] != lang:
        granular_marking = GranularMarking(lang=stix2_content['language'], selectors=['description'])
        granular_markings.append(granular_marking)
    if len(granular_markings) == 0:
        return None
    return granular_markings


# stip_user から x-stip-sns-author property を作成する
def _get_x_stip_sns_author(stip_user):
    d = {}
    try:
        d[const.STIP_STIX2_SNS_AUTHOR_AFFILIATION_KEY] = stip_user.affiliation
    except AttributeError:
        d[const.STIP_STIX2_SNS_AUTHOR_AFFILIATION_KEY] = ''
    if not d[const.STIP_STIX2_SNS_AUTHOR_AFFILIATION_KEY]:
        d[const.STIP_STIX2_SNS_AUTHOR_AFFILIATION_KEY] = ''

    try:
        d[const.STIP_STIX2_SNS_AUTHOR_CI_KEY] = stip_user.ci
    except AttributeError:
        d[const.STIP_STIX2_SNS_AUTHOR_CI_KEY] = ''
    if not d[const.STIP_STIX2_SNS_AUTHOR_CI_KEY]:
        d[const.STIP_STIX2_SNS_AUTHOR_CI_KEY] = ''

    try:
        d[const.STIP_STIX2_SNS_AUTHOR_REGION_CODE_KEY] = stip_user.region.code
    except AttributeError:
        d[const.STIP_STIX2_SNS_AUTHOR_REGION_CODE_KEY] = ''

    try:
        d[const.STIP_STIX2_SNS_AUTHOR_COUNTRY_CODE_KEY] = stip_user.region.country_code
    except AttributeError:
        d[const.STIP_STIX2_SNS_AUTHOR_COUNTRY_CODE_KEY] = ''

    d[const.STIP_STIX2_SNS_AUTHOR_SCREEN_NAME_KEY] = stip_user.screen_name
    d[const.STIP_STIX2_SNS_AUTHOR_USER_NAME_KEY] = stip_user.username
    return d


# stip_user から x-stip-sns-post property を作成する
def _get_x_stip_sns_post(
    title, description,
    tlp, sharing_range, referred_url
):
    d = {}
    d[const.STIP_STIX2_SNS_POST_TITLE_KEY] = title
    d[const.STIP_STIX2_SNS_POST_DECRIPTION_KEY] = description
    dt = datetime.datetime.now(tz=pytz.utc)
    d[const.STIP_STIX2_SNS_POST_TIMESTAMP_KEY] = format_stix2_datetime(dt)
    d[const.STIP_STIX2_SNS_POST_TLP_KEY] = tlp
    d[const.STIP_STIX2_SNS_POST_SHARING_RANGE_KEY] = sharing_range
    if referred_url:
        d[const.STIP_STIX2_SNS_POST_REFERRED_URL_KEY] = referred_url
    else:
        d[const.STIP_STIX2_SNS_POST_REFERRED_URL_KEY] = ''
    return d


def format_stix2_datetime(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + 'Z'


# x-stip-sns-identity property を作成する
def _get_x_stip_sns_identity():
    return STIP_SNS_IDENTITY_VALUE


# x-stip-sns-tool property を作成する
def _get_x_stip_sns_tool():
    d = {}
    d[const.STIP_STIX2_SNS_TOOL_NAME_KEY] = const.SNS_TOOL_NAME
    d[const.STIP_STIX2_SNS_TOOL_VENDOR_KEY] = const.SNS_TOOL_VENDOR
    return d


# stip_user から identity (Individual) を作成する
def _get_individual_identity(stip_user):
    id = IDProperty('identity').default()
    identity = SDO.Identity(
        id=id,
        name=stip_user.username,
        identity_class='Individual',
        x_stip_sns_account=stip_user.username,
        created_by_ref=id,
        allow_custom=True
    )
    return identity


def _get_organization_identity_sectors(ci):
    ci_table = {
        'Information and Communication Services': ['telecommunications'],
        'Financial Services': ['financial-services'],
        'Aviation Services': ['aerospace'],
        'Railway Services': ['transportation'],
        'Electric Power Supply Services': ['utilities'],
        'Gas Supply Services': ['utilities'],
        'Government and Administrative Services (Including Municipal Government)': ['government-national', 'government-regioanl', 'government-local', 'government-public-services'],
        'Medical Services': ['healthcare'],
        'Water Services': ['utilities'],
        'Logistics Services': ['transportation'],
        'Chemical Industries': ['technology'],
        'Credit Card Services': ['financial-services'],
        'Petroleum Industries': ['energy'],
    }

    if ci is None:
        return None
    if ci == 'Other':
        return None
    if ci in ci_table:
        return ci_table[ci]
    else:
        return None


# stip_user から identity (Organization) を作成する
def _get_organization_identity(stip_user, individual_identity):
    if stip_user.affiliation is None or len(stip_user.affiliation) == 0:
        return None
    sectors = _get_organization_identity_sectors(stip_user.ci)
    identity = SDO.Identity(
        name=stip_user.affiliation,
        identity_class='Organization',
        created_by_ref=individual_identity,
        sectors=sectors,
        x_stip_sns_account=stip_user.username,
        allow_custom=True
    )
    return identity


# stix2 の Bundle 作成する (post)
def get_post_stix2_bundle(
    confirm_data,
    title,
    content,
    tlp,
    referred_url,
    feed_confidece,
    sharing_range,
    stix2_titles=[],
    stix2_contents=[],
    x_stip_sns_attachments=None,
    stip_user=None,
    tags=[]
):

    from feeds.views import KEY_INDICATORS, KEY_TTPS, KEY_TAS, KEY_OTHER
    indicators = confirm_data[KEY_INDICATORS]
    ttps = confirm_data[KEY_TTPS]
    tas = confirm_data[KEY_TAS]
    other_objects = confirm_data[KEY_OTHER]

    # S-TIP Identity 作成する
    individual_identity = _get_individual_identity(stip_user)
    organization_identity = _get_organization_identity(stip_user, individual_identity)

    # x_stip_sns_author
    x_stip_sns_author = _get_x_stip_sns_author(stip_user)

    # x_stip_sns_post
    x_stip_sns_post = _get_x_stip_sns_post(
        title,
        content,
        tlp,
        sharing_range,
        referred_url)

    # x_stip_sns_bundle_id
    x_stip_sns_bundle_id = None
    # x_stip_sns_tags
    x_stip_sns_tags = None
    # x_stip_sns_indicators
    x_stip_sns_indicators = None
    # x_stip_sns_identity
    x_stip_sns_identity = _get_x_stip_sns_identity()
    # x_stip_sns_tool
    x_stip_sns_tool = _get_x_stip_sns_tool()

    # Report Object 用 object_refs
    report_object_refs = []

    # TLP marking_object 取得
    tlp_marking_object = _get_tlp_markings(tlp)

    # bundle 作成
    bundle = Bundle(individual_identity, tlp_marking_object, allow_custom=True)
    if organization_identity:
        bundle.objects.append(organization_identity)

    # objects に Vulnerability 追加
    for ttp in ttps:
        vulnerablity_object = _get_vulnerability_object(ttp, individual_identity, tlp_marking_object)
        bundle.objects.append(vulnerablity_object)
        report_object_refs.append(vulnerablity_object)

    # objects に ThreatActor 追加
    for ta in tas:
        ta_object = _get_threat_actor_object(ta, individual_identity, tlp_marking_object)
        bundle.objects.append(ta_object)
        report_object_refs.append(ta_object)

    # objects に Indicator 追加
    for indicator in indicators:
        indicator_o = _get_indicator_object(indicator, individual_identity, tlp_marking_object)
        if indicator_o is not None:
            bundle.objects.append(indicator_o)
            report_object_refs.append(indicator_o)

    for other_object in other_objects:
        oo_type = other_object['type']
        if oo_type in OO_FUNCS:
            f = OO_FUNCS[oo_type]
            o_ = f(other_object, individual_identity, tlp_marking_object)
            bundle.objects.append(o_)
            report_object_refs.append(o_)

    # 共通 lang
    common_lang = stip_user.language
    # Report と StipSns に格納する granular_markings を取得する
    if len(stix2_titles) > 0 and len(stix2_contents) > 0:
        granular_markings = _make_granular_markings(stix2_titles[0], stix2_contents[0], stip_user.language)
    else:
        granular_markings = None

    # StipSns Object (Custom Object)
    stip_sns = StipSns(
        lang=common_lang,
        granular_markings=granular_markings,
        object_marking_refs=[tlp_marking_object],
        created_by_ref=individual_identity,
        name=title,
        description=content,
        confidence=feed_confidece,
        x_stip_sns_type='post',
        x_stip_sns_author=x_stip_sns_author,
        x_stip_sns_post=x_stip_sns_post,
        x_stip_sns_attachments=x_stip_sns_attachments,
        x_stip_sns_bundle_id=x_stip_sns_bundle_id,
        x_stip_sns_tags=x_stip_sns_tags,
        x_stip_sns_indicators=x_stip_sns_indicators,
        x_stip_sns_identity=x_stip_sns_identity,
        x_stip_sns_tool=x_stip_sns_tool)
    report_object_refs.append(stip_sns)
    bundle.objects.append(stip_sns)

    # ReportObject
    published = format_stix2_datetime(datetime.datetime.now(tz=pytz.utc))
    report = SDO.Report(
        lang=common_lang,
        granular_markings=granular_markings,
        object_marking_refs=[tlp_marking_object],
        name=title,
        description=content,
        created_by_ref=individual_identity,
        published=published,
        report_types=['threat-report'],
        object_refs=report_object_refs,
        labels=tags,
        confidence=feed_confidece,
        allow_custom=True
    )
    bundle.objects.append(report)

    # language-content 作成
    if granular_markings:
        # S-TIP オブジェクト用の language-content 作成
        language_contents = _get_language_contents(stix2_titles, stix2_contents)
        if common_lang in language_contents:
            del language_contents[common_lang]

        if language_contents != {}:
            s_tip_lc = LanguageContent(
                created_by_ref=individual_identity,
                object_ref=stip_sns,
                object_modified=stip_sns.created,
                contents=language_contents,
                confidence=feed_confidece,
                allow_custom=True
            )
            bundle.objects.append(s_tip_lc)

            # Report オブジェクト用の language-content 作成
            report_lc = LanguageContent(
                object_ref=report,
                created_by_ref=individual_identity,
                object_modified=report.created,
                contents=language_contents,
                confidence=feed_confidece,
                allow_custom=True
            )
            bundle.objects.append(report_lc)
    return bundle


# stix2 の Bundle 作成する (attach)
def get_attach_stix2_bundle(
    tlp,
    referred_url,
    feed_confidence,
    sharing_range,
    request_file,
    stip_user=None
):

    # S-TIP Identity 作成する
    individual_identity = _get_individual_identity(stip_user)
    organization_identity = _get_organization_identity(stip_user, individual_identity)
    # x_stip_sns_author
    x_stip_sns_author = _get_x_stip_sns_author(stip_user)

    # x_stip_sns_identity
    x_stip_sns_identity = _get_x_stip_sns_identity()
    # x_stip_sns_tool
    x_stip_sns_tool = _get_x_stip_sns_tool()
    # TLP marking_object 取得
    tlp_marking_object = _get_tlp_markings(tlp)
    # 共通 lang
    common_lang = stip_user.language

    title = request_file.name
    content = 'File "%s" encoded in BASE64.' % (request_file.name)
    x_stip_sns_attachment = _get_x_stip_sns_attachment(request_file)

    # x_stip_sns_post
    x_stip_sns_post = _get_x_stip_sns_post(
        title,
        content,
        tlp,
        sharing_range,
        referred_url)

    stip_sns = StipSns(
        lang=common_lang,
        object_marking_refs=[tlp_marking_object],
        created_by_ref=individual_identity,
        name=title,
        description=content,
        confidence=feed_confidence,
        x_stip_sns_type=const.STIP_STIX2_SNS_POST_TYPE_ATTACHMENT,
        x_stip_sns_author=x_stip_sns_author,
        x_stip_sns_post=x_stip_sns_post,
        x_stip_sns_attachment=x_stip_sns_attachment,
        x_stip_sns_identity=x_stip_sns_identity,
        x_stip_sns_tool=x_stip_sns_tool)

    # bundle 作成
    bundle = Bundle(
        individual_identity,
        tlp_marking_object,
        stip_sns,
        allow_custom=True)
    if organization_identity:
        bundle.objects.append(organization_identity)
    return bundle, stip_sns.id


# feed_file から x-stip-sns-attachment property を作成する
def _get_x_stip_sns_attachment(request_file):
    d = {}
    d[const.STIP_STIX2_SNS_ATTACHMENT_FILENAME_KEY] = request_file.name
    content = base64.b64encode(request_file.read())
    d[const.STIP_STIX2_SNS_ATTACHMENT_CONTENT_KEY] = content.decode('utf-8')
    return d


# TLP 文字列に合わせた marking-definition を返却する
def _get_tlp_markings(tlp):
    tlp_table = {
        'WHITE': TLP_WHITE,
        'GREEN': TLP_GREEN,
        'AMBER': TLP_AMBER,
        'RED': TLP_RED
    }
    try:
        return tlp_table[tlp.upper()]
    except KeyError:
        return None


# stix2 の Bundle 作成する (comment)
def get_comment_stix2_bundle(
    x_stip_sns_bundle_id,
    report_id,
    x_stip_sns_bundle_version,
    description,
    tlp,
    stip_user=None
):

    # S-TIP Identity 作成する
    individual_identity = _get_individual_identity(stip_user)
    organization_identity = _get_organization_identity(stip_user, individual_identity)
    # x_stip_sns_author
    x_stip_sns_author = _get_x_stip_sns_author(stip_user)
    # x_stip_sns_identity
    x_stip_sns_identity = _get_x_stip_sns_identity()
    # x_stip_sns_tool
    x_stip_sns_tool = _get_x_stip_sns_tool()
    # TLP marking_object 取得
    tlp_marking_object = _get_tlp_markings(tlp)
    # 共通 lang
    common_lang = stip_user.language

    title = 'Comment to %s' % (x_stip_sns_bundle_id)
    stip_sns = StipSns(
        lang=common_lang,
        object_marking_refs=[tlp_marking_object],
        created_by_ref=individual_identity,
        name=title,
        description=description,
        confidence=stip_user.confidence,
        x_stip_sns_type=const.STIP_STIX2_SNS_POST_TYPE_COMMENT,
        x_stip_sns_author=x_stip_sns_author,
        x_stip_sns_bundle_id=x_stip_sns_bundle_id,
        x_stip_sns_bundle_version=x_stip_sns_bundle_version,
        x_stip_sns_identity=x_stip_sns_identity,
        x_stip_sns_tool=x_stip_sns_tool)

    note = SDO.Note(
        created_by_ref=individual_identity,
        content=description,
        authors=[stip_user.screen_name],
        object_refs=[report_id]
    )

    # bundle 作成
    bundle = Bundle(
        individual_identity,
        tlp_marking_object,
        stip_sns,
        allow_custom=True)
    if organization_identity:
        bundle.objects.append(organization_identity)
    bundle.objects.append(note)
    return bundle


# stix2 の Bundle 作成する (like)
def get_like_stix2_bundle(
    x_stip_sns_bundle_id,
    report_id,
    x_stip_sns_bundle_version,
    like,
    tlp,
    stip_user=None
):

    # S-TIP Identity 作成する
    individual_identity = _get_individual_identity(stip_user)
    organization_identity = _get_organization_identity(stip_user, individual_identity)
    # x_stip_sns_author
    x_stip_sns_author = _get_x_stip_sns_author(stip_user)
    # x_stip_sns_identity
    x_stip_sns_identity = _get_x_stip_sns_identity()
    # x_stip_sns_tool
    x_stip_sns_tool = _get_x_stip_sns_tool()
    # TLP marking_object 取得
    tlp_marking_object = _get_tlp_markings(tlp)
    # 共通 lang
    common_lang = stip_user.language

    if like:
        # like -> unlike
        x_stip_sns_type = const.STIP_STIX2_SNS_POST_TYPE_UNLIKE
        title = 'Unlike to %s' % (x_stip_sns_bundle_id)
        description = 'Unlike to %s' % (x_stip_sns_bundle_id)
        like = False
    else:
        # unlike -> like
        x_stip_sns_type = const.STIP_STIX2_SNS_POST_TYPE_LIKE
        title = 'Like to %s' % (x_stip_sns_bundle_id)
        description = 'Like to %s' % (x_stip_sns_bundle_id)
        like = True

    stip_sns = StipSns(
        lang=common_lang,
        object_marking_refs=[tlp_marking_object],
        created_by_ref=individual_identity,
        name=title,
        description=description,
        confidence=stip_user.confidence,
        x_stip_sns_type=x_stip_sns_type,
        x_stip_sns_author=x_stip_sns_author,
        x_stip_sns_bundle_id=x_stip_sns_bundle_id,
        x_stip_sns_bundle_version=x_stip_sns_bundle_version,
        x_stip_sns_identity=x_stip_sns_identity,
        x_stip_sns_tool=x_stip_sns_tool)

    # bundle 作成
    bundle = Bundle(
        individual_identity,
        tlp_marking_object,
        stip_sns,
        allow_custom=True)
    if organization_identity:
        bundle.objects.append(organization_identity)

    if like:
        opinion = SDO.Opinion(
            created_by_ref=individual_identity,
            opinion='strongly-agree',
            object_refs=[report_id]
        )
        bundle.objects.append(opinion)
    return bundle
