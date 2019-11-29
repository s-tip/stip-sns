# -*- coding: utf-8 -*-
from io import StringIO
from feeds.extractor.common import FileExtractor

class TxtExtractor(FileExtractor):
    TARGET_EXT_STRING = '.txt'

    #指定の TXT ファイルを開き、indicators, cve, threat_actor の要素を返却する
    @classmethod
    def _get_element_from_target_file(cls,file_,ta_list=[],white_list=[]):
        with open(file_.file_path,'r') as fp:
            outfp = StringIO(fp.read())
            confirm_indicators,confirm_ttps,confirm_tas = cls._get_extract_lists(outfp,file_.file_name,ta_list,white_list)
            outfp.close()
            return confirm_indicators,confirm_ttps,confirm_tas
        return None,None,None


