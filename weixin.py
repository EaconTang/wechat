# coding:utf-8
import time
import xml.etree.ElementTree as ET

from flask import Flask, request

from utils import *

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
            ret_content = 'ERROR: Unsupprt message type! It should be text.'
        else:
            content = xml.find('Content').text
            if content in ('help', u'帮助', u'说明'):
                ret_content = """
                输入"笑话", "joke"试试看吧?
                """.strip()
            elif content in (u'笑话',):
                ret_content = get_joke()
            elif content in ('joke',):
                ret_content = get_dark_humor_joke()
            else:
                # just reverse
                ret_content = reverse(content)

        return reply_text(to_user_name=from_user_name,
                          from_user_name=to_user_name,
                          create_time=int(time.time()),
                          msg_type='text',
                          content=ret_content)


if __name__ == "__main__":
    app.run(port=5001)
