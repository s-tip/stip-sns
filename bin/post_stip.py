#!/usr/bin/python3
# coding: UTF-8
import sys
import traceback
import argparse
import json
import requests

##############################
# post_stip
# S-TIP 投稿スクリプト
##############################
# 第1引数：URL (必須)
# 第2引数：POST 情報(必須)
# 第3引数：attachment file(任意)
##############################
# オプション
# url post_info_file [attachment_file,...]
##############################
'''
post_info_file例
(例1)
{
    "username": "satomi",
    "title": "test_title_from_script",
    "post" : "line1\nline2",
    "TLP": "GREEN",
    "publication" : "all"
}
・値と項目はダブルクオーテーションでくくる
・改行は\nで記載
・辞書の最後の項目の後ろにカンマを入れるとエラーなので要注意

(例2)
{
    "username": "satomi",
    "title": "test_title_from_script",
    "post" : "line1\nline2",
    "TLP": "GREEN",
    "publication" : "people",
    "people" : "1,2,3"
}
・With peopleに該当する項目は "publication" : "people"
・その場合、"people" には "uid"の数値文字列をリスト表示する(uidはauth.usersでselectしてください・・)

(例3)
{
    "username": "satomi",
    "title": "test_title_from_script",
    "post" : "line1\nline2",
    "TLP": "GREEN",
    "publication" : "group",
    "group" : "test_group"
}
・With a groupに該当する項目は "publication" : "group"
・その場合、"group" には任意の文字列を指定可能なので注意

'''


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Post S-TIP Script')
    parser.add_argument('-u', '--url', help='Post url')
    parser.add_argument('-p', '--post_info_file', help='Post setting information')
    parser.add_argument('attachments', nargs='*', help='attachement')
    args = parser.parse_args()

    if args.url is None:
        print('No URL.')
        parser.print_help()
        sys.exit(1)

    if args.post_info_file is None:
        print('No Post info file.')
        parser.print_help()
        sys.exit(1)

    with open(args.post_info_file, 'r', encoding='utf-8') as fp:
        payload = json.load(fp)

    index = 0
    files = {}
    for file_path in args.attachments:
        item_name = 'attachments_%d' % (index)
        index += 1
        files[item_name] = open(file_path, 'rb')

    r = requests.post(
        args.url,
        data=payload,
        files=files,
        verify=False)

    b = json.loads(r.text)
    if r.status_code != 200:
        print('Request Failed (%s, %s).' % (r.status_code, b['reason']))
    else:
        print('Success!')
