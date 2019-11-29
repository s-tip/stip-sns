# -*- coding: utf-8 -*-
import smtpd
import asyncore
import email
import base64
from stip.common.const import SHARING_RANGE_TYPE_KEY_ALL

'''
import threading
#smtp起動
#mail server thread 起動
def start_mail_thread():
    SMTP_ADDRESS = '0.0.0.0'
    SMTP_ACCEPT_MAIL_ADDRESS = sns_config.get('smtp','accept_mail_address')
    SMTP_PORT = int(sns_config.get('smtp','port'))
    SMTP_PORT = 25

    th = threading.Thread(target=start_mail_server,name="th",args=(SMTP_ADDRESS,SMTP_PORT))
    th.setDaemon(True)
    th.start()
'''

#mail server開始
def start_mail_server(address,port):
    try:
        __server = StipSMTPServer((address,port),None)
        asyncore.loop()
    except:
        #import traceback
        #traceback.print_exc()
        pass

class StipSMTPServer(smtpd.SMTPServer):
    #リクエストを受け付けた後の処理
    def process_message(self,peer,mailfrom,rcptos,data):
        #ACCEPT_MAIL_ADDRESS 以外は受け付けない
        from ctirs.models import SNSConfig
        smtp_accept_mail_address = SNSConfig.get_smtp_accept_mail_address()
        if smtp_accept_mail_address not in rcptos:
            print('Receiver Mail address is not permitted. ' + str(rcptos))
            return

        #mailfrom
        from django.contrib.auth.models import User
        users = User.objects.filter(email__exact=mailfrom)
        for user in users:
            #user ごとに投稿処理
            self.post(user,data)
        return

    #userごとにデータからpost処理を行う
    def post(self,user,data):
        try:
            #msg分解
            msg = email.message_from_string(data)

            #Subject取得
            try:
                #content-type指定でdecode
                (subject_str,subject_type) = email.Header.decode_header(msg['Subject'])[0]
                subject = subject_str.decode(subject_type)
            except:
                #存在しない場合はそのまま使用
                subject = msg['Subject']

            from ctirs.models import Feed
            #Feed作成
            feed = Feed()
            #Title は Subject
            feed.title = subject
            #TLP は UserのデフォルトTLP
            feed.tlp = user.tlp
            #Use
            feed.user = user

            #本文/Attachement取得
            attachements = []
            payloads = msg.get_payload()
            #添付がある場合は list, ない場合はstr
            if isinstance(payloads,str) == True:
                content_type = self.get_char_set_from_content_type(msg['Content-Type'])
                content_type = content_type.split(':')[0]
                if content_type is not None:
                    body = payloads.decode(content_type)
                else:
                    body = payloads
            elif isinstance(payloads,list) == True:
                #bodyは payloads[0]
                body_payload = payloads[0]
                body = self.get_unicode_content(body_payload)
                #それ以降はattachement
                for index in range(1,len(payloads)):
                    payload = payloads[index]
                    attachements.append(payload)
                
            #Sharing Rangeはall
            feed.sharing_range_type = SHARING_RANGE_TYPE_KEY_ALL
            #一旦Feedを保存しSTIXを作成する
            feed.save()
            
            #添付ファイル処理
            from feeds.views import save_post,save_attach_file
            for payload in attachements:
                file_name = self.get_file_name(payload)
                content = self.get_content(payload)
                #content を file stream にする
                import io
                o = io.BytesIO(content)
                attach_file = save_attach_file(file_name,o,feed.id)
                feed.files.add(attach_file)
            feed.save()

            #POSTする
            save_post(None,feed,body)
        
        except:
            import traceback
            traceback.print_exc()
        return

    #payload の内容が base64 でencode されているか?
    def is_encode_base64(self,payload):
        return payload.get('Content-Transfer-Encoding') == 'base64'
        
    #payloadの中身をbase64でencodeされていたらdecode
    #strで返却
    def get_content(self,payload):
        #中身を取得
        p = payload.get_payload()
        #base64でencodeされていたらdecode
        if self.is_encode_base64(payload) == True:
            content = base64.b64decode(p)
        else:
            content = p
        return content
    
    #payloadの中身をbase64でencodeされていたらdecode
    #unicodeで返却
    def get_unicode_content(self,payload):
        content = self.get_content(payload)
        char_set = self.get_char_set(payload)
        char_set = char_set.split(':')[0]
        if char_set is not None:
            content = content.decode(char_set)
        else:
            content = content.decode('utf-8')
        return content

    #添付のファイル名を取得
    def get_file_name(self,payload):
        for file_name,char_set in email.Header.decode_header(payload.get_filename()):
            #charset  指定なしならunicode変換,指定ありなら decodeする
            if char_set is not None:
                file_name = file_name.decode(char_set)
            else:
                file_name = str(file_name)
        return file_name

    #payload のchar_setを取得
    def get_char_set(self,payload):
        content_type = payload.get('Content-Type')
        return self.get_char_set_from_content_type(content_type)

    #conent_typeの値から char_set を取得
    #指定がない場合は None を返却
    def get_char_set_from_content_type(self,content_type):
        try:
            char_set = content_type.split('charset=')[1]
            return char_set
        except:
            None


