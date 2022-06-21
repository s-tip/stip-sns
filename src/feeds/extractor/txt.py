from io import StringIO
from feeds.extractor.common import FileExtractor


class TxtExtractor(FileExtractor):
    TARGET_EXT_STRING = '.txt'

    @classmethod
    def _get_element_from_target_file(cls, file_, list_param):
        with open(file_.file_path, 'r', encoding='utf-8') as fp:
            outfp = StringIO(fp.read())
            eeb = cls._get_extract_lists(outfp, file_.file_name, list_param)
            outfp.close()
            return eeb
