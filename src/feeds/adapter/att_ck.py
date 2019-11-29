from stix2 import TAXIICollectionSource, Filter
from taxii2client import Server, Collection
from feeds.mongo import Attck
from ctirs.models import System


class ATTCK_Taxii_Server(object):
    COLLCETION_TITLE = 'Enterprise ATT&CK'
    ATT_CK_TAXII_SERVER = 'https://cti-taxii.mitre.org'

    is_first_attck_txs_access = True
    taxii_collection_source = None

    @classmethod
    def modify_intrusion_sets(cls):
        # 初回の場合は取得する
        if cls.is_first_attck_txs_access:
            cls.is_first_attck_txs_access = False
            cls.taxii_collection_source = cls.get_taxii_collection_source()
        # Attack 全 drop
        Attck.drop_collection()
        intrusion_sets = cls.query_all()
        # cache に保存
        for intrusion_set in intrusion_sets:
            Attck.set_intrusion_set(intrusion_set)
        return

    @classmethod
    def get_taxii_collection_source(cls):
        # あらかじめ ATT&CK の TAXIICOllectionSourceを取得する
        try:
            proxies = System.get_request_proxies()
            attck_txs = Server("%s/taxii/" % (cls.ATT_CK_TAXII_SERVER), proxies=proxies)
            api_root = attck_txs.api_roots[0]
            for collection in api_root.collections:
                if collection.title == cls.COLLCETION_TITLE:
                    collection = Collection("%s/stix/collections/%s/" % (cls.ATT_CK_TAXII_SERVER, collection.id))
                    return TAXIICollectionSource(collection)
            return None
        except Exception:
            import traceback
            traceback.print_exc()
            return None

    @classmethod
    def get_intrusion_set(cls, ta_value):
        intrusion_set = Attck.get_intrusion_set(ta_value)
        # cache にあれば返却
        if intrusion_set is not None:
            return intrusion_set

        # 初回の場合は取得する
        if cls.is_first_attck_txs_access:
            cls.is_first_attck_txs_access = False
            cls.taxii_collection_source = cls.get_taxii_collection_source()

        # taxii_collection_source が未定義の場合は取得しない
        if cls.taxii_collection_source is None:
            return None
        if ta_value is None:
            return None
        if len(ta_value) == 0:
            return None
        # name で検索
        intrusion_set = cls.query_by_name(ta_value)
        if intrusion_set is None:
            # 見つからない場合は alias 検索
            intrusion_set = cls.query_by_aliases(ta_value)
        # alias でも検索できなかった場合はエラー
        if intrusion_set is None:
            return None
        # cache に保存
        doc = Attck.set_intrusion_set(intrusion_set)
        return doc.intrusion_set

    @classmethod
    # 全取得
    def query_all(cls):
        filters = [Filter("type", "=", "intrusion-set")]
        return cls.taxii_collection_source.query(filters)

    @classmethod
    # name で問い合わせ
    def query_by_name(cls, ta_value):
        filters = [Filter("type", "=", "intrusion-set"), Filter("name", "=", ta_value)]
        intrusion_sets = cls.taxii_collection_source.query(filters)
        return cls.get_query_result(intrusion_sets)

    @classmethod
    # aliases で問い合わせ
    def query_by_aliases(cls, ta_value):
        filters = [Filter("type", "=", "intrusion-set"), Filter("aliases", "contains", ta_value)]
        intrusion_sets = cls.taxii_collection_source.query(filters)
        return cls.get_query_result(intrusion_sets)

    @classmethod
    def get_query_result(cls, intrusion_sets):
        if len(intrusion_sets) != 0:
            return intrusion_sets[0]
        return None
