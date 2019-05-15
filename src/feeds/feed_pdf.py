# -*- coding: utf-8 -*-
import datetime
import pytz
from django.conf import settings as django_settings
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import pagesizes, colors, fonts
from reportlab.lib.units import cm,mm
from reportlab.lib.pagesizes import A4,portrait
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus.doctemplate import SimpleDocTemplate
from reportlab.platypus import Paragraph,PageBreak,Spacer
from reportlab.platypus.tables import Table, TableStyle
from feeds.feed_stix import FeedStix

class FeedPDF(object):

    FONT_MEIRYO = 'Meiryo'
    FONT_MEIRYO_BOLD = 'Meiryo-Bold'

    django_settings.PDF_FONT_DIR
    pdfmetrics.registerFont(TTFont(FONT_MEIRYO,django_settings.PDF_FONT_DIR + 'meiryo.ttc'))
    pdfmetrics.registerFont(TTFont(FONT_MEIRYO_BOLD,django_settings.PDF_FONT_DIR + 'meiryob.ttc'))

    fonts.addMapping(FONT_MEIRYO, 0, 0, FONT_MEIRYO)    #normal
    fonts.addMapping(FONT_MEIRYO, 0, 1, FONT_MEIRYO + '-Italic')    #italic
    fonts.addMapping(FONT_MEIRYO, 1, 0, FONT_MEIRYO + '-Bold')    #bold
    fonts.addMapping(FONT_MEIRYO, 1, 1, FONT_MEIRYO + '-BoldItalic')    #italic and bold


    def __init__(self,feed,stix_package):
        self.feed = feed
        self.stix_package = stix_package

    #Header文字列を取得する
    def set_header_string(self):
        if self.stix_package is not None:
            return 'S-TIP CTI PDF Report: %s' % (self.stix_package.id_)
        else:
            return 'S-TIP CTI PDF Report'

    #Footer文字列を取得する
    def set_footer_string(self):
        t_format = '%B %-d, %Y %H:%M%z'
        d =  datetime.datetime.now(pytz.timezone(django_settings.TIME_ZONE))
        return 'CTI Converted to PDF by S-TIP - %s' % (d.strftime(t_format))
    
    #各ページ共通描画
    def set_common_per_page(self,canvas,doc):
        PAGE_WIDTH,PAGE_HEIGHT = pagesizes.A4
        PDF_HEADER_FONT_SIZE = 8

        canvas.saveState()
        
        #header
        string = self.set_header_string()
        canvas.setFont(self.FONT_MEIRYO,PDF_HEADER_FONT_SIZE)
        canvas.drawCentredString((PAGE_WIDTH/2.0),(PAGE_HEIGHT-20),string)
        
        #footer
        string = self.set_footer_string()
        canvas.setFont(self.FONT_MEIRYO,PDF_HEADER_FONT_SIZE)
        canvas.drawCentredString((PAGE_WIDTH/2.0),20,string)

        #左上: アイコン
        image_path = django_settings.PDF_IMAGE_DIR + 'apple-icon-180x180.png'
        canvas.drawImage(image_path,10*mm,285*mm,width=10*mm,height=10*mm,preserveAspectRatio=True,mask=[0,0,0,0,0,0])

        #右上: TLP表記
        string = 'TLP: %s' % (self.feed.tlp.upper())
        #Tableにて実装 
        data = [[string],]
        table = Table(data)
        if self.feed.tlp.upper() == 'RED':
            color = '#FF0033'
        elif self.feed.tlp.upper() == 'AMBER':
            color = '#FFC000'
        elif self.feed.tlp.upper() == 'GREEN':
            color = '#33FF00'
        else:
            color = '#FFFFFF'

        table.setStyle(TableStyle([
            #背景色は黒
            ('BACKGROUND',(0,0),(-1,-1),colors.black),
            #テキスト色はTLPによって異なる
            ('TEXTCOLOR',(0,0),(-1,-1),color),
            # 表で使うフォントとそのサイズを設定
            ('FONT', (0, 0), (-1, -1), self.FONT_MEIRYO, 9),
            #('FONT', (0, 0), (-1, -1), 'CJK', 9),
            # 四角に罫線を引いて、0.5の太さで、色は黒
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            # 四角の内側に格子状の罫線を引いて、0.25の太さで、色は赤
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            # セルの縦文字位置を、TOPにする
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        #配置位置
        table.wrapOn(canvas, 180*mm, 287*mm)
        table.drawOn(canvas, 180*mm, 287*mm)
        
        canvas.restoreState()


    def first_page(self,canvas,doc):
        self.set_common_per_page(canvas,doc)
        
    def last_page(self,canvas,doc):
        self.set_common_per_page(canvas,doc)

    #PDF作成
    def make_pdf_content(self,response,feed):
        HEADER_BACKGROUND_COLOR = colors.HexColor('#48ACC6')
        EVEN_BACKGROUND_COLOR = colors.HexColor('#DAEEF3')
        ODD_BACKGROUND_COLOR = colors.white

        #style変更
        styles = getSampleStyleSheet()
        for name in ('Normal','BodyText','Title','Heading1','Heading2','Heading3','Heading4','Heading5','Heading6','Bullet','Definition','Code'):
            styles[name].wordWrap = 'CJK'
            styles[name].fontName = 'meiryo'
            
        #doc作成
        doc = SimpleDocTemplate(response,pagesize=portrait(A4))

        story=[]

        #Title
        string ='<b>Title:</b> %s' % (feed.title)
        story.append(Paragraph(string,styles['Normal']))

        #Author
        if feed.administrative_code is None:
            administrative_code = '-'
        else:
            administrative_code = feed.administrative_code
        if feed.country_code is None:
            country_code = '-'
        else:
            country_code = feed.country_code

        string = '%s (%s - %s, %s)' % (feed.user.get_screen_name(),feed.user.get_sector_display(),administrative_code,country_code)
        txt ='<b>Author:</b> %s' % (string)
        story.append(Paragraph(txt,styles['Normal']))

        #Produced Time
        string = str(self.stix_package.timestamp)
        txt ='<b>Produced Time:</b> %s' % (string)
        story.append(Paragraph(txt,styles['Normal']))
        
        #STIX Package ID
        string = str(self.stix_package.id_)
        txt ='<b>STIX Package ID:</b> %s' % (string)
        story.append(Paragraph(txt,styles['Normal']))

        #空行
        story.append(Spacer(1,1.0*cm))
        
        #content
        txt ='<b>Content:</b>'
        story.append(Paragraph(txt,styles['Normal']))
        #txt = feed.post.value.encode('utf-8')
        txt = feed.post.encode('utf-8')
        story.append(Paragraph(txt,styles['Normal']))

        #空行
        story.append(Spacer(1,1.0*cm))

        #STIXからObservablesとIndicatorsを抽出
        indicators = FeedStix.get_indicators(self.stix_package)
        if len(indicators) == 0:
            txt ='<b>Indicators: </b>None'
            story.append(Paragraph(txt,styles['Normal']))
        else:
            txt ='<b>Indicators:</b>'
            story.append(Paragraph(txt,styles['Normal']))
            #空行
            story.append(Spacer(1,0.1*cm))
            #Table
            d = [
                    #header
                    ['Type','Indicators'],
                ]

            #STIXからObservablesとIndicatorsを抽出
            for item in indicators:
                (type_,value) = item
                item = []
                item.append(type_)
                #file_nameの場合は値がパイプで囲まれている
                if type_ == 'file_name':
                    #前後のパイプをトリミング
                    value = value[1:-1]
                item.append(value)
                d.append(item)

            #この幅くらいがちょうどよい
            table = Table(d,colWidths=(20*mm,135*mm),rowHeights=6*mm)
            table.setStyle(TableStyle([
                #背景色
                #先頭行(ヘッダ)
                #2ECCFA
                ('BACKGROUND',(0,0),(-1,0),HEADER_BACKGROUND_COLOR),
                # 表で使うフォントとそのサイズを設定
                ('FONT', (0, 0), (-1, -1), self.FONT_MEIRYO, 9),
                #先頭行だけbold
                ('FONT', (0, 0), (-1, 0), self.FONT_MEIRYO_BOLD, 9),
                #先頭行は白
                ('TEXTCOLOR',(0, 0),(-1,0 ),colors.white),
                #罫線
                ('BOX', (0, 0), (-1, -1), 0.10, HEADER_BACKGROUND_COLOR),
                ('INNERGRID', (0, 0), (-1, -1), 0.10, HEADER_BACKGROUND_COLOR),
                # セルの縦文字位置を、TOPにする
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ]))

            #stripe
            for i in range(len(indicators)):
                if (i % 2) == 0:
                    table.setStyle(TableStyle([
                        ('BACKGROUND',(0,i+1),(-1,i+1),EVEN_BACKGROUND_COLOR),
                        ('TEXTCOLOR',(0,i+1),(-1,i+1),colors.black),
                    ]))
                else:
                    table.setStyle(TableStyle([
                        ('BACKGROUND',(0,i+1),(-1,i+1),ODD_BACKGROUND_COLOR),
                        ('TEXTCOLOR',(0,i+1),(-1,i+1),colors.black),
                    ]))
            story.append(table)
        
        #改ページ
        story.append(PageBreak())
        
        #PDF 作成
        doc.build(story,onFirstPage=self.first_page,onLaterPages=self.last_page)
        
