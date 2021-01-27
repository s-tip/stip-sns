from feeds.extractor.csv import CSVExtractor
from feeds.extractor.pdf import PDFExtractor
from feeds.extractor.post import PostExtractor
from feeds.extractor.txt import TxtExtractor
from feeds.extractor.web import WebExtractor
from feeds.extractor.common import CTIElementExtractorBean


class Extractor(object):
    # 添付ファイル or post からSTIX要素(indicator,Exploit_Targets)を作成する
    # 存在しない場合は None を返却する
    @staticmethod
    def get_stix_element(
            files,
            referred_url=None,
            posts=[],
            ta_list=[],
            white_list=[],
            scan_csv=True,
            scan_pdf=False,
            scan_post=True,
            scan_txt=True):

        # scan するコンテンツのフラグとクラス
        scan_contents = [
            (scan_csv, CSVExtractor),
            (scan_pdf, PDFExtractor),
            (scan_txt, TxtExtractor),
            # (scan_post, PostExtractor),
            # scan_post と一緒とする
            (scan_post, WebExtractor),
        ]

        eeb = CTIElementExtractorBean()

        for scan_content in scan_contents:
            flag = scan_content[0]
            clazz = scan_content[1]
            # check flag がある場合は get_stix_elements を呼び出し、戻り値が list なら要素を追加する
            if flag:
                this_eeb = clazz.get_stix_elements(
                    files=files,
                    referred_url=referred_url,
                    ta_list=ta_list,
                    white_list=white_list)
                eeb.extend(this_eeb)

        # scan_post だけ別
        if scan_post:
            for post in posts:
                this_eeb = PostExtractor.get_stix_elements(
                    post=post,
                    ta_list=ta_list,
                    white_list=white_list)
                eeb.extend(this_eeb)

        return eeb.indicators, eeb.ttps, eeb.tas
