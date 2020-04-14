from bs4 import BeautifulSoup
import datetime
import pytz
import iocextract
from django.conf import settings as django_settings
from stix2 import parse
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import pagesizes, colors, fonts
from reportlab.lib.units import cm, mm
from reportlab.lib.pagesizes import A4, portrait
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus.doctemplate import SimpleDocTemplate
from reportlab.platypus import Paragraph, PageBreak, Spacer
from reportlab.platypus.tables import Table, TableStyle
from feeds.feed_stix import FeedStix


class FeedPDFStixBase(object):
    def __init__(self, feed):
        pass

    def get_timestamp(self):
        raise NotImplementedError

    def get_indicators(self):
        raise NotImplementedError

    def get_exploit_targets(self):
        raise NotImplementedError

    def get_threat_actors(self):
        raise NotImplementedError


class FeedPDFStixV1(FeedPDFStixBase):
    def __init__(self, feed):
        super().__init__(feed)
        feed_stix = FeedStix(stix_file_path=feed.stix_file_path)
        self.stix_package = feed_stix.stix_package
 
    def get_timestamp(self):
        return str(self.stix_package.timestamp)

    def get_indicators(self):
        return FeedStix.get_indicators(self.stix_package)

    def get_exploit_targets(self):
        return FeedStix.get_exploit_targets(self.stix_package)

    def get_threat_actors(self):
        return FeedStix.get_threat_actors(self.stix_package)


class FeedPDFStixV2(FeedPDFStixBase):
    def __init__(self, feed):
        from feeds.views import get_csv_from_bundle_id
        super().__init__(feed)
        with open(feed.stix_file_path, 'r') as fp:
            self.stix_package = parse(fp.read(), allow_custom=True)
            self.package_id = feed.package_id
        self.indicators = []
        self.exploit_targets = []
        self.threat_actors = []
        for item in get_csv_from_bundle_id(self.package_id, threat_actors=True):
            (type_, value, description) = item
            if type_ == 'cve':
                self.exploit_targets.append(item)
            elif type_ == 'threat_actor':
                self.threat_actors.append(item)
            else:
                self.indicators.append(item)
 
    def get_timestamp(self):
        ts = None
        for o_ in self.stix_package.objects:
            if 'modified' in o_:
                o_dt = o_['modified']
            else:
                o_dt = o_['created']
            if ts:
                if o_dt > ts:
                    ts = o_dt
            else:
                ts = o_dt
        return str(ts)

    def get_indicators(self):
        return self.indicators

    def get_exploit_targets(self):
        return self.exploit_targets

    def get_threat_actors(self):
        return self.threat_actors


def _get_feed_pdf_stix(feed):
    if feed.stix_version.startswith('1.'):
        return FeedPDFStixV1(feed)
    elif feed.stix_version.startswith('2.'):
        return FeedPDFStixV2(feed)
    return None
 

