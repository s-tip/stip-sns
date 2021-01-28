import datetime
import re
import os
import fnmatch
from stix.indicator.indicator import Indicator
from stix.common import Statement
from stix.exploit_target import ExploitTarget
from stix.exploit_target.vulnerability import Vulnerability, CVSSVector
from stix.threat_actor import ThreatActor
from stix.extensions.identity.ciq_identity_3_0 import CIQIdentity3_0Instance, STIXCIQIdentity3_0, PartyName, OrganisationName
from cybox.core.observable import Observable
from cybox.objects.address_object import Address
from cybox.objects.uri_object import URI
from cybox.objects.file_object import File
from cybox.objects.domain_name_object import DomainName
from cybox.objects.address_object import EmailAddress
from stip.common.tld import TLD
from feeds.mongo import Cve
from feeds.adapter.att_ck import ATTCK_Taxii_Server
from feeds.adapter.crowd_strike import query_actors, get_actor_entities
from stix_customizer import StixCustomizer
from ctirs.models import SNSConfig

# regular expression
ipv4_reg_expression = r'.*?((?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)[\[(\{]{0,1}\.[\])\}]{0,1}){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)).*?$'
ipv4_reg = re.compile(ipv4_reg_expression)
url_reg_expression = r'.*?(https?|ftp)\[?(:)\]?(\/\/[-_.!~*\'()a-zA-Z0-9;\/?:\@&=+\$,%#]+).*?$'
url_reg = re.compile(url_reg_expression)
md5_expression = '.*?(([0-9]|[a-f]|[A-F]){32}).*?$'
md5_reg = re.compile(md5_expression)
sha1_expression = '.*?(([0-9]|[a-f]|[A-F]){40}).*?$'
sha1_reg = re.compile(sha1_expression)
sha256_expression = '.*?(([0-9]|[a-f]|[A-F]){64}).*?$'
sha256_reg = re.compile(sha256_expression)
sha512_expression = '.*?(([0-9]|[a-f]|[A-F]){128}).*?$'
sha512_reg = re.compile(sha512_expression)
domain_expression = r'.*?([A-Za-z0-9][A-Za-z0-9_-]*(\.[A-Za-z][A-Za-z0-9_-]*)*([\[(\{]{0,1}\.[\])\}]{0,1}[A-Za-z][A-Za-z][A-Za-z]*)).*?'
domain_reg = re.compile(domain_expression)
file_name_expression = r'.*?([^\\]+\.[^\\]+).*?$'
file_name_reg = re.compile(file_name_expression)
cve_expression = '.*(CVE-([0-9]){4}-([0-9]){1,5}).*$'
cve_reg = re.compile(cve_expression)
file_name_markup_expression = '[|](.+)[|]'
file_name_markup_reg = re.compile(file_name_markup_expression)
email_address_expression = r'.*?(\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*).*?$'
email_address_reg = re.compile(email_address_expression)
defang_expression = r'[\[\]()\{\}]'
defang_reg = re.compile(defang_expression)
bracket_expression = r'^\((?P<val>.*)\)$'
bracket_reg = re.compile(bracket_expression)
square_bracket_expression = r'^\[(?P<val>.*)\]$'
square_bracket_reg = re.compile(square_bracket_expression)
curly_bracket_expression = r'^\{(?P<val>.*)\}$'
curly_bracket_reg = re.compile(curly_bracket_expression)
left_bracket_expression = r'^[\(\[\{](?P<val>.*)$'
left_bracket_reg = re.compile(left_bracket_expression)
right_bracket_expression = r'^(?P<val>.*)[\)\]\}]$'
right_bracket_reg = re.compile(right_bracket_expression)

bracket_regs = [
    bracket_reg,
    square_bracket_reg,
    curly_bracket_reg
]

