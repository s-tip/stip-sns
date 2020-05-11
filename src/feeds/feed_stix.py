import traceback
import re
import datetime
import base64
import cybox.objects
import pytz
from stix.core import Indicators, ExploitTargets
from stix.core.stix_package import STIXPackage
from stix.core.stix_header import STIXHeader
from cybox.common.properties import HexBinary
from feeds.feed_stix_common import FeedStixCommon
from feeds.extractor.common import CommonExtractor
from feeds.adapter.crowd_strike import query_actors, get_actor_entities
# Statement Attachement の prefix
from stip.common.const import MARKING_STRUCTURE_STIP_ATTACHEMENT_CONTENT_PREFIX, MARKING_STRUCTURE_STIP_ATTACHEMENT_FILENAME_PREFIX
from ctirs.models import SNSConfig


ATT_CK_REG_STR = r'\[\[\S+\|(?P<ta_name>.+?)\]\](?P<description>.+)'
ATT_CK_PATTERN = re.compile(ATT_CK_REG_STR)
# [TITLE](URL)形式を抽出する正規表現
URL_PATTERN = re.compile(r'\[(.+?)\]\(([0-9A-Za-z\-\._~!#\$\&\'\*\+,/:;=?@\[\] ]+)\)')


class FeedStix(FeedStixCommon):
    def __init__(self,
                 feed=None,
                 stix_file_path=None,
                 indicators=None,
                 ttps=None,
                 tas=None
                 ):
        super(FeedStix, self).__init__()
        self.stix_package = None
        self.attachment_files = []
        if feed is not None:
            self.stix_package = self._make_stix_package(feed, indicators, ttps, tas)
        elif stix_file_path is not None:
            self.stix_package = STIXPackage.from_xml(stix_file_path)

    def _get_stix_header(self, feed):
        # header作成
        stix_header = STIXHeader()
        stix_header.title = feed.title
        stix_header.description = feed.post
        stix_header.handling = self._get_stix_header_marking(feed)
        # Inforamtion Source 格納
        stix_header.information_source = self._make_information_source()
        return stix_header

    # feed情報から STIX 作成する
    def _make_stix_package(self, feed, indicators=[], ttps=[], tas=[]):
        user_timezone = pytz.timezone(feed.user.timezone)
        # package ID作成
        package_id = self.generator.create_id(prefix='Package')

        # package作成
        stix_package = STIXPackage(id_=package_id)
        stix_package.timestamp = datetime.datetime.now(tz=user_timezone)

        # header格納
        stix_package.stix_header = self._get_stix_header(feed)

        # indicators 格納
        # web 画面から取得した indicators (json) から stix indicators 作成する
        stix_indicators = Indicators()
        for indicator_json in indicators:
            indicator = CommonExtractor.get_indicator_from_json(indicator_json, user_timezone)
            if indicator is not None:
                stix_indicators.append(indicator)
        stix_package.indicators = stix_indicators

        # ExploitTargets格納
        stix_exploit_targets = ExploitTargets()
        for ttp_json in ttps:
            et = CommonExtractor.get_exploit_target_from_json(ttp_json)
            if et is not None:
                stix_exploit_targets.append(et)
        stix_package.exploit_targets = stix_exploit_targets

        # ThreatActors 格納
        for ta_json in tas:
            value = ta_json['value']
            if SNSConfig.get_cs_custid() is not None and SNSConfig.get_cs_custkey() is not None:
                ta = self.get_ta_from_crowd_strike(value)
                if ta is None:
                    # ATT&CK から ThreatActor 取得する
                    ta = self.get_ta_from_attck(value)
            else:
                ta = self.get_ta_from_attck(value)
            stix_package.add_threat_actor(ta)

        # 添付ファイル用の STIX 作成する
        for file_ in feed.files.all():
            attach_file_stix_package = self._make_stix_package_for_attached_file(file_, feed)
            self.attachment_files.append(attach_file_stix_package)
            # 添付ファイル用の STIX を Related Pacakge に追加する
            stix_package.add_related_package(attach_file_stix_package.id_)
        return stix_package

    # ATT&CK から STIX の Threat Actor を取得する
    def get_ta_from_attck(self, ta_value):
        try:
            # ATT&CK から Attacker Group 情報を取得する
            description, _ = CommonExtractor._get_ta_description_from_attck(ta_value)
            ta = CommonExtractor._get_threat_actor_object(ta_value, description)
            return ta
        except BaseException:
            traceback.print_exc()
            return None

    # CrowdStrike から actor_entity 情報を取得する
    def get_ta_from_crowd_strike(self, ta_value):
        try:
            # Threat_actor で query する
            response = query_actors(ta_value)
            # 該当する Threat Actor 情報が見つからなかった
            if len(response['resources']) == 0:
                return None
            # 先頭の actor_id にて entity 取得する
            actor_id = response['resources'][0]
            attackers_entities = get_actor_entities(actor_id)
            # 該当する Attacker Entity がみつからなかった
            if len(attackers_entities['resources']) == 0:
                return None
            # 先頭のentityだけ利用する
            attacker_entity = attackers_entities['resources'][0]

            # description 作成
            description = '<br/>'
            description += ('%s: %s<br/>' % ('Threat Actor', ta_value))
            if 'known_as' in attacker_entity:
                description += ('%s: %s<br/>' % ('Known As', attacker_entity['known_as']))
            if 'motivations' in attacker_entity:
                ta_motivations = attacker_entity['motivations']
                description += ('%s: ' % ('Motivation'))
                for ta_motivation in ta_motivations:
                    description += ('%s,' % (ta_motivation['value']))
                description = description[:-1]
                description += '<br/>'
            else:
                ta_motivations = []
            if 'short_description' in attacker_entity:
                description += ('%s: %s<br/>' % ('Short Description', attacker_entity['short_description']))
            if 'url' in attacker_entity:
                url = attacker_entity['url']
                # Falcon 不具合対応までの暫定対処
                # url = 'https://falcon.crowdstrike.com/intelligence/actors/ricochet-chollima/'
                if url.startswith('https://falcon.crowdstrike.com/actors/'):
                    url = url.replace('https://falcon.crowdstrike.com/actors/', 'https://falcon.crowdstrike.com/intelligence/actors/')
                description += ('%s: <a href="%s" target="_blank">%s</a><br/>' % ('Report URL', url, url))

            ta = CommonExtractor._get_threat_actor_object(ta_value, description, ta_motivations)
            return ta
        except BaseException:
            # traceback.print_exc()
            return None

    # 添付ファイル用の STIX を作成する
    def _make_stix_package_for_attached_file(self, file_, feed):
        # package ID作成
        package_id = self.generator.create_id(prefix='Package')

        # 添付ファイルの中身を読み込み base64 で encode
        with open(file_.file_path, 'rb') as fp:
            content = base64.b64encode(fp.read())

        # content作成
        marking_specification_content = self._make_marking_specification_statement(MARKING_STRUCTURE_STIP_ATTACHEMENT_CONTENT_PREFIX, content.decode('utf-8'))
        # filename作成
        marking_specification_file_name = self._make_marking_specification_statement(MARKING_STRUCTURE_STIP_ATTACHEMENT_FILENAME_PREFIX, file_.file_name)

        # header 作成
        stix_header = STIXHeader()
        stix_header.handling = self._get_stix_header_marking(feed)
        stix_header.handling.add_marking(marking_specification_content)
        stix_header.handling.add_marking(marking_specification_file_name)
        stix_header.title = file_.file_name
        stix_header.description = 'File "%s" encoded in BASE64.' % (file_.file_name)
        # Information Source 格納
        stix_header.information_source = self._make_information_source()

        # package作成
        stix_package = STIXPackage(id_=package_id)
        stix_package.timestamp = datetime.datetime.now(tz=pytz.timezone(feed.user.timezone))
        stix_package.stix_header = stix_header
        return stix_package

    # リンクを外して、URLを最後に追加する
    def remove_hyperlink(self, text):
        # オブジェクトのタイトルを返す。URLはリストに追加する。
        def matchurls(matchobj):
            urls[matchobj[2]] = ''
            return matchobj[1]
        urls = dict()
        out = re.sub(URL_PATTERN, matchurls, text)
        for url in urls.keys():
            out = out + '\n<br/>' + 'URL: ' + url
        return out

    @classmethod
    def _get_value_from_address_object(cls, prop):
        # IPv4形式である
        try:
            if prop.category == cybox.objects.address_object.Address.CAT_IPV4:
                return prop.address_value.value
            return None
        except BaseException:
            return None

    @classmethod
    # observable に Observable_composition が含まれる場合はすべて展開する
    def flatten_observable_composit(cls, observable):
        ret = []
        if observable.object_ is not None:
            # Observable_composition がないので単一の Observable を追加
            ret.append(observable)
        else:
            # Observable_composition がある場合はすべて展開
            if observable.observable_composition is not None:
                if observable.observable_composition.observables is not None:
                    for observable in observable.observable_composition.observables:
                        # 再帰的呼び出し
                        ret.extend(FeedStix.flatten_observable_composit(observable))
        return ret

    @classmethod
    def get_exploit_targets(cls, stix_package):
        # CSVファイルのラベル
        CVE_TYPE = 'cve'
        lines = []

        if stix_package.exploit_targets is not None:
            for exploit_target in stix_package.exploit_targets:
                if exploit_target.vulnerabilities is not None:
                    for vulnerability in exploit_target.vulnerabilities:
                        if vulnerability.cve_id is not None:
                            lines.append((CVE_TYPE, vulnerability.cve_id, vulnerability.description.value))
        return lines

    @classmethod
    def get_threat_actors(cls, stix_package):
        ACTORS_TYPE = 'threat_actors'
        lines = []
        if stix_package.threat_actors is not None:
            for threat_actor in stix_package.threat_actors:
                lines.append((ACTORS_TYPE, threat_actor.title, threat_actor.description))
        return lines

    @classmethod
    def get_indicators(cls, stix_package, indicator_only=False):
        # CSVファイルのラベル
        IPV4_TYPE = 'ipv4'
        DOMAIN_TYPE = 'domain'
        MD5_TYPE = 'md5'
        SHA1_TYPE = 'sha1'
        SHA256_TYPE = 'sha256'
        SHA512_TYPE = 'sha512'
        URI_TYPE = 'uri'
        FILE_NAME_TYPE = 'file_name'
        EMAIL_ADDRESS_TYPE = 'e-mail'

        # STIXのうちobservables,indicatorsの要素を抜き出す
        observables = []
        # indicators
        if stix_package.indicators is not None:
            for indicator in stix_package.indicators:
                if indicator.observable is not None:
                    observables.extend(FeedStix.flatten_observable_composit(indicator.observable))

        # observables
        if not indicator_only:
            if stix_package.observables is not None:
                for observable in stix_package.observables:
                    observables.extend(FeedStix.flatten_observable_composit(indicator.observable))

        lines = []
        # タイプ別に情報を抽出する
        for observable in observables:
            try:
                prop = observable.object_.properties
                if isinstance(prop, cybox.objects.address_object.Address):
                    v = cls._get_value_from_address_object(prop)
                    if v is not None:
                        lines.append((IPV4_TYPE, v, observable.id_))
                        continue
                if isinstance(prop, cybox.objects.domain_name_object.DomainName):
                    # Domain名である
                    lines.append((DOMAIN_TYPE, prop.value.value, observable.id_))
                    continue
                if isinstance(prop, cybox.objects.uri_object.URI):
                    # uriである
                    lines.append((URI_TYPE, prop.value.value, observable.id_))
                    continue
                if isinstance(prop, cybox.objects.file_object.File):
                    # Fileである
                    if prop.file_name is not None:
                        file_name = '|%s|' % (prop.file_name.value)
                        lines.append((FILE_NAME_TYPE, file_name, observable.id_))
                    if prop.md5 is not None:
                        if isinstance(prop.md5, HexBinary):
                            value = prop.md5.value
                        else:
                            value = prop.md5
                        lines.append((MD5_TYPE, value, observable.id_))
                    if prop.sha1 is not None:
                        if isinstance(prop.sha1, HexBinary):
                            value = prop.sha1.value
                        else:
                            value = prop.sha1
                        lines.append((SHA1_TYPE, value, observable.id_))
                    if prop.sha256 is not None:
                        if isinstance(prop.sha256, HexBinary):
                            value = prop.sha256.value
                        else:
                            value = prop.sha256
                        lines.append((SHA256_TYPE, value, observable.id_))
                    if prop.sha512 is not None:
                        if isinstance(prop.sha512, HexBinary):
                            value = prop.sha512.value
                        else:
                            value = prop.sha512
                        lines.append((SHA512_TYPE, value, observable.id_))
                    continue
                if isinstance(prop, cybox.objects.address_object.Address):
                    # Addressである
                    if (prop.category == cybox.objects.address_object.Address.CAT_EMAIL):
                        lines.append((EMAIL_ADDRESS_TYPE, prop.address_value.value, observable.id_))
                    continue
                try:
                    if isinstance(prop, cybox.objects.network_connection_object.NetworkConnection):
                        # NetworkConnectionである
                        if prop.destination_socket_address is not None:
                            lines.append((IPV4_TYPE, cls._get_value_from_address_object(prop.destination_socket_address.ip_address), observable.id_))
                        if prop.source_socket_address is not None:
                            lines.append((IPV4_TYPE, cls._get_value_from_address_object(prop.source_socket_address.ip_address), observable.id_))
                        continue
                except AttributeError:
                    pass
            except BaseException:
                # 失敗時は無視する
                traceback.print_exc()
                pass
        return lines
