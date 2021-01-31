import io
from feeds.extractor.common import BaseExtractor

INDICATOR_BASE_NAME = 'S-TIP-SNS-Post-Content'


class PostExtractor(BaseExtractor):
    @classmethod
    def get_stix_elements(cls, post, param):
        return PostExtractor._get_element_from_post(post, param)

    @classmethod
    def _get_element_from_post(cls, post, param):
        outfp = io.StringIO(post)
        eeb = cls._get_extract_lists(outfp, INDICATOR_BASE_NAME, param.list_param)
        outfp.close()
        return eeb
