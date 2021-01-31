import logging
from io import StringIO
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.layout import LAParams
from pdfminer.converter import TextConverter
from pdfminer.pdfpage import PDFPage
from feeds.extractor.common import FileExtractor

pdf_rsrcmgr = PDFResourceManager()
pdf_codec = 'utf-8'
pdf_laparams = LAParams()
pdf_laparams.detect_vertical = True
logging.getLogger("pdfminer").setLevel(logging.WARNING)


class PDFExtractor(FileExtractor):
    TARGET_EXT_STRING = '.pdf'

    @classmethod
    def _get_element_from_target_file(cls, file_, list_param):
        outfp = StringIO()

        pdf_device = TextConverter(pdf_rsrcmgr, outfp, codec=pdf_codec, laparams=pdf_laparams)
        with open(file_.file_path, 'rb') as fp:
            interpreter = PDFPageInterpreter(pdf_rsrcmgr, pdf_device)
            for page in PDFPage.get_pages(fp, set(), maxpages=0, caching=True, check_extractable=True):
                interpreter.process_page(page)
        pdf_device.close()
        eeb = cls._get_extract_lists(outfp, file_.file_name, list_param)
        outfp.close()
        return eeb
