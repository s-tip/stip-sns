import io
import os
import bs4
import requests
import urllib.parse
import tempfile
from feeds.extractor.common import BaseExtractor
from ctirs.models import AttachFile, System
from feeds.extractor.pdf import PDFExtractor
from feeds.extractor.csv import CSVExtractor
from feeds.extractor.txt import TxtExtractor


class WebExtractor(BaseExtractor):
    # referred_url に GET でアクセスし、その文章を対象に STIX 要素 (indicator, Exploit_Targets) を作成する
    @classmethod
    def get_stix_elements(cls, ta_list=[], white_list=[], **kwargs):
        referred_url = kwargs['referred_url']
        # referred_url が無指定の場合は None 返却
        if referred_url is None:
            return None
        return WebExtractor._get_element_from_referred_url(referred_url, ta_list, white_list)

    # 指定の content から indicators, cve, threat_actor の要素を返却する
    @classmethod
    def _get_element_from_post(cls, content, referred_url, ta_list=[], white_list=[]):
        INDICATOR_BASE = 'Referred-URL:'
        outfp = io.StringIO(content)
        title_base_name = '%s %s' % (INDICATOR_BASE, referred_url)
        eeb = cls._get_extract_lists(outfp, title_base_name, ta_list, white_list)
        outfp.close()
        return eeb

    @classmethod
    # referred_url からファイル名を取得し、 content の内容を格納したファイルを作成した AttachFile を返却
    def _get_temp_file(cls, referred_url, content):
        file_ = AttachFile()
        # URL の最後をファイル名とする
        try:
            up = urllib.parse.urlparse(referred_url)
            file_name = up.path.split('/')[-1]
        except BaseException:
            file_name = 'undefined'
        file_.file_name = file_name

        # file_path は一時ファイル名から
        _, file_.file_path = tempfile.mkstemp()
        with open(file_.file_path, 'wb') as fp:
            fp.write(content)
        return file_

    @classmethod
    # referred_url から get でアクセスして stix 要素を抽出する
    def _get_element_from_referred_url(cls, referred_url, ta_list, white_list):
        extractors = {
            'application/pdf': PDFExtractor._get_element_from_target_file,
            'text/csv': CSVExtractor._get_element_from_target_file,
            'text/plain': TxtExtractor._get_element_from_target_file}
        try:
            resp = requests.get(referred_url, verify=False, proxies=System.get_request_proxies())
            content_type = resp.headers['content-type']
            file_ = None
            if 'text/html' in content_type:
                bs = bs4.BeautifulSoup(resp.text, 'lxml')
                return WebExtractor._get_element_from_post(bs.body.text, referred_url, ta_list=ta_list, white_list=white_list)
            else:
                # content_type が extractros の何かにマッチすればその処理を行う
                for extractor_key in list(extractors.keys()):
                    if extractor_key in content_type:
                        # 一時ファイルを作成
                        file_ = WebExtractor._get_temp_file(referred_url, resp.content)
                        try:
                            # それぞれの処理を行う
                            eeb = extractors[extractor_key](file_, ta_list=ta_list, white_list=white_list)
                            # 一時ファイルを削除してスキップ
                            if file_ is not None and file_.file_path is not None:
                                os.remove(file_.file_path)
                            return eeb
                        except BaseException:
                            # 失敗した場合は None
                            return None
            return None

        except Exception:
            import traceback
            traceback.print_exc()
            return None
