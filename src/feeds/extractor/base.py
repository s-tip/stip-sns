from feeds.extractor.csv import CSVExtractor
from feeds.extractor.pdf import PDFExtractor
from feeds.extractor.post import PostExtractor
from feeds.extractor.txt import TxtExtractor
from feeds.extractor.web import WebExtractor
from feeds.extractor.common import CTIElementExtractorBean

class CTIElementExtractorParam(object):
    def __init__(self, account_param, list_param, post_param):
        self.account_param = account_param
        self.list_param = list_param
        self.post_param = post_param

class CTIElementExtractorAccountParam(object):
    def __init__(self, scan_csv=True, scan_pdf=False, scan_post=True, scan_txt=True):
        self.scan_csv = scan_csv
        self.scan_pdf = scan_pdf
        self.scan_post= scan_post
        self.scan_txt= scan_txt

class CTIElementExtractorListParam(object):
    def __init__(self, ta_list, white_list):
        self.ta_list = ta_list
        self.white_list = white_list

class CTIElementExtractorPostParam(object):
    def __init__(self, files, referred_url=None, posts=[]):
        self.files = files
        self.referred_url = referred_url
        self.posts = posts

class Extractor(object):
    @staticmethod
    def get_stix_element(param):
        account_param = param.account_param
        scan_contents = [
            (account_param.scan_csv, CSVExtractor),
            (account_param.scan_pdf, PDFExtractor),
            (account_param.scan_txt, TxtExtractor),
            (account_param.scan_post, WebExtractor),
        ]
 
        eeb = CTIElementExtractorBean()
        for scan_content in scan_contents:
            flag = scan_content[0]
            clazz = scan_content[1]
            if flag:
                this_eeb = clazz.get_stix_elements(param)
                eeb.extend(this_eeb)
        if account_param.scan_post:
            for post in param.post_param.posts:
                this_eeb = PostExtractor.get_stix_elements(post, param)
                eeb.extend(this_eeb)

        return eeb
