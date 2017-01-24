# coding:utf-8
import time
import os
import xml.etree.ElementTree as ET

from flask import Flask, request, render_template

from utils import *

BASE_DIR = os.path.join(os.path.dirname(__file__))
app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def wechat_auth():
    if request.method == 'GET':
        d = request.args
        return auth_weixin(token='nhd798xc58655bv878cv78dklkmn',
                           signature=d.get('signature'),
                           timestamp=d.get('timestamp'),
                           nonce=d.get('nonce'),
                           echostr=d.get('echostr'))

    if request.method == 'POST':
        # extract data
        xml_str = request.stream.read()
        xml = ET.fromstring(xml_str)
        to_user_name = xml.find('ToUserName').text
        from_user_name = xml.find('FromUserName').text
        create_time = xml.find('CreateTime').text
        msg_type = xml.find('MsgType').text
        msgId = xml.find('MsgId').text

        # only deal with text msg
        ret_content = ''
        if msg_type != 'text':
            ret_content = u'不好意思, 我只看得懂文字...'
        else:
            content = xml.find('Content').text
            for key_words, act in policy():
                if content in key_words:
                    if isinstance(act, unicode):
                        ret_content = act.encode('utf8')
                    elif callable(act):
                        ret_content = act()
                    else:
                        ret_content = str(act)
            if not ret_content:
                ret_content = get_tuling_reply(content)
                # if content in ('help', u'帮助', u'说明'):
                #     ret_content = """
                #     输入"笑话", "joke"试试看吧?
                #     """.strip()
                # elif content in (u'笑话',):
                #     ret_content = get_joke()
                # elif content in ('joke',):
                #     ret_content = get_dark_humor_joke()
                # else:
                #     # just reverse
                #     # ret_content = reverse(content)
                #     ret_content = get_tuling_reply(content)
        return reply_text(to_user_name=from_user_name,
                          from_user_name=to_user_name,
                          create_time=int(time.time()),
                          msg_type='text',
                          content=ret_content)


@app.route('/qrcode')
def get_qrcode():
    return app.send_static_file('qrcode.html')


if __name__ == "__main__":
    app.run(port=5001)