class FeedPDF(object):

    FONT_MEIRYO = 'Meiryo'
    FONT_MEIRYO_BOLD = 'Meiryo-Bold'

    django_settings.PDF_FONT_DIR
    pdfmetrics.registerFont(TTFont(FONT_MEIRYO, django_settings.PDF_FONT_DIR + 'meiryo.ttc'))
    pdfmetrics.registerFont(TTFont(FONT_MEIRYO_BOLD, django_settings.PDF_FONT_DIR + 'meiryob.ttc'))

    fonts.addMapping(FONT_MEIRYO, 0, 0, FONT_MEIRYO)  # normal
    fonts.addMapping(FONT_MEIRYO, 0, 1, FONT_MEIRYO + '-Italic')  # italic
    fonts.addMapping(FONT_MEIRYO, 1, 0, FONT_MEIRYO + '-Bold')  # bold
    fonts.addMapping(FONT_MEIRYO, 1, 1, FONT_MEIRYO + '-BoldItalic')  # italic and bold

    def __init__(self):
        self.package_id = None
        self.tlp = None

    # Header文字列を取得する
    def _set_header_string(self):
        if self.package_id is not None: 
            return 'S-TIP CTI PDF Report: %s' % (self.package_id)
        else:
            return 'S-TIP CTI PDF Report'

    # Footer文字列を取得する
    def _set_footer_string(self):
        t_format = '%B %-d, %Y %H:%M%z'
        d = datetime.datetime.now(pytz.timezone(django_settings.TIME_ZONE))
        return 'CTI Converted to PDF by S-TIP - %s' % (d.strftime(t_format))

    # 各ページ共通描画
    def _set_common_per_page(self, canvas, doc):
        PAGE_WIDTH, PAGE_HEIGHT = pagesizes.A4
        PDF_HEADER_FONT_SIZE = 8

        canvas.saveState()

        # header
        string = self._set_header_string()
        canvas.setFont(self.FONT_MEIRYO, PDF_HEADER_FONT_SIZE)
        canvas.drawCentredString((PAGE_WIDTH / 2.0), (PAGE_HEIGHT - 32), string)

        # footer
        string = self._set_footer_string()
        canvas.setFont(self.FONT_MEIRYO, PDF_HEADER_FONT_SIZE)
        canvas.drawCentredString((PAGE_WIDTH / 2.0), 24, string)

        # 左上: アイコン
        image_path = django_settings.PDF_IMAGE_DIR + 'stip-logo.png'
        canvas.drawImage(image_path, 8.4*mm, 273.6*mm, width=15*mm, height=15*mm, preserveAspectRatio=True, mask=[0, 0, 0, 0, 0, 0])
        # 297(A4)-15(image)-8.4mm(margin)
        # 右上: TLP表記
        string = 'TLP: %s' % (self.tlp.upper())
        # Tableにて実装
        data = [[string], ]
        table = Table(data)
        if self.tlp.upper() == 'RED':
            color = '#FF0033'
        elif self.tlp.upper() == 'AMBER':
            color = '#FFC000'
        elif self.tlp.upper() == 'GREEN':
            color = '#33FF00'
        else:
            color = '#FFFFFF'

        table.setStyle(TableStyle([
            # 背景色は黒
            ('BACKGROUND', (0, 0), (-1, -1), colors.black),
            # テキスト色はTLPによって異なる
            ('TEXTCOLOR', (0, 0), (-1, -1), color),
            # 表で使うフォントとそのサイズを設定
            ('FONT', (0, 0), (-1, -1), self.FONT_MEIRYO, 9),
            # ('FONT', (0, 0), (-1, -1), 'CJK', 9),
            # 四角に罫線を引いて、0.5の太さで、色は黒
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            # 四角の内側に格子状の罫線を引いて、0.25の太さで、色は赤
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            # セルの縦文字位置を、TOPにする
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        # 配置位置
        table.wrapOn(canvas, 178*mm, 282.7*mm)
        table.drawOn(canvas, 178*mm, 282.7*mm)

        canvas.restoreState()

    def _first_page(self, canvas, doc):
        self._set_common_per_page(canvas, doc)

    def _last_page(self, canvas, doc):
        self._set_common_per_page(canvas, doc)

    # テーブル作成
    def _create_table(self, d, row_num, col_widths):
        HEADER_BACKGROUND_COLOR = colors.HexColor('#48ACC6')
        EVEN_BACKGROUND_COLOR = colors.HexColor('#DAEEF3')
        ODD_BACKGROUND_COLOR = colors.white

        table = Table(d, colWidths=col_widths)
        table.setStyle(TableStyle([
            # 背景色
            # 先頭行(ヘッダ)
            # 2ECCFA
            ('BACKGROUND', (0, 0), (-1, 0), HEADER_BACKGROUND_COLOR),
            # 表で使うフォントとそのサイズを設定
            ('FONT', (0, 0), (-1, -1), self.FONT_MEIRYO, 9),
            # 先頭行だけbold
            ('FONT', (0, 0), (-1, 0), self.FONT_MEIRYO_BOLD, 9),
            # 先頭行は白
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            # 罫線
            ('BOX', (0, 0), (-1, -1), 0.10, HEADER_BACKGROUND_COLOR),
            ('INNERGRID', (0, 0), (-1, -1), 0.10, HEADER_BACKGROUND_COLOR),
            # セルの縦文字位置を、TOPにする
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))

        # stripe
        for i in range(row_num):
            if (i % 2) == 0:
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, i + 1), (-1, i + 1), EVEN_BACKGROUND_COLOR),
                    ('TEXTCOLOR', (0, i + 1), (-1, i + 1), colors.black),
                ]))
            else:
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, i + 1), (-1, i + 1), ODD_BACKGROUND_COLOR),
                    ('TEXTCOLOR', (0, i + 1), (-1, i + 1), colors.black),
                ]))
        return table

    # <A>タグを除外して、最後にURLを追記
    def _html_text(self, text):
        text = text.replace('<br>', '\n')
        text = text.replace('<br/>', '\n')
        soup = BeautifulSoup(text, 'html.parser')
        output = soup.get_text()
        elems = soup.find_all('a')
        for elem in elems:
            output = output + '\n' + elem.get('href')

        output = output.replace('\n', '<br/>')
        return output

    # PDF作成
    def make_pdf_content(self, response, feed):
        self.package_id = feed.package_id
        self.tlp = feed.tlp
        feed_pdf_stix = _get_feed_pdf_stix(feed)
        # style変更
        styles = getSampleStyleSheet()
        for name in ('Normal', 'BodyText', 'Title', 'Heading1', 'Heading2', 'Heading3', 'Heading4', 'Heading5', 'Heading6', 'Bullet', 'Definition', 'Code'):
            styles[name].wordWrap = 'CJK'
            styles[name].fontName = 'meiryo'

        # doc作成
        doc = SimpleDocTemplate(response, pagesize=portrait(A4))

        story = []

        # Title
        string = '<b>Title:</b> %s' % iocextract.defang(feed.title)
        story.append(Paragraph(string, styles['Normal']))

        # Author
        if feed.administrative_code is None:
            administrative_code = '-'
        else:
            administrative_code = feed.administrative_code
        if feed.country_code is None:
            country_code = '-'
        else:
            country_code = feed.country_code

        string = '%s (%s - %s, %s)' % (feed.user.get_screen_name(), feed.user.get_sector_display(), administrative_code, country_code)
        txt = '<b>Author:</b> %s' % (string)
        story.append(Paragraph(txt, styles['Normal']))

        # Produced Time
        ts = feed_pdf_stix.get_timestamp()
        txt = '<b>Produced Time:</b> %s' % (ts)
        story.append(Paragraph(txt, styles['Normal']))

        # STIX Package ID
        string = str(feed.package_id)
        txt = '<b>STIX Package ID:</b> %s' % (string)
        story.append(Paragraph(txt, styles['Normal']))

        # 空行
        story.append(Spacer(1, 1.0*cm))

        # content
        txt = '<b>Content:</b>'
        story.append(Paragraph(txt, styles['Normal']))
        txt = iocextract.defang(feed.post)
        story.append(Paragraph(txt, styles['Normal']))

        # 空行
        story.append(Spacer(1, 1.0*cm))

        # テーブルのセルスタイル設定
        style = ParagraphStyle(name='Normal', fontName=self.FONT_MEIRYO, fontSize=9, leading=9)

        # indicators
        indicators = feed_pdf_stix.get_indicators()
        if len(indicators) == 0:
            txt = '<b>Indicators:</b> No Data'
            story.append(Paragraph(txt, styles['Normal']))
        else:
            txt = '<b>Indicators:</b>'
            story.append(Paragraph(txt, styles['Normal']))
            # 空行
            story.append(Spacer(1, 0.1*cm))
            # Table
            d = [
                # header
                ['Type', 'Indicators'],
            ]

            # Sort(優先度は1列目、2列目の順で名前順)
            indicators.sort(key=lambda x: x[1])
            indicators.sort(key=lambda x: x[0])

            # STIXからObservablesとIndicatorsを抽出
            for item in indicators:
                (type_, value, _) = item
                item = []
                item.append(Paragraph(type_, style))
                # file_nameの場合は値がパイプで囲まれている
                if type_ == 'file_name':
                    # 前後のパイプをトリミング
                    value = value[1:-1]
                # defang
                value = iocextract.defang(value)
                item.append(Paragraph(value, style))
                d.append(item)

            # テーブル作成とスタイル設定
            indicators_table = self._create_table(d, len(indicators), (20*mm, 135*mm))
            story.append(indicators_table)

        # 空行
        story.append(Spacer(1, 1.0*cm))

        # Exploit Targets
        exploit_targets = feed_pdf_stix.get_exploit_targets()
        if len(exploit_targets) == 0:
            txt = '<b>Exploit Targets:</b> No Data'
            story.append(Paragraph(txt, styles['Normal']))
        else:
            txt = '<b>Exploit Targets:</b>'
            story.append(Paragraph(txt, styles['Normal']))
            # 空行
            story.append(Spacer(1, 0.1*cm))
            # Table
            d = [
                # header
                ['CVE', 'Description'],
            ]

            # Description情報を抽出
            for item in exploit_targets:
                (_, cve, value) = item
                item = []
                value = self._html_text(value)
                item.append(Paragraph(cve, style))
                item.append(Paragraph(value, style))
                d.append(item)

            # テーブル作成とスタイル設定
            cve_table = self._create_table(d, len(exploit_targets), (30*mm, 125*mm))
            story.append(cve_table)

        # 空行
        story.append(Spacer(1, 1.0*cm))

        # Threat Actors
        threat_actors = feed_pdf_stix.get_threat_actors()
        if len(threat_actors) == 0:
            txt = '<b>Threat Actors:</b> No Data'
            story.append(Paragraph(txt, styles['Normal']))
        else:
            txt = '<b>Threat Actors:</b>'
            story.append(Paragraph(txt, styles['Normal']))
            # 空行
            story.append(Spacer(1, 0.1*cm))
            # Table
            d = [
                # header
                ['Name', 'Description'],
            ]

            # Description情報を抽出
            for item in threat_actors:
                (_, actor, value) = item
                item = []
                item.append(Paragraph(actor, style))
                item.append(Paragraph(str(value), style))
                d.append(item)

            # テーブル作成とスタイル設定
            actors_table = self._create_table(d, len(threat_actors), (30*mm, 125*mm))
            story.append(actors_table)

        # 改ページ
        story.append(PageBreak())

        # PDF 作成
        doc.build(story, onFirstPage=self._first_page, onLaterPages=self._last_page)
