import datetime
import pytz
import requests
import traceback
import json
from mongoengine import connect, fields
from mongoengine.document import Document
from mongoengine.errors import DoesNotExist
from ctirs.models import SNSConfig, System

CIRCL_API_URL_PREFIX = 'http://cve.circl.lu/api/cve/'


class Attck(Document):
    name = fields.StringField(unique=True, max_length=32)
    aliases = fields.ListField()
    intrusion_set = fields.DictField()
    created = fields.DateTimeField(default=datetime.datetime.now)

    meta = {
        'db_alias': 'attck'
    }

    @classmethod
    # ATT&CK から情報取得して攻撃者リストを保存する
    def modify_save_attck_information(cls):
        from feeds.adapter.att_ck import ATTCK_Taxii_Server
        # ATTCK 洗い替え
        ATTCK_Taxii_Server.modify_intrusion_sets()
        # 攻撃者リスト取得
        attck_ta_list = cls.get_threat_actors_lists()
        # 保存
        sns_config = SNSConfig.objects.get()
        # 保存前と ATTCK をマージして保存
        org_ta_list = sns_config.common_cti_extractor_threat_actors_list.split('\n')
        attck_ta_list.extend(org_ta_list)
        new_ta_list = sorted(list(set(attck_ta_list)))
        try:
            new_ta_list.remove('')
        except ValueError:
            pass
        sns_config.common_cti_extractor_threat_actors_list = '\n'.join(new_ta_list)
        sns_config.save()
        return

    @classmethod
    def get_threat_actors_lists(cls):
        # threat_actors list 作成
        ta_list = []
        for attck in Attck.objects:
            if attck.name is not None:
                ta_list.append(attck.name)
            if attck.aliases is not None:
                for alias in attck.aliases:
                    if alias is not None:
                        if alias != attck.name:
                            ta_list.append(alias)
        ta_list = sorted(list(set(ta_list)))
        return ta_list

    @classmethod
    # attacker_name から ATT&CK の intrusion_set 情報を取得する
    def get_intrusion_set(cls, name):
        try:
            # すでにある場合は返却
            doc = Attck.objects.get(name=name)
        except DoesNotExist:
            doc = None

        # 指定の name で見つからない
        if doc is None:
            # alias で調べる
            try:
                docs = Attck.objects(aliases=name)
                if len(docs) == 0:
                    doc = None
                else:
                    doc = docs[0]
            except DoesNotExist:
                doc = None
        # それでも見つからない場合は None
        if doc is None:
            return None
        return doc.intrusion_set

    @classmethod
    # intrusion_set を新規保存
    def set_intrusion_set(cls, intrusion_set):
        doc = Attck()
        doc.intrusion_set = json.loads(intrusion_set.serialize())
        if 'name' in doc.intrusion_set:
            doc.name = doc.intrusion_set['name']
        if 'aliases' in doc.intrusion_set:
            doc.aliases = doc.intrusion_set['aliases']
        doc.save()
        return doc


class Cve(Document):
    cve = fields.StringField(unique=True, max_length=32)
    info = fields.DictField()
    created = fields.DateTimeField(default=datetime.datetime.now)

    meta = {
        'db_alias': 'circl'
    }

    @classmethod
    # cve 番号から Circl の CVE 情報を取得する
    def get_cve_info(cls, cve):
        try:
            # すでにある場合は返却
            doc = Cve.objects.get(cve=cve)
        except DoesNotExist:
            # cve.circl.lu から取得して新規 document 作成する
            doc = cls._fetch_from_circl(cve)

        # 指定の cve が見つからないなどの理由で取得できなかった場合は None
        if doc is None:
            return None
        return doc.info

    @classmethod
    def _fetch_from_circl(cls, cve):
        # cve.circl.lu から取得する
        url = '%s%s' % (CIRCL_API_URL_PREFIX, cve)
        try:
            resp = requests.get(url, proxies=System.get_request_proxies())
            if resp.text == 'null':
                # データが返却されていない
                return None
            info = json.loads(resp.text)
            doc = Cve()
            doc.cve = cve
            doc.info = info
            doc.created = datetime.datetime.now(pytz.utc)
            doc.save()
            return doc
        except BaseException:
            traceback.print_exc()
            # 取得できなかった
            return None


# mongo 接続
def init_mongo():
    # 接続する
    try:
        connect(SNSConfig.get_circl_mongo_database(), host=SNSConfig.get_circl_mongo_host(), port=SNSConfig.get_circl_mongo_port(), alias='circl')
    except BaseException:
        # エラーの場合はデフォルト設定
        connect(SNSConfig.DEFAULT_CIRCL_MONGO_DATABASE, host=SNSConfig.DEFAULT_CIRCL_MONGO_HOST, port=SNSConfig.DEFAULT_CIRCL_MONGO_PORT, alias='circl')

    try:
        connect(SNSConfig.get_attck_mongo_database(), host=SNSConfig.get_attck_mongo_host(), port=SNSConfig.get_attck_mongo_port(), alias='attck')
    except BaseException:
        # エラーの場合はデフォルト設定
        connect(SNSConfig.DEFAULT_ATTCK_MONGO_DATABASE, host=SNSConfig.DEFAULT_ATTCK_MONGO_HOST, port=SNSConfig.DEFAULT_ATTCK_MONGO_PORT, alias='attck')


# ATTCK コレクションがない場合は起動時に取得し、攻撃者情報リストを取得する
def init_attck_collection():
    # mongo 接続
    init_mongo()
    if len(Attck.objects) == 0:
        Attck.modify_save_attck_information()
    return