JSON_OBJECT_TYPE_IPV4 = 'ipv4'
JSON_OBJECT_TYPE_URI = 'uri'
JSON_OBJECT_TYPE_MD5 = 'md5'
JSON_OBJECT_TYPE_SHA1 = 'sha1'
JSON_OBJECT_TYPE_SHA256 = 'sha256'
JSON_OBJECT_TYPE_SHA512 = 'sha512'
JSON_OBJECT_TYPE_DOMAIN = 'domain'
JSON_OBJECT_TYPE_FILE_NAME = 'file_name'
JSON_OBJECT_TYPE_EMAIL_ADDRESS = 'email_address'


class CTIElementExtractorBean(object):
    def __init__(self):
        self.indicators = []
        self.ttps = []
        self.tas = []
        self.custom_objects = []

    def extend(self, eeb):
        if eeb is None:
            return
        if not isinstance(eeb, CTIElementExtractorBean):
            return
        self.indicators.extend(eeb.indicators)
        self.ttps.extend(eeb.ttps)
        self.tas.extend(eeb.tas)
        self.custom_objects.extend(eeb.custom_objects)
        
    def append_indicator(self, indicator):
        self.indicators.append(indicator)

    def append_ttp(self, ttp):
        self.ttps.append(ttp)

    def append_ta(self, ta):
        self.tas.append(ta)

    def append_custom_object(self, custom_object):
        self.custom_objects.append(custom_object)

    def get_indicators(self):
        return self.indicators

    def get_ttps(self):
        return self.ttps

    def get_tas(self):
        return self.tas

    def get_custom_objects(self):
        return self.custom_objects


