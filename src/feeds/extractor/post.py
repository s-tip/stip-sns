import io
from feeds.extractor.common import BaseExtractor

INDICATOR_BASE_NAME = 'S-TIP-SNS-Post-Content'


class PostExtractor(BaseExtractor):
    # post から STIX 要素 (indicator, Exploit_Targets) を作成する
    @classmethod
    def get_stix_elements(cls, post, ta_list=[], white_list=[], **kwargs):
        return PostExtractor._get_element_from_post(post, ta_list=ta_list, white_list=white_list)

    # 指定の post から indicators, cve, threat_actor の要素を返却する
    @classmethod
    def _get_element_from_post(cls, post, ta_list=[], white_list=[]):
        outfp = io.StringIO(post)
        eeb = cls._get_extract_lists(outfp, INDICATOR_BASE_NAME, ta_list, white_list)
        outfp.close()
        return eeb