class BaseExtractor(object):
    word_extract_expression = r'([\[\]\-_.!~*\'(){}a-zA-Z0-9;\/?:\@&=+\$,%#]+)'
    word_extract_reg = re.compile(word_extract_expression)
    CVE_TYPE_STR = 'cve'
    TA_TYPE_STR = 'threat_actor'

    # 引数 STIX 要素 (indicator, Exploit_Targets) を作成する
    @classmethod
    def get_stix_elements(cls, **kwargs):
        raise NotImplementedError

    # 単語ごとに、ipv4, url, hash, domainを含むかを判定する、
    # 最初に見つかった要素を (object, type) として返却。
    @classmethod
    def _get_objects_from_word(cls, word):
        if len(word) == 0:
            return None, None
        return CommonExtractor.get_object_from_word(word)

    # 1行から word ごとに分割する
    @classmethod
    def _get_words_from_line(cls, line):
        return cls.word_extract_reg.findall(line)

    @staticmethod
    def _remove_parentheses(word):
        for brakcet_reg in bracket_regs:
            ret = bracket_reg.match(word)
            if ret:
                return ret.group('val')
        return word

    @staticmethod
    def _remove_parenthes(word):
        ret = left_bracket_reg.match(word)
        if ret:
            word = ret.group('val')
        ret = right_bracket_reg.match(word)
        if ret:
            word = ret.group('val')
        return word

    @staticmethod
    def _refang_ioc(v):
        return defang_reg.sub('', v)

    @classmethod
    # value が bytes なら str にする
    def decode(cls, v_):
        if isinstance(v_, bytes):
            return v_.decode()
        return v_

    # white_list に value がマッチングする場合は True
    @classmethod
    def _is_included_white_list(cls, value, white_list):
        for white_item in white_list:
            # 正規表現に一つでもマッチングした場合は True
            if fnmatch.fnmatch(value, white_item):
                return True
        return False

    # outfp (StringIO) から indicators, cve, threat_actor のリストを作成する
    # outfp は close しない (呼び出し元で close すること)
    # 1.含まれている観測事象を自動判別し Object, Title の tuple リストを作成する (white_list にマッチングする場合は抽出しない)
    # 2.含まれている cve を自動判別し tuple リストを作成する
    # 3.含まれている ta_list を自動判別し tuple リストを作成する
    @classmethod
    def _get_extract_lists(cls, outfp, title_base_name, ta_list, white_list):
        # 改行ごとにリストとする
        contents = outfp.getvalue()
        extract_dict = {}
        eeb = CTIElementExtractorBean()
        indicator_index = 1
        ttp_index = 1
        ta_index = 1
        custom_objects = StixCustomizer.get_instance().get_custom_objects()

        # 一行から半角文字郡のリストを抽出する
        words = cls._get_words_from_line(contents)
        # 存在しない場合は読み飛ばし
        if words is not None:
            # 単語ごとに indicators チェックする
            for word in words:
                word = BaseExtractor._remove_parentheses(word)
                type_, value = cls._get_objects_from_word(word)
                if type_ is not None:
                    # 重複チェック
                    duplicate_flag, extract_dict = CommonExtractor.is_duplicate(extract_dict, type_, value)
                    if not duplicate_flag:
                        # 重複していないので登録
                        title = '%s-%04d' % (title_base_name, indicator_index)
                        # white_list check
                        white_flag = cls._is_included_white_list(value, white_list)
                        # white_list に含まれない場合に checked をつける
                        eeb.append_indicator((cls.decode(type_), cls.decode(value), cls.decode(title), cls.decode(title_base_name), (white_flag is False)))
                        indicator_index += 1
                # cve チェック
                cve = CommonExtractor.get_cve_from_word(word)
                if cve is not None:
                    duplicate_flag, extract_dict = CommonExtractor.is_duplicate(extract_dict, cls.CVE_TYPE_STR, cve)
                    if not duplicate_flag:
                        # 重複していないので登録
                        title = '%s-%04d' % (title_base_name, ttp_index)
                        eeb.append_ttp((cls.decode(cls.CVE_TYPE_STR), cls.decode(cve), cls.decode(title), cls.decode(title_base_name), True))
                        ttp_index += 1
            for index, word in enumerate(words):
                ta = CommonExtractor.get_ta_from_words(words[index:], ta_list)
                if ta is not None:
                    duplicate_flag, extract_dict = CommonExtractor.is_duplicate(extract_dict, cls.TA_TYPE_STR, ta)
                    if not duplicate_flag:
                        # 重複していないので登録
                        title = '%s-%04d' % (title_base_name, ta_index)
                        eeb.append_ta((cls.decode(cls.TA_TYPE_STR), cls.decode(ta), cls.decode(title), cls.decode(title_base_name), True))
                        ta_index += 1

            custom_object_index = 1
            for co in CommonExtractor.get_custom_objects_from_words(words, custom_objects):
                obj_name, prop_name, obj_value = co
                title = '%s-%04d' % (title_base_name, custom_object_index)
                type_ = 'CUSTOM_OBJECT:%s/%s' % (obj_name, prop_name)
                eeb.append_custom_object((cls.decode(type_), cls.decode(obj_value), cls.decode(title), cls.decode(title_base_name), True))
                custom_object_index += 1
        return eeb


class FileExtractor(BaseExtractor):
    TARGET_EXT_STRING = None

    # ファイルから STIX 要素 (indicator, Exploit_Targets) を作成する
    @classmethod
    def get_stix_elements(cls, files, ta_list=[], white_list=[], **kwargs):
        target_files = cls._get_target_files(files)
        # 該当ファイルがないので Indicators を作成しない
        if len(target_files) == 0:
            return None
        eeb = CTIElementExtractorBean()
        for file_ in target_files:
            # Observable の Object リストと cve リストを Web Browser で確認用の indicators リストを取得する
            this_eeb = cls._get_element_from_target_file(
                file_, ta_list=ta_list, white_list=white_list)
            eeb.extend(this_eeb)
        return eeb

    # Extract 対象ファイルを返却
    @classmethod
    def _get_target_files(cls, files):
        ret_ = []
        if files is not None:
            for file_ in files:
                if cls._is_target_file(file_.file_name):
                    ret_.append(file_)
        return ret_

    # Extract 対象 ファイルであるかの判定ロジック
    @classmethod
    def _is_target_file(cls, file_name):
        # 引数の file_name の拡張子が TARGET_EXT_STRING の時に該当であると判定する
        _, ext = os.path.splitext(file_name)
        return ext.lower() == cls.TARGET_EXT_STRING

    @classmethod
    # 対象のファイルから indicators, ttps リストを作成して返却する
    def _get_element_from_target_file(cls, file_):
        raise NotImplementedError

    # 単語ごとに、ipv4, url, hash, domainを含むかを判定する、
    # 最初に見つかった要素を (object, type) として返却。
    @classmethod
    def _get_objects_from_word(cls, word):
        return super(FileExtractor, cls)._get_objects_from_word(word)

    # 1行から word ごとに分割する
    @classmethod
    def _get_words_from_line(cls, line):
        return super(FileExtractor, cls)._get_words_from_line(line)


class CommonExtractor(object):
    parentheses_reg_expression = r'\((?P<content>.+)\)'
    parentheses_reg = re.compile(parentheses_reg_expression)
    square_bracket_reg_expression = r'\[(?P<content>.+)\]'
    square_bracket_reg = re.compile(square_bracket_reg_expression)
    curly_reg_expression = r'\{(?P<content>.+)\}'
    curly_reg = re.compile(curly_reg_expression)

    # TLD 判定インスタンス
    try:
        public_suffix_list_file_path = SNSConfig.get_sns_public_suffix_list_file_path()
    except BaseException:
        # 設定 DB から取得できない場合はデフォルト値
        public_suffix_list_file_path = SNSConfig.DEFAULT_SNS_PUBLIC_SUFFIX_LIST_FILE_PATH
    tld = TLD(public_suffix_list_file_path)

    # object,title から Indicator 作成
    @staticmethod
    def get_indicator_from_object(object_, title, user_timezone):
        # Observableを作成する
        observable = Observable()
        observable.object_ = object_
        # observable,description,titleを設定する
        indicator = Indicator()
        indicator.timestamp = datetime.datetime.now(tz=user_timezone)
        indicator.title = title
        indicator.description = title
        indicator.observable = observable
        return indicator

    # cve番号からExploitTarget作成
    @staticmethod
    def get_exploit_target_from_cve(cve):
        title = cve
        # description は mitreのページヘのリンク
        description = 'https://cve.mitre.org/cgi-bin/cvename.cgi?name=' + str(cve)
        # ExploitTarget
        et = ExploitTarget()
        et.title = title
        et.description = description
        et.short_description = description
        # Vulnerability
        vulnerablity = Vulnerability()
        vulnerablity.title = title
        vulnerablity.description = description
        vulnerablity.short_description = description
        vulnerablity.cve_id = cve
        et.add_vulnerability(vulnerablity)
        return et

    # 辞書にすでにそのタイプの値が含まれているかチェックする
    # 存在する場合はTrue,しない場合はFalse
    # 更新された辞書と一緒にtupleで返却
    @staticmethod
    def is_duplicate(d, type_, value):
        if type_ not in d:
            # 辞書にそのタイプが初出の場合はリストを作成
            d[type_] = [value]
            return False, d
        else:
            # 辞書にそのタイプが存在する場合は重複している
            if value in d[type_]:
                return True, d
            else:
                d[type_].append(value)
                return False, d

    @staticmethod
    def is_punctuation_char(c):
        if ((c == '.') or (c == ',') or (c == '!') or (c == '?') or (c == ';') or (c == ':')):
            return True
        return False

    @staticmethod
    def remove_punctuation_char(word):
        def remove_bracket(word, reg):
            ret = reg.match(word)
            if ret is not None:
                return ret.group('content')
            else:
                return word

        # puctuation 対応
        if (len(word) == 0):
            return ''
        if (len(word) == 1):
            if CommonExtractor.is_punctuation_char(word):
                return ''
        last_char = word[-1]
        if CommonExtractor.is_punctuation_char(last_char):
            word = word[:-1]

        return word

    # 単語に cve 情報が含まれていたら返却する
    @staticmethod
    def get_cve_from_word(word):
        # puctuation 対応
        word = CommonExtractor.remove_punctuation_char(word)
        if len(word) == 0:
            return None
        # cveか?
        v = CommonExtractor._get_cve_value(word)
        if v is not None:
            return v
        return None

    # 単語に actor 情報が含まれていたら返却する
    @staticmethod
    def get_ta_from_words(words, actors_list=[]):
        # actorか?
        for actor_words in actors_list:
            # actors_list 一つひとつの項目(actor_words)ごとに以下のチェック
            # actor_words は空白区切りでの複数ワードの可能性がある
            actor_word_list = actor_words.split(' ')
            index = 0
            isMatch = True
            # actor_words の単語一つづつごとに words をずらしてチェックする
            for actor_word in actor_word_list:
                try:
                    # puctuation 対応
                    while True:
                        word = CommonExtractor.remove_punctuation_char(words[index])
                        word = BaseExtractor._remove_parenthes(word)
                        # puctuation 対応後に長さが 0 の場合, words[index] は puctuation 文字であるため index をすすめる
                        if len(word) == 0:
                            index += 1
                        else:
                            break
                    # 大文字小文字は区別しない
                    if actor_word.lower() != word.lower():
                        # 単語が違う (次の actor_words checkを行う)
                        isMatch = False
                        break
                except IndexError:
                    # word が終端を迎えたので違う (次の actor_words checkを行う)
                    isMatch = False
                    break
                # 単語が一致したのでずらす
                index += 1
            # 最終的に一致したら actors_wordsを返却
            if isMatch:
                return actor_words
        # 一致しなかった
        return None

    @staticmethod
    def get_custom_objects_from_words(words, custom_objects):
        ret = []
        if custom_objects is None:
            return ret
        for word in words:
            word = BaseExtractor._remove_parentheses(word)
            for o_ in custom_objects:
                for prop in o_['properties']:
                    if prop['pattern'] is not None:
                        value = CommonExtractor._get_regular_value(prop['pattern'], word)
                        if value is None:
                            continue
                        ret.append((
                            BaseExtractor.decode(o_['name']),
                            BaseExtractor.decode(prop['name']),
                            BaseExtractor.decode(value)))
        return ret

    # 単語がそれぞれipv4,url,hash,domainであるかを判定する
    # そのcybox 種別 と 値を返却する
    @staticmethod
    def get_object_from_word(word):
        # word の両端 check
        if (word[0] == '\"' and word[-1] == '\"') or (word[0] == '\'' and word[-1] == '\''):
            # 両端に " か ' の場合だけ削除
            word = word[1:-1]

        # puctuation 対応
        word = CommonExtractor.remove_punctuation_char(word)
        if len(word) == 0:
            return None, None

        # ipv4か?
        v = CommonExtractor._get_ipv4_value(word)
        if v is not None:
            return JSON_OBJECT_TYPE_IPV4, BaseExtractor._refang_ioc(v)

        # urlか?
        v = CommonExtractor._get_url_value(word)
        if v is not None:
            return JSON_OBJECT_TYPE_URI, v

        # hash 値は長い順番から判定する
        # sha512か?
        v = CommonExtractor._get_sha512_value(word)
        if v is not None:
            return JSON_OBJECT_TYPE_SHA512, v

        # sha256か?
        v = CommonExtractor._get_sha256_value(word)
        if v is not None:
            return JSON_OBJECT_TYPE_SHA256, v

        # sha1か?
        v = CommonExtractor._get_sha1_value(word)
        if v is not None:
            return JSON_OBJECT_TYPE_SHA1, v

        # md5か?
        v = CommonExtractor._get_md5_value(word)
        if v is not None:
            return JSON_OBJECT_TYPE_MD5, v

        # email_addressか?
        v = CommonExtractor._get_email_address_value(word)
        if v is not None:
            return JSON_OBJECT_TYPE_EMAIL_ADDRESS, v

        # domainか?
        v = CommonExtractor._get_domain_value(word)
        if v is not None:
            # TLD が含まれていたらドメイン名と判断
            v = BaseExtractor._refang_ioc(v)
            if CommonExtractor.tld.get_tld(v) is not None:
                # ドメイン名とする
                return JSON_OBJECT_TYPE_DOMAIN, v

        # file_nameか? (reg)
        v = CommonExtractor._get_file_name_value(word)
        if v is not None:
            return JSON_OBJECT_TYPE_FILE_NAME, v

        # file_nameか? (markup)
        v = file_name_markup_reg.match(word)
        if v is not None:
            # 最初に見つかった項目のみを対象とする
            return JSON_OBJECT_TYPE_FILE_NAME, v.group(1)
        return None, None

    # web 画面から取得した indicators json から stix indicators 作成する
    @staticmethod
    def get_indicator_from_json(indicator_json, user_timezone):
        type_ = indicator_json['type']
        v = indicator_json['value']
        title = indicator_json['title']
        o_ = None

        # ipv4か?
        if type_ == JSON_OBJECT_TYPE_IPV4:
            o_ = Address()
            o_.address_value = BaseExtractor._refang_ioc(v)

        # urlか?
        if type_ == JSON_OBJECT_TYPE_URI:
            o_ = URI()
            o_.value = v

        # md5か?
        if type_ == JSON_OBJECT_TYPE_MD5:
            o_ = File()
            o_.md5 = v

        # sha1か?
        if type_ == JSON_OBJECT_TYPE_SHA1:
            o_ = File()
            o_.sha1 = v

        # sha256か?
        if type_ == JSON_OBJECT_TYPE_SHA256:
            o_ = File()
            o_.sha256 = v

        # sha512か?
        if type_ == JSON_OBJECT_TYPE_SHA512:
            o_ = File()
            o_.sha512 = v

        # email-addressか?
        if type_ == JSON_OBJECT_TYPE_EMAIL_ADDRESS:
            o_ = EmailAddress()
            o_.address_value = v

        # domainか?
        if type_ == JSON_OBJECT_TYPE_DOMAIN:
            o_ = DomainName()
            o_.value = BaseExtractor._refang_ioc(v)

        # file名か?
        if type_ == JSON_OBJECT_TYPE_FILE_NAME:
            o_ = File()
            o_.file_name = v

        # なにも該当していないので None
        if o_ is None:
            print('何も該当なし:' + str(type_) + ':' + str(v))
            return None

        # indicator 作って返却
        indicator_title = '%s (%s)' % (v, title)
        ind = CommonExtractor.get_indicator_from_object(o_, indicator_title, user_timezone)
        return ind

    @staticmethod
    def get_mitre_url_from_json(json_cve):
        mitre_url = 'https://cve.mitre.org/cgi-bin/cvename.cgi?name=' + str(json_cve)
        return mitre_url

    @staticmethod
    def get_circl_url_from_json(json_cve):
        circl_url = 'https://cve.circl.lu/cve/' + str(json_cve)
        return circl_url

    @staticmethod
    def get_ttp_common_short_description(ttp_json):
        json_cve = ttp_json['value']
        mitre_url = CommonExtractor.get_mitre_url_from_json(json_cve)
        circl_url = CommonExtractor.get_circl_url_from_json(json_cve)
        common_short_description = '%s (<a href="%s" target="_blank">MITRE</a>, <a href="%s" target="_blank">circl.lu</a>)<br/>' % (json_cve, mitre_url, circl_url)
        return common_short_description

    @staticmethod
    def get_cve_info(json_cve):
        return Cve.get_cve_info(json_cve)

    @staticmethod
    def get_vul_cvss_score(cve_info):
        try:
            vul_cvss_score = CVSSVector()
            vul_cvss_score.base_score = cve_info['cvss']
        except BaseException:
            vul_cvss_score = None
        return vul_cvss_score

    @staticmethod
    def get_cve_info_summary(cve_info):
        return cve_info['summary']

    @staticmethod
    def get_ttp_common_description(ttp_json):
        json_cve = ttp_json['value']
        circl_url = CommonExtractor.get_circl_url_from_json(json_cve)
        cve_info = CommonExtractor.get_cve_info(json_cve)
        vul_cvss_score = CommonExtractor.get_vul_cvss_score(cve_info)
        common_description = CommonExtractor.get_ttp_common_short_description(ttp_json)

        if vul_cvss_score is not None:
            common_description += ('Base Score: %s<br/>' % (vul_cvss_score.base_score))
        try:
            common_description += ('%s<br/>' % (CommonExtractor.get_cve_info_summary(cve_info)))
        except BaseException:
            # 取得失敗時は circl のページの url
            common_description += ('%s<br/>' % (circl_url))

        return common_description

    # web 画面から取得した ttp json から stix ttp 作成する
    @staticmethod
    def get_exploit_target_from_json(ttp_json):
        json_cve = ttp_json['value']
        json_title = ttp_json['title']

        # title は "%CVE番号% (index)" とする
        title = '%s (%s)' % (json_cve, json_title)

        # # CVE 情報を circl から取得する
        cve_info = CommonExtractor.get_cve_info(json_cve)

        # Expoit_Target, Vulnerability の Short Description は link
        common_short_description = CommonExtractor.get_ttp_common_short_description(ttp_json)

        # # base_score
        vul_cvss_score = CommonExtractor.get_vul_cvss_score(cve_info)

        # Expoit_Target, Vulnerability の Description 作成
        common_decritpion = CommonExtractor.get_ttp_common_description(ttp_json)

        # ExploitTarget
        et = ExploitTarget()
        et.title = title
        et.description = common_decritpion
        et.short_description = common_short_description
        # Vulnerability
        vulnerablity = Vulnerability()
        vulnerablity.title = title
        vulnerablity.description = common_decritpion
        vulnerablity.short_description = common_short_description
        vulnerablity.cve_id = json_cve
        if vul_cvss_score is not None:
            vulnerablity.cvss_score = vul_cvss_score
        et.add_vulnerability(vulnerablity)
        return et

    @staticmethod
    def _get_ta_description_from_attck(ta_value):
        # ATT&CK から Attacker Group 情報を取得する
        intrusion_set = ATTCK_Taxii_Server.get_intrusion_set(ta_value)
        if intrusion_set is None:
            return None, None
        description = ''
        if 'description' in intrusion_set and len(intrusion_set['description']) != 0:
            description += intrusion_set['description']
        if 'aliases' in intrusion_set:
            description += '\n\n<br/><br/>Aliases: '
            for alias in intrusion_set['aliases']:
                description += ('%s, ' % (alias))
            description = description[:-2]
            aliases = intrusion_set['aliases']
        else:
            aliases = None
        return description, aliases

    @staticmethod
    def _get_ta_description_from_crowd_strike(ta_value):
        try:
            response = query_actors(ta_value)
            if len(response['resources']) == 0:
                return None, None
            actor_id = response['resources'][0]
            attackers_entities = get_actor_entities(actor_id)
            if len(attackers_entities['resources']) == 0:
                return None, None
            attacker_entity = attackers_entities['resources'][0]

            description = '<br/>'
            description += ('%s: %s<br/>' % ('Threat Actor', ta_value))
            if 'known_as' in attacker_entity:
                aliases = attacker_entity['known_as']
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
                if url.startswith('https://falcon.crowdstrike.com/actors/'):
                    url = url.replace('https://falcon.crowdstrike.com/actors/', 'https://falcon.crowdstrike.com/intelligence/actors/')
                description += ('%s: <a href="%s" target="_blank">%s</a><br/>' % ('Report URL', url, url))
            return description, aliases
        except BaseException:
            return None, None

    # value , descirption から ThreatActorObject 作成する
    @staticmethod
    def _get_threat_actor_object(value, description=None, crowd_strike_motivations=[]):
        # 攻撃者情報作成
        organisation_name = OrganisationName(value)
        party_name = PartyName()
        party_name.add_organisation_name(organisation_name)
        identity_specification = STIXCIQIdentity3_0()
        identity_specification.party_name = party_name
        identity = CIQIdentity3_0Instance()

        # ThreatActor
        ta = ThreatActor()
        ta.identity = identity
        ta.identity.specification = identity_specification
        # Title に抽出した Threat Actor 名前
        ta.title = value
        ta.description = description
        ta.short_description = description
        ta.identity = identity

        # motivations 作成
        for crowd_strike_motivation in crowd_strike_motivations:
            ta_motivation = Statement(crowd_strike_motivation['value'])
            # motivation 追加
            ta.add_motivation(ta_motivation)
        return ta

    # regをもとにitemを解析し、最初に見つかった文字列を返却
    # 存在しない場合はNone
    @staticmethod
    def _get_regular_value(reg, item):
        v = reg.match(item)
        if v is not None:
            # 最初に見つかった項目のみを対象とする
            r = v.group(1)
            return r
        return None

    # 文字列がipv4を含む場合、最初に見つかった文字列を返却
    # 存在しない場合はNone
    @staticmethod
    def _get_ipv4_value(item):
        v = ipv4_reg.match(item)
        if v is not None:
            return v.group(1)
        return None

    # 文字列がurlを含む場合、: の前後に [] がある場合は取り除いて返却
    # 存在しない場合はNone
    @staticmethod
    def _get_url_value(item):
        v = url_reg.match(item)
        if v is not None:
            return v.group(1) + v.group(2) + v.group(3)
        return None

    # 文字列がmd5を含む場合、最初に見つかった文字列を返却
    # 存在しない場合はNone
    @staticmethod
    def _get_md5_value(item):
        return CommonExtractor._get_regular_value(md5_reg, item)

    # 文字列がsha1を含む場合、最初に見つかった文字列を返却
    # 存在しない場合はNone
    @staticmethod
    def _get_sha1_value(item):
        return CommonExtractor._get_regular_value(sha1_reg, item)

    # 文字列がsha256を含む場合、最初に見つかった文字列を返却
    # 存在しない場合はNone
    @staticmethod
    def _get_sha256_value(item):
        return CommonExtractor._get_regular_value(sha256_reg, item)

    # 文字列がsha512を含む場合、最初に見つかった文字列を返却
    # 存在しない場合はNone
    @staticmethod
    def _get_sha512_value(item):
        return CommonExtractor._get_regular_value(sha512_reg, item)

    # 文字列がemail-addressを含む場合、最初に見つかった文字列を返却
    # 存在しない場合はNone
    @staticmethod
    def _get_email_address_value(item):
        return CommonExtractor._get_regular_value(email_address_reg, item)

    # 文字列がdomainを含む場合、最初に見つかった文字列を返却
    # 存在しない場合はNone
    @staticmethod
    def _get_domain_value(item):
        return CommonExtractor._get_regular_value(domain_reg, item)

    @staticmethod
    def _get_file_name_value(item):
        ret = CommonExtractor._get_regular_value(file_name_reg, item)
        if ret:
            try:
                float(ret)
                return None
            except ValueError:
                return ret
        return ret

    # 文字列がcveを含む場合、最初に見つかった文字列を返却
    # 存在しない場合はNone
    @staticmethod
    def _get_cve_value(item):
        return CommonExtractor._get_regular_value(cve_reg, item)
